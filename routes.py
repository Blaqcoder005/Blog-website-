from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse
from config import supabase
from schema import PostCreate, PostUpdate
import datetime

router = APIRouter(tags=["routes"])

@router.post("/create")
def create_post(post: PostCreate):
    id = user[id]
    if not id:
        return RedirectResponse("/login")

    new_post = {"title": title, "content": content}

    supabase.table("content").insert(new_post).execute()

    return new_post.data

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

