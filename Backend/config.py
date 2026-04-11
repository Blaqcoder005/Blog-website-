from fastapi import Request, Depends, HTTPException, status
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
import os
from supabase import create_client, Client, ClientOptions
from datetime import datetime
import re
import secrets, hashlib
# load Onespot.env explicitly
load_dotenv(".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SERVICE_ROLE = os.getenv("SERVICE_ROLE")
SECRET_KEY = os.getenv("SECRET_KEY")

# quick sanity check
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# Create client with options object (v2+)
options = ClientOptions()  # adjust if you need headers or other options
supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE, options)

# export these for other modules to import
__all__ = ["supabase", "SERVICE_ROLE", "SECRET_KEY", "SUPABASE_URL", "SUPABASE_KEY"]



#...........Password hashing(salted SHA-256)..........
def hash_password(password: str):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt +password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, stored: str):
    try:
       salt, hashed = stored.split("$")
    except ValueError:
       return False
    return hashlib.sha256((salt +password).encode()).hexdigest() == hashed

#................endpoint_security................
def require_session_user(request: Request):
    if not request.session.get("user_id"):
        raise HTTPException(status_code=401)
    return {
        "id": request.session["user_id"],
        "role": request.session["role"],
        "email": request.session["email"],
        "agency_id": request.session.get("agency_id"),
        "username": request.session["username"],
    }

def require_role(allowed_roles: list[str]):
    def checker(user=Depends(require_session_user)):
        role = user.get("role")

        if not role or role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )

        return user

    return checker

def require_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401)
    return user

def generate_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug).strip('-')
    timestamp = hashlib.md5(datetime.utcnow().isoformat().encode()).hexdigest()[:6]
    return f"{slug}-{timestamp}"
