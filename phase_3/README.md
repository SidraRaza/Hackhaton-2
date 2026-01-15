# Hackathon II Todo App

A full-stack web application featuring task management with user authentication and JWT-based security.

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI with SQLModel ORM
- **Database**: PostgreSQL (Neon Serverless compatible)
- **Authentication**: JWT-based authentication
- **Deployment**: Docker-ready with docker-compose

## Features

- User registration and authentication
- Task CRUD operations (Create, Read, Update, Delete)
- Task filtering and sorting
- User data isolation (each user sees only their tasks)
- Responsive UI design
- JWT-based security

## Prerequisites

- Node.js 18+ with npm
- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL (local or cloud instance)

## Local Development Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd hackhathon-2/phase_2
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with environment variables
cp ../.env.example .env
# Edit .env with your database URL and JWT secret
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp ../.env.example .env.local
# Edit .env.local if needed
```

### 4. Run the Applications

#### Option A: Run Separately

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

#### Option B: Using Docker

```bash
# From the project root directory
docker-compose up --build
```

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
NEON_DATABASE_URL=your-neon-database-url-here  # Optional, for Neon PostgreSQL
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Or your backend URL
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get current user profile

### Tasks
- `GET /api/tasks/` - Get all user tasks
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

All task endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Project Structure

```
hackhathon-2/
├── backend/
│   ├── models/           # Database models (SQLModel)
│   ├── routes/           # API endpoints
│   ├── utils/            # Utilities (auth, etc.)
│   ├── config/           # Configuration
│   ├── database.py       # Database connection
│   └── main.py           # Main application
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages (App Router)
│   │   ├── components/   # Reusable components
│   │   ├── lib/          # Custom hooks and utilities
│   │   └── styles/       # Global styles
│   ├── public/
│   └── package.json
├── specs/                # Project specifications
├── docker-compose.yml    # Docker configuration
├── .env.example          # Environment variables template
└── README.md
```

## Docker Deployment

The application is configured for easy Docker deployment:

```bash
# Build and start all services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432 (PostgreSQL)

## Development Commands

### Backend
```bash
# Run development server
uvicorn main:app --reload --port 8000

# Run tests
pytest
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Security Features

- JWT-based authentication with expiration
- User data isolation (users can only access their own tasks)
- Password hashing with bcrypt
- Input validation on both frontend and backend
- Secure token storage in localStorage

## Troubleshooting

### Common Issues
1. **Port already in use**: Change ports in the commands above
2. **Database connection errors**: Verify DATABASE_URL is correct
3. **JWT Secret**: Ensure it's at least 32 characters long
4. **CORS errors**: Check backend CORS settings

### Reset Database
If you need to reset the database, you can recreate the tables by restarting the application or running the appropriate database commands.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and commit (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.