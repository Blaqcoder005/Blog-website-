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
@router.get("/posts/{id}")
def get_post(id: int):
    response = supabase.table("posts").select("*").eq("id", id).execute()
    return response.data

@router.patch("/posts/{id}")
def update_post(id: int, post: PostUpdate):
    data = post.dict(exclude_unset=True)

    response = supabase.table("posts").update(data).eq("id", id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Post not found")

    return response.data[0]

