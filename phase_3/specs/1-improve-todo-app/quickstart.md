# Quickstart Guide: Improve Todo Application

## Prerequisites
- Node.js 18+ installed
- Python 3.11+ installed
- PostgreSQL database (local or cloud)
- Git

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <repository-name>
git checkout 1-improve-todo-app
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database connection and auth secret

# Run database migrations
python migrations.py

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your backend API URL

# Start the development server
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend docs: http://localhost:8000/docs

## Key Features

### Todo Management
- Add, edit, delete, and mark todos as completed
- Visual distinction between completed and pending todos
- Loading and error handling for all operations

### Authentication
- Login and registration accessible from navbar
- Secure JWT-based session management
- Protected routes for authenticated users

### Chatbot Integration
- Collapsible sidebar with AI chatbot
- Natural language processing for todo management
- Conversation history and context

### UI/UX Enhancements
- Premium, modern color palette
- Responsive design for all screen sizes
- Light/dark theme toggle
- Smooth transitions and visual feedback

## Development Commands

### Frontend
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

### Backend
```bash
# Run development server
uvicorn main:app --reload

# Run tests
pytest

# Format code
black .

# Check types
mypy .
```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/dbname
BETTER_AUTH_SECRET=your-secret-key
```