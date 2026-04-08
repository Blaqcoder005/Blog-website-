# Blog API - Production-Ready FastAPI Backend

A modular, asynchronous FastAPI backend for a blog website with JWT authentication.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Local Testing Guide](#local-testing-guide)
- [API Endpoints](#api-endpoints)
- [Endpoint Guide](#endpoint-guide)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Features

- **Asynchronous**: Full async/await support for high concurrency
- **JWT Authentication**: Secure OAuth2 implementation
- **Modular Architecture**: Clean separation of concerns
- **Pydantic Validation**: Strict input/output validation
- **Database**: SQLite (development) / PostgreSQL (production) with SQLAlchemy ORM
- **CORS Support**: Configurable CORS middleware
- **Password Security**: PBKDF2-SHA256 password hashing via Passlib

## Project Structure

```
.
├── config.py          # Environment configuration
├── database.py        # Database connection and session management
├── models.py          # SQLAlchemy models and Pydantic schemas
├── routes.py          # API endpoints
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
└── README.md
```

## Setup

### 1. Create Virtual Environment

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If execution policy blocks scripts, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Upgrade pip
python -m pip install --upgrade pip
```

**Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

**macOS/Linux:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` includes `email-validator`, which is required for Pydantic `EmailStr` validation on the auth models.

If you ever install packages manually or repair a broken environment, make sure it is present:

```bash
pip install email-validator
```

### 3. Configure Environment

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./blog.db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
PROJECT_NAME=Blog API
VERSION=1.0.0
API_V1_PREFIX=/api/v1

# CORS - comma-separated list
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Database
DATABASE_ECHO=false
```

### 4. Verify the Installation

Run a quick import check before starting the server:

```bash
python -c "import main; print(main.app.title)"
```

Expected output:

```text
Blog API
```

If this step passes, your dependencies, environment variables, and `email-validator` setup are all loading correctly.

### 5. Run the Application

```bash
uvicorn main:app --reload
```

The server will start at http://localhost:8000

### 6. Access API Documentation

Open your browser and navigate to: http://localhost:8000/docs

## Interactive Terminal Client

You can test the API manually from the terminal with the interactive client:

```bash
python interactive_api_client.py
```

By default it targets `http://127.0.0.1:8000`. To use a different server:

```bash
python interactive_api_client.py --base-url http://127.0.0.1:8001
```

### Example: Register a User

```text
api> POST /api/v1/auth/register
Body type [json/form/raw/none]: json
Paste JSON body. Type END on a new line to submit:
{
  "email": "reader@example.com",
  "username": "reader1",
  "password": "Password123!",
  "is_active": true,
  "is_admin": false
}
END
```

### Example: Login

```text
api> POST /api/v1/auth/token
Body type [json/form/raw/none]: form
Enter form fields as key=value. Type END on a new line to submit:
username=reader@example.com
password=Password123!
END
```

### Example: Store the Returned Token

After a successful login, load the `access_token` from the last response:

```text
api> use-token
```

You can also set a token manually:

```text
api> token YOUR_JWT_TOKEN_HERE
```

### Example: Send a Protected Request

Once a token is set, you can call protected endpoints directly:

```text
api> GET /api/v1/posts
```

To create a protected admin-only post:

```text
api> POST /api/v1/posts
Body type [json/form/raw/none]: json
Paste JSON body. Type END on a new line to submit:
{
  "title": "My First Terminal Post",
  "content": "Created from the interactive API client.",
  "is_published": true,
  "category_ids": [],
  "tag_ids": []
}
END
```

## Local Testing Guide

### Prerequisites

- Python 3.8+
- SQLite (included with Python) or PostgreSQL
- Virtual environment created and activated

### Testing with curl

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### 2. Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "securepassword123",
    "is_active": true,
    "is_admin": true
  }'
```

**Response (200 OK):**
```json
{
  "email": "admin@example.com",
  "username": "admin",
  "is_active": true,
  "is_admin": true,
  "id": 1,
  "created_at": "2024-01-15T10:30:00"
}
```

#### 3. Login and Get JWT Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=securepassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "email": "admin@example.com",
    "username": "admin",
    "is_active": true,
    "is_admin": true,
    "id": 1,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

#### 4. Create a New Post (Admin Only)

```bash
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "title": "Getting Started with FastAPI",
    "content": "FastAPI is a modern, fast web framework for building APIs with Python.",
    "is_published": true
  }'
```

**Response (200 OK):**
```json
{
  "title": "Getting Started with FastAPI",
  "content": "FastAPI is a modern, fast web framework for building APIs with Python.",
  "is_published": true,
  "id": 1,
  "author_id": 1,
  "slug": "getting-started-with-fastapi",
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T11:00:00"
}
```

#### 5. List All Published Posts

```bash
curl http://localhost:8000/api/v1/posts
```

**Response:**
```json
[
  {
    "title": "Getting Started with FastAPI",
    "content": "FastAPI is a modern, fast web framework for building APIs with Python.",
    "is_published": true,
    "id": 1,
    "author_id": 1,
    "slug": "getting-started-with-fastapi",
    "created_at": "2024-01-15T11:00:00",
    "updated_at": "2024-01-15T11:00:00"
  }
]
```

#### 6. Get a Specific Post

```bash
curl http://localhost:8000/api/v1/posts/1
```

**Response:**
```json
{
  "title": "Getting Started with FastAPI",
  "content": "FastAPI is a modern, fast web framework for building APIs with Python.",
  "is_published": true,
  "id": 1,
  "author_id": 1,
  "slug": "getting-started-with-fastapi",
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T11:00:00"
}
```

#### 7. Create a Comment

```bash
curl -X POST http://localhost:8000/api/v1/posts/1/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "content": "Great article! Very helpful.",
    "parent_comment_id": null
  }'
