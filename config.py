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


