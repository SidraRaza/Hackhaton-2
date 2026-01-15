# Quickstart Guide - Hackathon II Todo App

## Overview
This guide provides a quick setup and run process for the Hackathon II Todo App. Follow these steps to get the full-stack application running locally.

## Prerequisites
- Node.js 18+ with npm
- Python 3.9+
- PostgreSQL (local or cloud instance)
- Git

## Local Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackhathon-2/phase_2
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your database URL and JWT secret
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local file with your backend API URL
```

### 4. Database Setup
```bash
# In backend directory with virtual environment activated
# The application will create tables automatically on startup
```

## Running the Application

### Development Mode
```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Documentation: http://localhost:8000/docs

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
NEON_DATABASE_URL=your_neon_postgres_connection_string
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get current user

### Tasks
- `GET /api/tasks/` - Get all user tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## Sample Usage

### Register a New User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Create a Task
```bash
# After getting JWT token from login
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the todo app implementation",
    "priority": "high"
  }'
```

## Testing the Application

### Backend Tests
```bash
# In backend directory
pytest
```

### Frontend Tests
```bash
# In frontend directory
npm run test
```

## Troubleshooting

### Common Issues
1. **Port already in use**: Change ports in the commands above
2. **Database connection**: Verify DATABASE_URL is correct
3. **JWT Secret**: Ensure it's at least 32 characters
4. **CORS errors**: Check backend CORS settings

### Resetting the Database
```bash
# This will recreate all tables (destroys all data)
# In backend directory:
python reset_db.py  # if available
```

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
```

### Run Production Server
```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Next Steps
1. Explore the API documentation at http://localhost:8000/docs
2. Customize the UI components in the frontend/src/components directory
3. Add new features by following the spec-driven development workflow
4. Refer to the full specifications in the specs/ directory for detailed implementation guides