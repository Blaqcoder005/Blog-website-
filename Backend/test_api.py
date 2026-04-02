import asyncio
import os
import unittest
from pathlib import Path

from fastapi import HTTPException

TEST_DB_PATH = Path("test_blog_api.db")

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_blog_api.db"
os.environ["DATABASE_ECHO"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["PROJECT_NAME"] = "Blog API Test"
os.environ["VERSION"] = "1.0.0"
os.environ["API_V1_PREFIX"] = "/api/v1"
os.environ["ALLOWED_ORIGINS"] = '["http://testserver"]'

from database import async_session_factory, engine
from models import Base, Category, CommentCreate, PostCreate, Tag, UserCreate
from routes import create_comment, create_post, create_user


async def reset_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def seed_taxonomy():
    async with async_session_factory() as session:
        category = Category(name="Backend", slug="backend", description="Backend posts")
        tag = Tag(name="FastAPI", slug="fastapi")
        session.add_all([category, tag])
        await session.commit()
        await session.refresh(category)
        await session.refresh(tag)
        return category.id, tag.id


class BlogApiTests(unittest.TestCase):
    def setUp(self):
        asyncio.run(reset_database())

    @classmethod
    def tearDownClass(cls):
        asyncio.run(engine.dispose())
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

    def create_user_record(self, *, email: str, username: str, is_admin: bool):
        async def _create_user_record():
            async with async_session_factory() as session:
                return await create_user(
                    session,
                    UserCreate(
                        email=email,
                        username=username,
                        password="Password123!",
                        is_active=True,
                        is_admin=is_admin,
                    ),
                )

        return asyncio.run(_create_user_record())

    def create_post_record(self, *, user, title: str, content: str, category_ids=None, tag_ids=None):
        async def _create_post_record():
            async with async_session_factory() as session:
                return await create_post(
                    PostCreate(
                        title=title,
                        content=content,
                        is_published=True,
                        category_ids=category_ids or [],
                        tag_ids=tag_ids or [],
                    ),
                    session,
                    user,
                )

        return asyncio.run(_create_post_record())

    def create_comment_record(self, *, user, post_id: int, content: str, parent_comment_id=None):
        async def _create_comment_record():
            async with async_session_factory() as session:
                return await create_comment(
                    post_id,
                    CommentCreate(
                        content=content,
                        parent_comment_id=parent_comment_id,
                    ),
                    session,
                    user,
                )

        return asyncio.run(_create_comment_record())

    def test_create_user_preserves_admin_flag(self):
        admin_user = self.create_user_record(
            email="admin@example.com",
            username="admin",
            is_admin=True,
        )
        normal_user = self.create_user_record(
            email="user@example.com",
            username="user",
            is_admin=False,
        )

        self.assertTrue(admin_user.is_admin)
        self.assertFalse(normal_user.is_admin)

    def test_create_post_persists_taxonomy_and_generates_unique_slug(self):
        category_id, tag_id = asyncio.run(seed_taxonomy())
        admin_user = self.create_user_record(
            email="admin@example.com",
            username="admin",
            is_admin=True,
        )

        first_post = self.create_post_record(
            user=admin_user,
            title="FastAPI Testing",
            content="First post body",
            category_ids=[category_id],
            tag_ids=[tag_id],
        )
        self.assertEqual(first_post.slug, "fastapi-testing")
        self.assertEqual(first_post.category_ids, [category_id])
        self.assertEqual(first_post.tag_ids, [tag_id])

        second_post = self.create_post_record(
            user=admin_user,
            title="FastAPI Testing",
            content="Second post body",
        )
        self.assertEqual(second_post.slug, "fastapi-testing-2")

    def test_comment_parent_must_belong_to_same_post(self):
        admin_user = self.create_user_record(
            email="admin@example.com",
            username="admin",
            is_admin=True,
        )
        normal_user = self.create_user_record(
            email="user@example.com",
            username="user",
            is_admin=False,
        )

        first_post = self.create_post_record(
            user=admin_user,
            title="First Post",
            content="First post body",
        )
        second_post = self.create_post_record(
            user=admin_user,
            title="Second Post",
            content="Second post body",
        )

        parent_comment = self.create_comment_record(
            user=normal_user,
            post_id=first_post.id,
            content="Parent comment",
        )
        self.assertEqual(parent_comment.post_id, first_post.id)

        async def _create_invalid_reply():
            async with async_session_factory() as session:
                await create_comment(
                    second_post.id,
                    CommentCreate(
                        content="Reply on wrong post",
                        parent_comment_id=parent_comment.id,
                    ),
                    session,
                    normal_user,
                )

        with self.assertRaises(HTTPException) as context:
            asyncio.run(_create_invalid_reply())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Parent comment must belong to the same post")


if __name__ == "__main__":
    unittest.main()
