# Quickstart Guide: AI-Powered Conversational Task Management

## Overview
This guide provides instructions for setting up and developing the AI-powered conversational task management feature. This feature adds a chat interface to the existing task management application, allowing users to create, update, list, and complete tasks using natural language.

## Prerequisites
- Python 3.9+ for backend development
- Node.js 18+ for frontend development
- OpenAI API key
- PostgreSQL database (Neon Serverless recommended)
- Better Auth configured
- Git for version control

## Environment Setup

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Additional dependencies for this feature:
   ```bash
   pip install openai
   pip install pydantic-settings
   pip install python-multipart
   ```

3. Set up environment variables:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit the .env file to include your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Run database migrations:
   ```bash
   python -m alembic upgrade head
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

   Additional dependencies for this feature:
   ```bash
   npm install @openai/assistant-ui-react @openai/assistant-runtime
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Key Architecture Components

### 1. MCP Server (Model Context Protocol)
Located in: `backend/app/mcp_server.py`

The MCP server implements the Model Context Protocol and exposes task management tools as functions that the AI agent can call. The tools include:
- `create_task`: Creates a new task
- `update_task`: Updates an existing task
- `delete_task`: Deletes a task
- `get_tasks`: Retrieves user's tasks
- `complete_task`: Marks a task as completed

### 2. AI Service
Located in: `backend/app/ai_service.py`

The AI service handles communication with OpenAI's API, manages conversation threads, and processes tool calls from the AI assistant.

### 3. Chat API Endpoint
Located in: `backend/app/api/chat.py`

The chat endpoint serves as the main interface between the frontend and the AI service. It handles:
- Authentication validation
- Conversation loading and saving
- Request/response processing
- Error handling

### 4. Database Models
Located in: `backend/app/models/`

New models added for this feature:
- `Conversation`: Stores conversation metadata
- `Message`: Stores individual messages within conversations

### 5. Frontend Chat Component
Located in: `frontend/src/components/ChatInterface.jsx`

The chat component provides the UI for the conversational interface using OpenAI's assistant components.

## Development Workflow

### Adding New MCP Tools
1. Define the tool function in `backend/app/mcp_tools.py`
2. Add proper authentication checks to ensure users can only access their own data
3. Write unit tests for the new tool
4. Register the tool with the MCP server

### Modifying AI Behavior
1. Update the system prompt in `backend/app/ai_service.py`
2. Adjust the available tools in the assistant configuration
3. Test with various user inputs to ensure proper behavior

### Updating Frontend Chat UI
1. Modify `frontend/src/components/ChatInterface.jsx`
2. Ensure responsive design is maintained
3. Test across different device sizes
4. Verify accessibility compliance

## Testing

### Backend Tests
Run backend tests with:
```bash
cd backend
pytest tests/
```

Key test areas:
- MCP tools functionality and authentication
- AI service integration
- Chat API endpoints
- Database operations

### Frontend Tests
Run frontend tests with:
```bash
cd frontend
npm run test
```

## Troubleshooting

### Common Issues
1. **OpenAI API Connection**: Verify your API key is correctly set in environment variables
2. **Authentication Failures**: Ensure JWT tokens are properly passed in requests
3. **Database Connection**: Check database URL and credentials in your .env file
4. **MCP Tools Not Responding**: Verify the MCP server is properly registered with the AI service

### Debugging Tips
- Enable detailed logging in the AI service for debugging AI interactions
- Use the database admin panel to inspect conversation and message data
- Check the browser developer tools for frontend errors
- Monitor the backend server logs for API request details

## Deployment Notes
- Ensure the OpenAI API key is properly configured in production
- Set up proper CORS policies for production domains
- Configure SSL certificates for secure connections
- Set up monitoring for AI API usage and costs