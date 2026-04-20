from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config import SECRET_KEY
from routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://news-trends-exnw.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600, #this cache preflight for 1 hour
)
app.add_middleware(
    SessionMiddleware,
    same_site="none",
    secret_key= SECRET_KEY,  # must be secure
    https_only=True,
)

app.include_router(router)


@app.options("/{full_path:path}")
async def options_handler(request: Request):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "https://news-trends-exnw.onrender.com",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@app.get("/ping")
def ping():
    return {"status": "ok"}


