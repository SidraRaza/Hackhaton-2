# Quickstart Guide: Todo CRUD Functionality

## Development Setup

### Prerequisites
- Node.js 18+ for frontend development
- Python 3.9+ for backend development
- PostgreSQL or Neon database instance
- Docker (optional, for containerized setup)

### Environment Configuration
1. Copy `.env.example` to `.env` in both frontend and backend directories
2. Configure database connection strings
3. Set JWT secret for authentication
4. Configure Better Auth settings

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python migrations.py  # Run database migrations
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Todo Management
- `GET /api/todos` - Retrieve all todos for authenticated user
- `POST /api/todos` - Create a new todo
- `PUT /api/todos/{id}` - Update an existing todo
- `DELETE /api/todos/{id}` - Delete a todo

### Authentication
All endpoints require JWT authentication in the format:
```
Authorization: Bearer <jwt_token>
```

## Frontend Components

### Todo Form
Located in `frontend/src/components/TodoForm.tsx`
- Handles creation and updating of todos
- Validates input before submission
- Shows loading states during API operations

### Todo List
Located in `frontend/src/components/TodoList.tsx`
- Displays todos with proper authentication context
- Handles real-time updates after CRUD operations
- Provides filtering and sorting capabilities

### Task Card
Located in `frontend/src/components/TaskCard.tsx`
- Individual todo representation
- Provides inline editing capability
- Handles completion toggling and deletion

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests
```bash
cd backend
python tests/e2e_chat.py
```

## Troubleshooting

### Common Issues
1. **API endpoints not found**: Verify backend is running on port 8000
2. **Authentication failures**: Check JWT token validity and format
3. **Database connection errors**: Verify database connection strings
4. **Frontend-backend communication**: Ensure API endpoint consistency

### Debugging Steps
1. Check browser developer tools for API errors
2. Verify backend logs for detailed error messages
3. Confirm authentication token is properly set
4. Ensure database migrations are applied