<<<<<<< HEAD
from dotenv import load_dotenv
import os
from supabase import create_client, Client, ClientOptions

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


=======
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    PROJECT_NAME: str = "Blog API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: List[str]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
>>>>>>> 3c24d33 (initial commit)
