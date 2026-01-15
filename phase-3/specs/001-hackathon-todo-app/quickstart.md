# Quickstart: hackathon-todo

## Prerequisites
- Node.js 18+ for frontend development
- Python 3.9+ for backend development
- PostgreSQL-compatible database (Neon Serverless recommended)
- Git for version control

## Setup Instructions

### 1. Clone and Initialize
```bash
git clone <repository-url>
cd hackathon-todo
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Configuration
Create `.env` files in both backend and frontend directories:

**Backend (.env):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/hackathon_todo
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days in minutes
BETTER_AUTH_SECRET=your-better-auth-secret
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Database Setup
```bash
# From backend directory
alembic upgrade head
```

### 6. Running the Application

**Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## API Endpoints
- Backend API: http://localhost:8000/api
- Frontend: http://localhost:3000

## Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment
The application is designed for deployment to platforms that support both Next.js static exports and Python/ASGI applications. Consider using Vercel for frontend and Railway/Deta/Render for backend.