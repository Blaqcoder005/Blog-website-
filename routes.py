from fastapi import APIRouter, Form, UploadFile, Depends
from fastapi.responses import RedirectResponse
from config import supabase 
import datetime

router = APIRouter(tags=["routes"])

@router.post("/create")
async def create_post(title: str = Form, content: str = Form):
    id = user[id]
    if not id:
        return RedirectResponse("/login")
    new_post = {"content_id": title, "content": content}
    supabase.table(content).insert(new_post).execute()
    return {"message":"Published"}

@router.get("/view")
async def view_post():
    id = user[id]
    content = supabase.table("content").select("*").eq("content_id", title).execute()
    return {"content":content}

