# Todo Application - Phase II (Full-Stack Multi-User Web App By Ahmed Raza)

**Version**: 2.0.0
**Phase**: Phase II - Multi-User Web Application
**Status**: Full-Stack Application with Authentication and Persistence

---

## Overview

Modern, full-stack todo application with user authentication, persistent storage, and responsive web interface. Users can create accounts, manage their personal task lists, and access their data from any device.

**Features**:
- User authentication (signup, signin, signout)
- Multi-user support with complete data isolation
- Task CRUD operations (create, read, update, delete)
- Mark tasks as complete/incomplete
- Responsive design (mobile to desktop)
- Persistent storage with PostgreSQL
- RESTful API with automatic documentation

**Technology Stack**:
- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI with SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT tokens with Better Auth
- **Architecture**: Clean separation with models, services, API routes

---

## Prerequisites

### Backend Requirements
- Python 3.13+
- UV package manager
- Neon PostgreSQL database (or local PostgreSQL)

### Frontend Requirements
- Node.js 18+
- npm or pnpm

---

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd path/to/todo-app/phase1
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and fill in:
# - DATABASE_URL (Neon PostgreSQL connection string)
# - BETTER_AUTH_SECRET (32+ character random string)
# - CORS_ORIGINS (http://localhost:3000)

# Initialize database
# Run the SQL script in backend/scripts/init_db.sql on your Neon database

# Start backend server
uvicorn src.main:app --reload --port 8000
```

Backend will start at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local and fill in:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - BETTER_AUTH_SECRET (same as backend)
# - BETTER_AUTH_URL=http://localhost:3000

# Start frontend server
npm run dev
```

Frontend will start at `http://localhost:3000`

---

## Usage

### 1. Create Account

1. Visit `http://localhost:3000`
2. Click "Sign Up"
3. Enter email and password (min 8 characters, must contain letter and number)
4. Click "Sign Up"

### 2. Sign In

1. Visit `http://localhost:3000`
2. Click "Sign In"
3. Enter your email and password
4. Click "Sign In"

### 3. Manage Tasks

**Create Task**:
- Click "+ Add Task" button
- Enter title (required, 1-200 characters)
- Enter description (optional, max 1000 characters)
- Click "Create Task"

**View Tasks**:
- All tasks displayed on main page
- Filter by: All, Active, Completed
- Tasks sorted by creation date (newest first)

**Update Task**:
- Click "Edit" on any task
- Modify title and/or description
- Click "Save"

**Mark Complete**:
- Click checkbox next to task
- Task will be marked as complete (strikethrough)
- Click again to mark incomplete

**Delete Task**:
- Click "Delete" on any task
- Confirm deletion
- Task permanently removed

### 4. Sign Out

- Click "Sign Out" button in header
- Redirected to home page

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### API Endpoints

**Authentication**:
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Authenticate and get JWT token
- `POST /api/auth/signout` - Sign out (client-side token removal)

**Tasks**:
- `GET /api/users/{user_id}/tasks` - List all tasks for user
- `POST /api/users/{user_id}/tasks` - Create new task
- `GET /api/users/{user_id}/tasks/{task_id}` - Get task details
- `PUT /api/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/users/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/users/{user_id}/tasks/{task_id}/complete` - Toggle completion

---

## Project Structure

```
phase1/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLModel entities (User, Task)
│   │   ├── services/        # Business logic (AuthService, TaskService)
│   │   ├── api/
│   │   │   ├── routes/      # API endpoints (auth, tasks)
│   │   │   ├── middleware/  # JWT auth, error handling
│   │   │   └── models/      # Request/response models
│   │   ├── db/              # Database connection
│   │   ├── config.py        # Configuration management
│   │   └── main.py          # FastAPI app entry point
│   ├── tests/               # Unit, integration, contract tests
│   ├── scripts/             # Database initialization scripts
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   │   ├── (auth)/      # Auth pages (signin, signup)
│   │   │   └── (dashboard)/ # Protected pages (tasks)
│   │   ├── components/
│   │   │   ├── auth/        # Auth forms
│   │   │   ├── tasks/       # Task components
│   │   │   └── ui/          # Reusable UI components
│   │   ├── lib/             # API client, auth, utilities
│   │   ├── types/           # TypeScript types
│   │   └── styles/          # Global styles
│   ├── tests/               # Component and integration tests
│   ├── package.json
│   └── README.md
├── specs/                   # Feature specifications
├── history/                 # Prompt history records
└── README.md                # This file
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m contract

# Run with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm test -- --coverage
```

---

## Deployment

### Backend Deployment

Deploy to platforms supporting Python:
- Vercel
- Railway
- Render
- DigitalOcean App Platform

**Environment Variables**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: JWT secret (32+ characters)
- `CORS_ORIGINS`: Frontend URL (e.g., https://yourdomain.com)

### Frontend Deployment

Deploy to Vercel (recommended for Next.js):

```bash
cd frontend
npm run build
```

**Environment Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `BETTER_AUTH_SECRET`: Same as backend
- `BETTER_AUTH_URL`: Frontend URL

---

## Troubleshooting

### Backend Issues

**Database Connection Error**:
- Verify `DATABASE_URL` in `.env` is correct
- Ensure Neon database is accessible
- Check connection string includes `sslmode=require`

**JWT Authentication Error**:
- Verify `BETTER_AUTH_SECRET` matches frontend
- Check token expiry (default 7 days)
- Ensure Authorization header format: `Bearer <token>`

### Frontend Issues

**API Connection Error**:
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check backend server is running
- Verify CORS is configured correctly

**Authentication Issues**:
- Clear browser localStorage and cookies
- Verify `BETTER_AUTH_SECRET` matches backend
- Check browser console for errors

---

## Security Notes

- Passwords are hashed with bcrypt (10+ rounds)
- JWT tokens expire after 7 days
- All API endpoints require authentication (except signup/signin)
- User data is completely isolated (users can only access their own tasks)
- HTML is escaped to prevent XSS attacks
- CORS is configured to allow only specified origins

---

## Phase Comparison

**Phase I** (Console App):
- In-memory storage
- Single user
- CLI interface
- No authentication
- Data lost on exit

**Phase II** (Web App):
- PostgreSQL persistence
- Multi-user support
- Web interface
- JWT authentication
- Data persists across sessions

---

## Next Steps (Future Phases)

**Phase III**: AI-Native Features
- Natural language task creation
- Smart task suggestions
- Conversational interface

**Phase IV**: Cloud-Native Deployment
- Kubernetes deployment
- Infrastructure as Code
- Observability and monitoring
- CI/CD pipelines

---

## License

Copyright (c) 2025 Evolution of Todo Project. All rights reserved.
