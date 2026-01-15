# Hackathon Todo App

A full-stack todo application with authentication, built with Next.js, FastAPI, and SQLModel.

## Features

- User authentication and registration
- Create, read, update, and delete tasks
- Task completion toggling
- User isolation (users can only see their own tasks)
- Responsive design for mobile and desktop
- JWT-based authentication

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLModel
- **Database**: PostgreSQL (compatible with Neon Serverless)
- **Authentication**: JWT tokens with bcrypt password hashing

### Frontend
- **Framework**: Next.js 16+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth integration

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Tasks
- `GET /api/tasks` - Get all tasks for authenticated user
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{id}` - Get a specific task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion status

## Environment Variables

### Backend
- `DATABASE_URL` - PostgreSQL database URL
- `SECRET_KEY` - Secret key for JWT tokens
- `BETTER_AUTH_SECRET` - Secret for Better Auth

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

## Deployment

The application is designed for deployment to platforms that support both Next.js static exports and Python/ASGI applications. Consider using Vercel for frontend and Railway/Deta/Render for backend.