from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config import SECRET_KEY
from routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600, #this cache preflight for 1 hour
)
app.add_middleware(
    SessionMiddleware,
    same_site="lax",
    secret_key= SECRET_KEY,  # must be secure
    https_only=False,
)

app.include_router(router)
