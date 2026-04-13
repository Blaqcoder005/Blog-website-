from fastapi import APIRouter, Form, Request, UploadFile, File, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from config import supabase, hash_password, verify_password, generate_slug
from schema import PostCreate, PostUpdate
import datetime, uuid, os

router = APIRouter(tags=["routes"])

@router.get("/me")
def auth_me(request: Request):
    user = request.session.get("user_id")
    if not user:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "user_id": user
    }

@router.post("/register")
async def register(request: Request):
    form = await request.form()
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    print(email, password)
    if not email or not password:
        return HTMLResponse("Missing fields", status_code=400)

    email = email.strip().lower()

    # Check if email exists
    existing = supabase.table("users") \
        .select("id") \
        .eq("email", email) \
        .eq("username", username) \
        .execute()

    if existing.data:
        return HTMLResponse("Email already exists", status_code=400)

    # Check if username exists
    if username:
        existing_username = supabase.table("users") \
            .select("id") \
            .eq("username", username) \
            .execute()

        if existing_username.data:
            return HTMLResponse("Username already taken", status_code=400)

    # Hash password
    pw_hash = hash_password(password)

    # Create user FIRST 
    user_data = {
        "email": email,
        "password_hash": pw_hash,
    }
    if username:
        user_data["username"] = username

    new_user = supabase.table("users").insert(user_data).execute()
    user_id = new_user.data[0]["id"]  # ← capture the ID

    return { "success": True }

@router.post("/login")
async def login(request: Request):
    form = await request.form()

    email = form.get("email")
    password = form.get("password")

    if not email or not password:
        return HTMLResponse("Missing fields", status_code=400)

    email = email.strip().lower()

    res = (
        supabase
        .table("users")
        .select("id, email, username, password_hash")
        .eq("email", email)
        .execute()
    )

    print("DEBUG RES:", res.data)

    if not res.data:
        return HTMLResponse("User not found", status_code=404)

    user = res.data[0]

    if not verify_password(password, user["password_hash"]):
        return HTMLResponse("Invalid credentials", status_code=401)

    request.session["user_id"] = user["id"]
    request.session["email"] = user["email"]
    request.session["username"] = user.get("username")

    return {
        "success": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"]
        }
    }

@router.post("/create")
async def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login")

    image_url = None

    if image and image.filename:
        file_bytes = await image.read()
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        supabase.storage.from_("blog-images").upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": image.content_type, "upsert": "false"}
        )

        image_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/blog-images/{filename}"

    new_post = {
        "title": title,
        "content": content,
        "slug": generate_slug(title),
        "image_url": image_url
    }

    response = supabase.table("posts").insert(new_post).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create post")

    return response.data[0]

# GET all posts
@router.get("/posts")
def get_posts():
    response = supabase.table("posts").select("*").execute()
    return response.data

# GET single post
@router.get("/posts/{slug}")
def get_post(slug: str):
    response = supabase.table("posts") \
        .select("*") \
        .eq("slug", slug) \
        .execute()

    if not response.data:
        return {"error": "Post not found"}

    return response.data[0]

@router.patch("/posts/{title}")
def update_post(title: str, post: PostUpdate):
    data = post.dict(exclude_unset=True)

    response = supabase.table("posts").update(data).eq("title", title).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Post not found")

    return response.data[0]

@router.post("/comment")
async def add_comment(request: Request):
    form = await request.form()
    post_id = form.get("slug")
    comment_text = form.get("comment")

    session = request.session
    if "user_id" not in session:
        return RedirectResponse("/login")

    user_id = session["user_id"]

    comment = {
        "user_id": user_id,
        "slug": post_id,
        "content": comment_text
    }

    response = supabase.table("comments").insert(comment).execute()
    return response.data

@router.get("/comments/{slug}")
def get_comments(slug: str):
    response = supabase.table("comments").select("*").eq("slug", slug).execute()

    if not response.data:
        return {"error": "No comments found"}

    return response.data
