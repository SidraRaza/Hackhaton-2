# Hackathon Todo App

A full-stack multi-user web application with JWT authentication, responsive frontend, REST API, and Neon Serverless PostgreSQL storage.

## Features

- User registration and authentication with JWT tokens
- Create, read, update, and delete tasks
- Task completion status toggling
- User isolation - users can only access their own tasks
- Responsive design for mobile and desktop
- Modern UI with dark/light mode support
- TypeScript for type safety
- RESTful API design

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLModel
- **Database**: PostgreSQL (compatible with Neon Serverless)
- **Authentication**: JWT tokens with bcrypt password hashing

### Frontend
- **Framework**: Next.js 16+
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom dark/light mode
- **Authentication**: Better Auth integration
- **UI Components**: Custom-built with Tailwind CSS

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- PostgreSQL-compatible database (Neon Serverless recommended)

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

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/hackathon_todo
SECRET_KEY=your-super-secret-key-here
BETTER_AUTH_SECRET=your-better-auth-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days in minutes
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
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

## UI Enhancements

The frontend includes modern UI enhancements:
- Responsive design with mobile-first approach
- Dark/light mode with system preference detection
- Smooth transitions and animations
- Enhanced form validation with visual feedback
- Loading states and skeleton screens
- Accessible navigation with proper ARIA attributes
- Modern card-based design with subtle shadows

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

[MIT License](LICENSE)

## Contact

Project Link: [https://github.com/your-username/hackathon-todo-app](https://github.com/your-username/hackathon-todo-app)