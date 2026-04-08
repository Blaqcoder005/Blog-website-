import re
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import settings
from database import get_db
from models import (
    Category,
    Comment,
    CommentCreate,
    CommentRead,
    Post,
    PostCreate,
    PostRead,
    PostUpdate,
    Tag,
    Token,
    User,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["blog"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:255] or "post"


async def generate_unique_slug(
    db: AsyncSession, title: str, *, exclude_post_id: int | None = None
) -> str:
    base_slug = slugify(title)
    slug = base_slug
    counter = 2

    while True:
        query = select(Post).where(Post.slug == slug)
        if exclude_post_id is not None:
            query = query.where(Post.id != exclude_post_id)

        existing_post = (await db.execute(query)).scalar_one_or_none()
        if existing_post is None:
            return slug

        suffix = f"-{counter}"
        slug = f"{base_slug[:255 - len(suffix)]}{suffix}"
        counter += 1


async def fetch_categories_by_ids(db: AsyncSession, category_ids: List[int]) -> List[Category]:
    if not category_ids:
        return []

    result = await db.execute(select(Category).where(Category.id.in_(category_ids)))
    categories = result.scalars().all()
    categories_by_id = {category.id: category for category in categories}
    missing_ids = [category_id for category_id in category_ids if category_id not in categories_by_id]
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Categories not found: {missing_ids}")

    return [categories_by_id[category_id] for category_id in category_ids]


async def fetch_tags_by_ids(db: AsyncSession, tag_ids: List[int]) -> List[Tag]:
    if not tag_ids:
        return []

    result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
    tags = result.scalars().all()
    tags_by_id = {tag.id: tag for tag in tags}
    missing_ids = [tag_id for tag_id in tag_ids if tag_id not in tags_by_id]
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Tags not found: {missing_ids}")

    return [tags_by_id[tag_id] for tag_id in tag_ids]


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.categories),
            selectinload(Post.tags),
        )
        .where(Post.id == post_id)
    )
    return result.scalar_one_or_none()


async def get_comments_for_post(db: AsyncSession, post_id: int) -> List[Comment]:
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.post_id == post_id, Comment.is_approved == True)
    )
    return result.scalars().all()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_active=user.is_active,
        is_admin=user.is_admin,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user


@router.post("/auth/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email exists")
    return await create_user(db, user)


@router.post("/auth/token", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {"sub": user.email},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/posts", response_model=List[PostRead])
async def get_posts(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.categories),
            selectinload(Post.tags),
        )
        .where(Post.is_published == True)
    )
    return result.scalars().all()


@router.get("/posts/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts", response_model=PostRead)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_admin_user),
):
    categories = await fetch_categories_by_ids(db, post.category_ids)
    tags = await fetch_tags_by_ids(db, post.tag_ids)
    slug = await generate_unique_slug(db, post.title)

    db_post = Post(
        title=post.title,
        content=post.content,
        slug=slug,
        author_id=user.id,
        is_published=post.is_published,
        categories=categories,
        tags=tags,
    )

    db.add(db_post)
    await db.commit()
    return await get_post_by_id(db, db_post.id)


@router.put("/posts/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    post: PostUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_admin_user),
):
    db_post = await get_post_by_id(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = post.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"]:
        db_post.slug = await generate_unique_slug(db, update_data["title"], exclude_post_id=db_post.id)

    if "category_ids" in update_data:
        db_post.categories = await fetch_categories_by_ids(db, update_data.pop("category_ids"))

    if "tag_ids" in update_data:
        db_post.tags = await fetch_tags_by_ids(db, update_data.pop("tag_ids"))

    for key, value in update_data.items():
        setattr(db_post, key, value)

    await db.commit()
    return await get_post_by_id(db, db_post.id)


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_admin_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(db_post)
    await db.commit()
    return None


@router.get("/posts/{post_id}/comments", response_model=List[CommentRead])
async def get_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_comments_for_post(db, post_id)


@router.post("/posts/{post_id}/comments", response_model=CommentRead)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalar_one_or_none()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    if comment.parent_comment_id is not None:
        result = await db.execute(select(Comment).where(Comment.id == comment.parent_comment_id))
        parent_comment = result.scalar_one_or_none()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent_comment.post_id != post_id:
            raise HTTPException(status_code=400, detail="Parent comment must belong to the same post")

    db_comment = Comment(
        content=comment.content,
        author_id=user.id,
        post_id=post_id,
        parent_comment_id=comment.parent_comment_id,
    )

    db.add(db_comment)
    await db.commit()

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.id == db_comment.id)
    )
    return result.scalar_one()