```

**Response (200 OK):**
```json
{
  "content": "Great article! Very helpful.",
  "post_id": 1,
  "parent_comment_id": null,
  "id": 1,
  "author_id": 1,
  "is_approved": false,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### 8. Update a Post (Admin Only)

```bash
curl -X PUT http://localhost:8000/api/v1/posts/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "title": "Getting Started with FastAPI - Updated",
    "content": "FastAPI is a modern, fast web framework for building APIs with Python. This post has been updated."
  }'
```

**Response:**
```json
{
  "title": "Getting Started with FastAPI - Updated",
  "content": "FastAPI is a modern, fast web framework for building APIs with Python. This post has been updated.",
  "is_published": true,
  "id": 1,
  "author_id": 1,
  "slug": "getting-started-with-fastapi",
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T12:30:00"
}
```

#### 9. Delete a Post (Admin Only)

```bash
curl -X DELETE http://localhost:8000/api/v1/posts/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Response:** (204 No Content)

## API Endpoints

### Public
- `GET /` - Root endpoint
- `GET /health` - Health check

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get JWT token

### Posts (Protected)
- `GET /api/v1/posts` - List published posts
- `GET /api/v1/posts/{post_id}` - Get post by ID
- `POST /api/v1/posts` - Create post (Admin only)
- `PUT /api/v1/posts/{post_id}` - Update post (Admin only)
- `DELETE /api/v1/posts/{post_id}` - Delete post (Admin only)

### Comments (Protected)
- `GET /api/v1/posts/{post_id}/comments` - List comments
- `POST /api/v1/posts/{post_id}/comments` - Create comment

## Endpoint Guide

### `GET /`
- **What**: Returns the API welcome message, current version, and docs path.
- **Why**: Useful as a quick sanity check that the app is running.
- **When**: Use it first when starting the server or verifying deployment.
- **Where**: Open it in the browser at `http://localhost:8000/` or call it from a frontend health check.
- **How to use**: Send a simple `GET` request with no body and no authentication.

### `GET /health`
- **What**: Returns a lightweight health payload: `{"status": "healthy"}`.
- **Why**: Designed for monitoring, uptime checks, and container readiness checks.
- **When**: Use it in deployment checks, reverse proxies, CI smoke tests, or load balancer probes.
- **Where**: Call it from monitoring tools or the terminal at `http://localhost:8000/health`.
- **How to use**: Send a simple `GET` request with no body and no authentication.

### `POST /api/v1/auth/register`
- **What**: Creates a new user account.
- **Why**: This is the onboarding endpoint for anyone who needs to access protected routes.
- **When**: Use it before login, usually once per new user.
- **Where**: Call it from a signup form, admin setup flow, or testing tool like `curl` or Postman.
- **How to use**: Send JSON with `email`, `username`, `password`, `is_active`, and `is_admin`. For normal users, `is_admin` should be `false`.

### `POST /api/v1/auth/token`
- **What**: Authenticates a user and returns a bearer token plus the user record.
- **Why**: Protected routes require this token in the `Authorization` header.
- **When**: Use it after registration or whenever a user signs in again.
- **Where**: Call it from your login form or terminal tests.
- **How to use**: Send `application/x-www-form-urlencoded` data with `username=<email>` and `password=<password>`, then reuse the returned `access_token` as `Bearer <token>`.

### `GET /api/v1/posts`
- **What**: Returns all published posts visible to authenticated users.
- **Why**: This is the main listing endpoint for blog feeds, dashboards, or readers.
- **When**: Use it when loading a homepage, posts page, or user dashboard.
- **Where**: Call it from the frontend post list screen after login.
- **How to use**: Send an authenticated `GET` request with `Authorization: Bearer <token>`.

### `GET /api/v1/posts/{post_id}`
- **What**: Returns one post by ID.
- **Why**: Lets the client fetch full details for a selected post.
- **When**: Use it when a user opens a post detail page or editor view.
- **Where**: Call it from routes like `/posts/1` in your frontend.
- **How to use**: Send an authenticated `GET` request and replace `{post_id}` with a real post ID.

### `POST /api/v1/posts`
- **What**: Creates a new blog post.
- **Why**: This is the write endpoint for publishing or drafting content.
- **When**: Use it from an admin-only post creation screen or seeded test flow.
- **Where**: Call it from an admin dashboard, CMS form, or terminal script.
- **How to use**: Send an authenticated admin request with JSON containing `title`, `content`, `is_published`, `category_ids`, and `tag_ids`.

### `PUT /api/v1/posts/{post_id}`
- **What**: Updates an existing post.
- **Why**: Allows admins to revise content, publishing state, categories, tags, and title.
- **When**: Use it when editing a post after creation.
- **Where**: Call it from an admin edit page or maintenance tool.
- **How to use**: Send an authenticated admin request to the target post ID with the fields you want to update as JSON.

### `DELETE /api/v1/posts/{post_id}`
- **What**: Deletes a post.
- **Why**: Removes unwanted or obsolete content from the system.
- **When**: Use it when an admin intentionally removes a post.
- **Where**: Call it from an admin moderation or content management interface.
- **How to use**: Send an authenticated admin `DELETE` request to the target post ID. A successful response returns `204 No Content`.

### `GET /api/v1/posts/{post_id}/comments`
- **What**: Returns approved comments for a specific post.
- **Why**: Lets readers or dashboards display discussion under a post.
- **When**: Use it when loading a post detail page with comments.
- **Where**: Call it after the post detail request in your frontend.
- **How to use**: Send an authenticated `GET` request and replace `{post_id}` with the target post ID.

### `POST /api/v1/posts/{post_id}/comments`
- **What**: Creates a new comment for a specific post.
- **Why**: Allows authenticated users to participate in discussion.
- **When**: Use it when a user submits a comment or reply.
- **Where**: Call it from a comment form under a post.
- **How to use**: Send an authenticated request with JSON containing `content` and optional `parent_comment_id`. Do not send `post_id` in the body because the URL already defines the post.

## Security

- Password hashing with PBKDF2-SHA256
- JWT token authentication
- Admin role-based access control
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Ensure the database file exists (for SQLite)
2. Verify database credentials in `.env`
3. Check that the database exists: `createdb blog_db`
4. Verify user permissions

### Virtual Environment Issues

If dependencies fail to install:

1. Ensure virtual environment is activated
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Try installing dependencies individually

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

Or change the port in the uvicorn command:

```bash
uvicorn main:app --reload --port 8001
```
