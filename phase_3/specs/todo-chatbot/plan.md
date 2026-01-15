# Implementation Plan: AI-Powered Todo Chatbot

## Overview
- **Source Spec:** D:/hackhathon-2/phase_3/specs/todo-chatbot/spec.md
- **Total Steps:** 18
- **Estimated Complexity:** High

## Dependencies
- Node.js runtime environment
- Database system (PostgreSQL/SQLite)
- OpenAI API access (or alternative LLM service)
- MCP server infrastructure

## Execution Order

### Phase 1: Backend Foundation

#### Step 1.1: Set up project structure and dependencies
- **Category:** Infrastructure
- **Dependencies:** None
- **Files:** package.json, src/server.js, .env, .gitignore
- **Acceptance Criteria:**
  - [ ] Project structure created with proper directories
  - [ ] Essential dependencies installed (express, cors, dotenv, etc.)
  - [ ] Environment configuration set up
  - [ ] Git ignore configured properly

**Claude Prompt:**
```
Create a new Node.js project for an AI-powered todo chatbot with the following requirements:

1. Initialize a package.json with these dependencies:
   - express: latest version
   - cors: latest version
   - dotenv: latest version
   - sqlite3: latest version
   - openai: latest version
   - nodemon: latest version (dev dependency)
   - jest: latest version (dev dependency)
   - supertest: latest version (dev dependency)

2. Create the basic project structure:
   - src/ (with server.js as entry point)
   - src/models/ (for database models)
   - src/routes/ (for API routes)
   - src/middleware/ (for middleware functions)
   - src/config/ (for configuration files)
   - src/utils/ (for utility functions)
   - tests/ (for test files)

3. Create a basic server.js file that:
   - Sets up Express app
   - Uses CORS middleware
   - Loads environment variables
   - Starts server on port 3000
   - Has basic error handling

4. Create a .env file with:
   - PORT=3000
   - DATABASE_URL=file:./db.sqlite
   - OPENAI_API_KEY=your_api_key_here

5. Create a .gitignore file that excludes:
   - node_modules/
   - .env
   - coverage/
   - .DS_Store
   - *.log

Make sure all files are properly structured and the server can start successfully.
```

---

#### Step 1.2: Set up database schema and migration
- **Category:** Backend
- **Dependencies:** Step 1.1
- **Files:** src/config/database.js, migrations/001_create_tables.sql
- **Acceptance Criteria:**
  - [ ] Database connection established
  - [ ] Users table created with id, email, name, created_at
  - [ ] Todos table created with id, user_id, title, description, completed, created_at
  - [ ] Chat_sessions table created with id, user_id, title, created_at
  - [ ] Chat_messages table created with id, session_id, role, content, timestamp

**Claude Prompt:**
```
Set up the database schema for the AI-powered todo chatbot with SQLite. Create the following files:

1. src/config/database.js:
   - Import sqlite3
   - Create database connection function
   - Export database instance
   - Include functions to run initial migrations

2. migrations/001_create_tables.sql:
   - CREATE TABLE users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       email TEXT UNIQUE NOT NULL,
       name TEXT NOT NULL,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP
     );

   - CREATE TABLE todos (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       title TEXT NOT NULL,
       description TEXT,
       completed BOOLEAN DEFAULT FALSE,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(id)
     );

   - CREATE TABLE chat_sessions (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       title TEXT NOT NULL,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(id)
     );

   - CREATE TABLE chat_messages (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       session_id INTEGER NOT NULL,
       role TEXT NOT NULL, -- 'user' or 'assistant'
       content TEXT NOT NULL,
       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
     );

3. Update src/server.js to initialize the database connection on startup.

Include proper error handling and logging for database operations.
```

---

#### Step 1.3: Implement user authentication model
- **Category:** Backend
- **Dependencies:** Step 1.2
- **Files:** src/models/User.js, src/middleware/auth.js
- **Acceptance Criteria:**
  - [ ] User model with create, findById, findByEmail methods
  - [ ] Password hashing implemented
  - [ ] JWT token generation and verification
  - [ ] Authentication middleware that validates tokens

**Claude Prompt:**
```
Implement user authentication functionality for the AI-powered todo chatbot:

1. Create src/models/User.js with:
   - Static methods: create(email, password, name), findById(id), findByEmail(email)
   - Instance method: validatePassword(plainPassword)
   - Password hashing using bcrypt or crypto
   - Database queries for user operations

2. Create src/middleware/auth.js with:
   - authenticateToken(req, res, next) function that verifies JWT
   - Proper error handling for invalid/missing tokens
   - Attaches user object to req.user when valid

3. Install bcrypt dependency if needed

4. Add JWT secret to .env file:
   - JWT_SECRET=your_jwt_secret_here

5. Update package.json to include bcrypt dependency

Include proper validation and error handling for all authentication operations.
```

---

#### Step 1.4: Create todo model with CRUD operations
- **Category:** Backend
- **Dependencies:** Step 1.3
- **Files:** src/models/Todo.js
- **Acceptance Criteria:**
  - [ ] Todo model with create, findById, update, delete methods
  - [ ] Methods to get all todos for a user
  - [ ] Toggle completion status functionality
  - [ ] Proper error handling for database operations

**Claude Prompt:**
```
Create the Todo model with full CRUD operations for the AI-powered todo chatbot:

1. Create src/models/Todo.js with:
   - Static methods:
     * create(userId, title, description) - creates new todo
     * findById(id) - gets specific todo
     * findByUserId(userId) - gets all todos for a user
     * update(id, updates) - updates todo properties
     * delete(id) - deletes a todo
     * toggleCompleted(id) - toggles completion status
   - Proper validation for inputs
   - Error handling for database operations
   - Return appropriate data structures

2. Include SQL queries for all operations
3. Handle edge cases like invalid user IDs, non-existent todos
4. Log important operations for debugging

Ensure all methods properly handle database transactions and return consistent data formats.
```

---

#### Step 1.5: Create chat session and message models
- **Category:** Backend
- **Dependencies:** Step 1.3
- **Files:** src/models/ChatSession.js, src/models/ChatMessage.js
- **Acceptance Criteria:**
  - [ ] ChatSession model with create, findById, findByUserId, updateTitle methods
  - [ ] ChatMessage model with create, findBySessionId methods
  - [ ] Proper relationships between sessions and messages
  - [ ] Methods to add messages to sessions

**Claude Prompt:**
```
Create the chat session and message models for the AI-powered todo chatbot:

1. Create src/models/ChatSession.js with:
   - Static methods:
     * create(userId, title) - creates new chat session
     * findById(id) - gets specific session
     * findByUserId(userId) - gets all sessions for a user
     * updateTitle(id, title) - updates session title
   - Proper validation and error handling
   - Database queries for all operations

2. Create src/models/ChatMessage.js with:
   - Static methods:
     * create(sessionId, role, content) - creates new message
     * findBySessionId(sessionId) - gets all messages for a session
   - Validation for role ('user' or 'assistant')
   - Proper error handling and database queries

3. Include foreign key constraints and relationship handling
4. Add timestamps to track message order
5. Return consistent data structures from all methods

Ensure proper database transaction handling and relationship integrity.
```

---

### Phase 2: API Endpoints

#### Step 2.1: Implement authentication API routes
- **Category:** Backend
- **Dependencies:** Step 1.3
- **Files:** src/routes/auth.js
- **Acceptance Criteria:**
  - [ ] POST /api/auth/register endpoint
  - [ ] POST /api/auth/login endpoint
  - [ ] GET /api/auth/me endpoint (protected)
  - [ ] Proper input validation and error responses

**Claude Prompt:**
```
Create authentication API routes for the AI-powered todo chatbot:

1. Create src/routes/auth.js with:
   - POST /register:
     * Validates email, password, name
     * Checks if user already exists
     * Creates new user with hashed password
     * Returns JWT token
     * Proper error handling for validation failures

   - POST /login:
     * Validates email and password
     * Verifies credentials against stored hash
     * Returns JWT token if valid
     * Proper error handling for invalid credentials

   - GET /me (protected route):
     * Requires valid JWT token
     * Returns user profile info (id, email, name)
     * Uses auth middleware

2. Include proper input validation:
   - Email format validation
   - Password strength requirements (min 8 chars)
   - Name length validation

3. Return appropriate HTTP status codes (200, 201, 400, 401, 409, 500)
4. Include proper error response formatting
5. Add rate limiting considerations in comments

Update server.js to include these routes under /api/auth path.
```

---

#### Step 2.2: Implement todo API routes
- **Category:** Backend
- **Dependencies:** Step 1.4, Step 2.1
- **Files:** src/routes/todos.js
- **Acceptance Criteria:**
  - [ ] GET /api/todos (protected) - gets user's todos
  - [ ] POST /api/todos (protected) - creates new todo
  - [ ] PUT /api/todos/:id (protected) - updates todo
  - [ ] DELETE /api/todos/:id (protected) - deletes todo
  - [ ] PATCH /api/todos/:id/toggle (protected) - toggles completion

**Claude Prompt:**
```
Create todo API routes for the AI-powered todo chatbot:

1. Create src/routes/todos.js with protected routes:
   - GET /:
     * Requires valid JWT token (use auth middleware)
     * Gets all todos for authenticated user
     * Returns todos with id, title, description, completed, created_at
     * Proper error handling for database issues

   - POST /:
     * Requires valid JWT token
     * Validates title (required), description (optional)
     * Creates new todo for authenticated user
     * Returns created todo with id and timestamps
     * Proper error handling for validation failures

   - PUT /:id:
     * Requires valid JWT token
     * Validates todo belongs to user
     * Updates title and/or description
     * Returns updated todo
     * Error handling for non-existent todos

   - DELETE /:id:
     * Requires valid JWT token
     * Validates todo belongs to user
     * Deletes specified todo
     * Returns success confirmation
     * Error handling for non-existent todos

   - PATCH /:id/toggle:
     * Requires valid JWT token
     * Validates todo belongs to user
     * Toggles completed status
     * Returns updated todo
     * Error handling for non-existent todos

2. Include proper input validation and sanitization
3. Return appropriate HTTP status codes
4. Include error handling for unauthorized access attempts
5. Add comments explaining security considerations

Update server.js to include these routes under /api/todos path with auth middleware.
```

---

#### Step 2.3: Implement chat API routes
- **Category:** Backend
- **Dependencies:** Step 1.5, Step 2.1
- **Files:** src/routes/chat.js
- **Acceptance Criteria:**
  - [ ] GET /api/chat/sessions (protected) - gets user's chat sessions
  - [ ] POST /api/chat/sessions (protected) - creates new session
  - [ ] GET /api/chat/sessions/:id/messages (protected) - gets session messages
  - [ ] POST /api/chat/sessions/:id/messages (protected) - adds message to session

**Claude Prompt:**
```
Create chat API routes for the AI-powered todo chatbot:

1. Create src/routes/chat.js with protected routes:
   - GET /sessions:
     * Requires valid JWT token (use auth middleware)
     * Gets all chat sessions for authenticated user
     * Returns sessions with id, title, created_at
     * Proper error handling for database issues

   - POST /sessions:
     * Requires valid JWT token
     * Validates title parameter
     * Creates new chat session for authenticated user
     * Returns created session with id and timestamps
     * Proper error handling for validation failures

   - GET /sessions/:id/messages:
     * Requires valid JWT token
     * Validates session belongs to user
     * Gets all messages for specified session
     * Returns messages with id, role, content, timestamp
     * Error handling for non-existent sessions

   - POST /sessions/:id/messages:
     * Requires valid JWT token
     * Validates session belongs to user
     * Validates message content and role
     * Adds user message to session
     * Returns added message
     * Error handling for non-existent sessions

2. Include proper input validation and sanitization
3. Return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
4. Include error handling for unauthorized access attempts
5. Add comments explaining security considerations and data validation

Update server.js to include these routes under /api/chat path with auth middleware.
```

---

### Phase 3: AI Integration

#### Step 3.1: Set up OpenAI client and configuration
- **Category:** Backend
- **Dependencies:** Step 1.1
- **Files:** src/config/openai.js, src/utils/aiHelper.js
- **Acceptance Criteria:**
  - [ ] OpenAI client initialized with API key
  - [ ] Configuration for model parameters
  - [ ] Helper functions for AI interactions
  - [ ] Error handling for API failures

**Claude Prompt:**
```
Set up OpenAI integration for the AI-powered todo chatbot:

1. Create src/config/openai.js with:
   - Import openai package
   - Initialize OpenAI client with API key from process.env.OPENAI_API_KEY
   - Configuration object with:
     * Model: gpt-3.5-turbo or gpt-4 (configurable)
     * Temperature: 0.7 (configurable)
     * Max tokens: 1000 (configurable)
     * Timeout settings
   - Export configured client and settings

2. Create src/utils/aiHelper.js with:
   - sendMessageToAI(prompt, options) function
   - formatTodoResponse(text) function to parse AI responses for todo actions
   - handleError(error) function to handle OpenAI errors gracefully
   - Proper logging for debugging AI interactions
   - Rate limiting considerations in comments

3. Add error handling for:
   - Invalid API keys
   - Network timeouts
   - API quota exceeded
   - Invalid responses

4. Include proper environment variable validation
5. Add documentation comments for all functions

Make sure to handle API costs considerations and include proper error responses to clients.
```

---

#### Step 3.2: Implement AI chat processing logic
- **Category:** Backend
- **Dependencies:** Step 3.1, Step 1.5
- **Files:** src/utils/chatProcessor.js
- **Acceptance Criteria:**
  - [ ] Function to process user messages and generate AI responses
  - [ ] Logic to detect todo-related intents from user input
  - [ ] Integration with todo model for creating/updating todos
  - [ ] Proper context management for conversations

**Claude Prompt:**
```
Create AI chat processing logic for the AI-powered todo chatbot:

1. Create src/utils/chatProcessor.js with:
   - processUserMessage(userId, sessionId, userMessage) function
   - analyzeMessageIntent(messageText) function to detect todo actions
   - handleTodoCreation(intentData) function to create todos
   - handleTodoUpdate(intentData) function to update todos
   - handleTodoListing() function to retrieve user's todos
   - generateAIResponse(context, userMessage) function to get AI response
   - getAllContextForSession(sessionId) function to gather conversation context

2. Intent detection should recognize:
   - Creating new todos ("add", "create", "new task")
   - Updating existing todos ("complete", "done", "mark as")
   - Listing todos ("show", "list", "what")
   - Other conversational inputs

3. Include proper error handling:
   - Invalid user inputs
   - Database operation failures
   - AI API failures
   - Unauthorized access attempts

4. Context management should include:
   - Previous messages in session
   - User's current todos
   - Session history for continuity

5. Return structured responses with:
   - AI-generated text
   - Action indicators (if todo operations occurred)
   - Updated todo list if changed

6. Include logging for debugging and monitoring

Make sure the processor handles both simple and complex todo management scenarios.
```

---

#### Step 3.3: Implement enhanced chat endpoint with AI processing
- **Category:** Backend
- **Dependencies:** Step 3.2, Step 2.3
- **Files:** src/routes/chat.js (update)
- **Acceptance Criteria:**
  - [ ] Enhanced POST /api/chat/sessions/:id/messages to process with AI
  - [ ] Automatic todo creation/update based on AI analysis
  - [ ] Returns both AI response and affected todos
  - [ ] Maintains conversation context

**Claude Prompt:**
```
Enhance the chat API routes to integrate AI processing for the AI-powered todo chatbot:

1. Update src/routes/chat.js POST /sessions/:id/messages route:
   - Validate session belongs to user
   - Call processUserMessage from chatProcessor
   - Save both user message and AI response to database
   - Return combined response with:
     * AI response text
     * Any newly created todos
     * Any updated todos
     * Updated todo list
   - Handle errors gracefully with appropriate status codes

2. Add new route POST /api/chat/process:
   - Takes user message and optional session ID
   - Creates new session if none provided
   - Processes message through AI and returns full response
   - Useful for initial conversations without existing session

3. Include proper validation:
   - Message content is not empty
   - Session ID format is valid
   - User has access to session

4. Add rate limiting considerations in comments
5. Include proper error handling for:
   - AI service unavailability
   - Database save failures
   - Processing timeouts
   - Invalid session access

6. Add response caching considerations for similar queries in comments

Update the response format to include both AI responses and any affected todo items.
```

---

### Phase 4: MCP Server Components

#### Step 4.1: Set up MCP server configuration
- **Category:** Infrastructure
- **Dependencies:** Step 1.1
- **Files:** mcp-server/index.js, mcp-server/config.js, mcp-server/.env
- **Acceptance Criteria:**
  - [ ] MCP server structure created
  - [ ] Configuration for MCP protocol
  - [ ] Environment setup for MCP server
  - [ ] Basic health check endpoint

**Claude Prompt:**
```
Set up MCP (Model Context Protocol) server components for the AI-powered todo chatbot:

1. Create mcp-server/ directory structure:
   - mcp-server/index.js (main server entry point)
   - mcp-server/config.js (MCP configuration)
   - mcp-server/.env (MCP server environment)
   - mcp-server/routes/ (API routes for MCP)
   - mcp-server/models/ (data models for MCP)
   - mcp-server/utils/ (utility functions for MCP)

2. Create mcp-server/config.js with:
   - MCP protocol configuration
   - Server port settings (default 3001)
   - CORS settings for MCP clients
   - API key validation setup
   - Connection pooling settings

3. Create mcp-server/index.js with:
   - Express app setup for MCP server
   - Middleware configuration
   - Basic health check endpoint at GET /
   - Error handling setup
   - Server startup logic

4. Create mcp-server/.env with:
   - MCP_PORT=3001
   - MCP_API_KEY=your_mcp_api_key_here
   - MCP_SERVER_NAME=todo-chatbot-mcp

5. Include proper error handling and logging
6. Add comments explaining MCP-specific configurations

Ensure the MCP server can start independently and has proper security configurations.
```

---

#### Step 4.2: Implement MCP todo management endpoints
- **Category:** Backend
- **Dependencies:** Step 4.1, Step 1.4
- **Files:** mcp-server/routes/todos.js, mcp-server/models/TodoAdapter.js
- **Acceptance Criteria:**
  - [ ] GET /mcp/todos endpoint for listing todos
  - [ ] POST /mcp/todos endpoint for creating todos
  - [ ] PUT /mcp/todos/:id endpoint for updating todos
  - [ ] Todo adapter to connect MCP server to main application database

**Claude Prompt:**
```
Implement MCP (Model Context Protocol) todo management endpoints for the AI-powered todo chatbot:

1. Create mcp-server/models/TodoAdapter.js with:
   - Connect to main application's database
   - getAllTodos(userId) function
   - createTodo(userId, title, description) function
   - updateTodo(id, updates) function
   - deleteTodo(id) function
   - toggleTodoCompletion(id) function
   - Proper error handling for database connections
   - Validation for user permissions

2. Create mcp-server/routes/todos.js with:
   - GET /:
     * Authenticate with MCP API key
     * Validate userId parameter
     * Return user's todos in MCP-compatible format
     * Include proper error handling

   - POST /:
     * Authenticate with MCP API key
     * Validate required fields (userId, title)
     * Create new todo via TodoAdapter
     * Return created todo in MCP format
     * Proper error handling for validation failures

   - PUT /:id:
     * Authenticate with MCP API key
     * Validate todo belongs to user
     * Update todo via TodoAdapter
     * Return updated todo in MCP format
     * Error handling for non-existent todos

   - DELETE /:id:
     * Authenticate with MCP API key
     * Validate todo belongs to user
     * Delete todo via TodoAdapter
     * Return success confirmation
     * Error handling for non-existent todos

3. Include proper input validation and sanitization
4. Return appropriate HTTP status codes
5. Add MCP-specific headers and response formatting
6. Include security measures for API key validation

Mount these routes under /mcp/todos in the MCP server.
```

---

#### Step 4.3: Implement MCP chat context endpoints
- **Category:** Backend
- **Dependencies:** Step 4.2, Step 1.5
- **Files:** mcp-server/routes/context.js, mcp-server/models/ContextProvider.js
- **Acceptance Criteria:**
  - [ ] GET /mcp/context/:userId endpoint for user context
  - [ ] GET /mcp/context/:userId/todos endpoint for user's todos
  - [ ] GET /mcp/context/:userId/chat-history endpoint for conversation history
  - [ ] Context provider to aggregate user data for AI models

**Claude Prompt:**
```
Implement MCP (Model Context Protocol) chat context endpoints for the AI-powered todo chatbot:

1. Create mcp-server/models/ContextProvider.js with:
   - getUserContext(userId) function to aggregate user data
   - getUserTodos(userId) function to get current todos
   - getUserChatHistory(userId, limit) function to get recent conversations
   - formatForAIModel(data) function to prepare context for AI consumption
   - Proper error handling for data retrieval
   - Privacy considerations for sensitive data

2. Create mcp-server/routes/context.js with:
   - GET /:userId:
     * Authenticate with MCP API key
     * Validate userId parameter
     * Return comprehensive user context
     * Include user profile, todos count, recent activity
     * Proper error handling for invalid users

   - GET /:userId/todos:
     * Authenticate with MCP API key
     * Validate userId parameter
     * Return user's todos in AI-friendly format
     * Include completion status and descriptions
     * Proper error handling for database issues

   - GET /:userId/chat-history:
     * Authenticate with MCP API key
     * Validate userId parameter
     * Accept optional limit parameter (default 10)
     * Return recent chat messages in chronological order
     * Format suitable for AI context provision
     * Proper error handling for data retrieval

3. Include proper input validation and sanitization
4. Return appropriate HTTP status codes
5. Add MCP-specific headers and response formatting
6. Include privacy and security measures
7. Add rate limiting considerations in comments

Format responses in a way that's easily consumable by AI models for context awareness.
```

---

#### Step 4.4: Implement MCP server startup and health monitoring
- **Category:** Infrastructure
- **Dependencies:** Step 4.3
- **Files:** mcp-server/server.js, mcp-server/health.js
- **Acceptance Criteria:**
  - [ ] Main MCP server startup with all routes
  - [ ] Health check endpoints for monitoring
  - [ ] Proper error handling and logging
  - [ ] Graceful shutdown procedures

**Claude Prompt:**
```
Implement MCP server startup and health monitoring for the AI-powered todo chatbot:

1. Create mcp-server/server.js with:
   - Complete server initialization
   - Import all necessary routes (todos, context)
   - Setup middleware (CORS, JSON parsing, error handling)
   - Mount routes under appropriate paths
   - Database connection validation on startup
   - Proper logging configuration
   - Error handling middleware

2. Create mcp-server/health.js with:
   - GET /health endpoint returning server status
   - GET /health/db endpoint checking database connectivity
   - GET /health/api endpoint checking external API availability (OpenAI)
   - Response format with status, timestamp, and details
   - Appropriate HTTP status codes (200 for healthy, 503 for unhealthy)

3. Update mcp-server/index.js to:
   - Import and use the server configuration
   - Start server on configured port
   - Handle startup errors gracefully
   - Implement graceful shutdown on SIGTERM/SIGINT
   - Add logging for startup and shutdown events

4. Include comprehensive error handling:
   - Uncaught exceptions
   - Unhandled promise rejections
   - Database connection failures
   - External API unavailability

5. Add monitoring considerations in comments:
   - Performance metrics
   - API usage tracking
   - Error rate monitoring

6. Include configuration validation at startup

Ensure the MCP server can run independently and report its health status properly.
```

---

### Phase 5: Frontend Components

#### Step 5.1: Set up frontend project structure
- **Category:** Frontend
- **Dependencies:** None
- **Files:** frontend/package.json, frontend/src/index.html, frontend/src/App.jsx, frontend/vite.config.js
- **Acceptance Criteria:**
  - [ ] React project with Vite setup
  - [ ] Basic project structure with components directory
  - [ ] API client setup for backend communication
  - [ ] Routing configuration

**Claude Prompt:**
```
Set up the frontend project structure for the AI-powered todo chatbot:

1. Create frontend/ directory with:
   - package.json with React and Vite dependencies:
     * react, react-dom
     * @vitejs/plugin-react
     * axios for API calls
     * react-router-dom for routing
     * @headlessui/react for UI components
     * @heroicons/react for icons

   - vite.config.js with:
     * React plugin configuration
     * Dev server proxy to backend (localhost:3000)
     * Build output settings

   - src/index.html with basic HTML structure
   - src/main.jsx with React root rendering
   - src/App.jsx as main application component

2. Create src/ directory structure:
   - src/components/ (reusable UI components)
   - src/pages/ (page-level components)
   - src/hooks/ (custom React hooks)
   - src/utils/ (utility functions)
   - src/services/ (API service functions)
   - src/styles/ (CSS files)

3. Create basic App.jsx with:
   - Router setup with routes for login, dashboard, chat
   - Main layout structure
   - Navigation component
   - State management for authentication

4. Create src/services/api.js with:
   - Axios instance configured with base URL
   - Request interceptors for adding auth tokens
   - Response interceptors for error handling
   - Base API functions (get, post, put, delete)

5. Include basic styling setup with Tailwind CSS configuration
6. Add environment variables support for API URLs

Ensure the project can be started with npm run dev and connects to the backend API.
```

---

#### Step 5.2: Implement authentication components
- **Category:** Frontend
- **Dependencies:** Step 5.1
- **Files:** frontend/src/pages/LoginPage.jsx, frontend/src/pages/RegisterPage.jsx, frontend/src/hooks/useAuth.js
- **Acceptance Criteria:**
  - [ ] Login page with form and validation
  - [ ] Registration page with form and validation
  - [ ] Authentication hook for managing user state
  - [ ] Protected route wrapper

**Claude Prompt:**
```
Create authentication components for the AI-powered todo chatbot frontend:

1. Create frontend/src/hooks/useAuth.js with:
   - Custom hook for authentication state management
   - Functions: login(credentials), register(userData), logout(), getCurrentUser()
   - Local storage management for JWT tokens
   - Loading and error states
   - Token expiration handling

2. Create frontend/src/pages/LoginPage.jsx with:
   - Form with email and password fields
   - Form validation and error display
   - Submit handler calling auth hook
   - Loading state during authentication
   - Link to registration page
   - Error message display for failed login

3. Create frontend/src/pages/RegisterPage.jsx with:
   - Form with email, password, and name fields
   - Form validation (email format, password strength, name length)
   - Submit handler calling auth hook
   - Loading state during registration
   - Link to login page
   - Error message display for registration failures

4. Create frontend/src/components/ProtectedRoute.jsx with:
   - Component that checks authentication status
   - Redirects to login if not authenticated
   - Renders children if authenticated
   - Loading state while checking auth status

5. Update frontend/src/App.jsx to:
   - Include routes for login and register
   - Wrap protected pages with ProtectedRoute
   - Provide auth context to child components

6. Include proper accessibility attributes
7. Add loading spinners and visual feedback
8. Include error boundary patterns for auth-related errors

Use Headless UI components for accessible form elements and proper error messaging.
```

---

#### Step 5.3: Implement todo list and management components
- **Category:** Frontend
- **Dependencies:** Step 5.2
- **Files:** frontend/src/pages/DashboardPage.jsx, frontend/src/components/TodoList.jsx, frontend/src/components/TodoForm.jsx
- **Acceptance Criteria:**
  - [ ] Dashboard page showing user's todos
  - [ ] Todo list component with filtering and sorting
  - [ ] Todo form component for creating/editing todos
  - [ ] Interactive UI for marking todos as complete

**Claude Prompt:**
```
Create todo list and management components for the AI-powered todo chatbot frontend:

1. Create frontend/src/components/TodoList.jsx with:
   - Receives todos array as prop
   - Displays todos in a clean, organized list
   - Checkbox for toggling completion status
   - Edit/delete buttons for each todo
   - Filtering options (all, active, completed)
   - Sorting options (created date, title)
   - Empty state when no todos exist
   - Loading states during updates

2. Create frontend/src/components/TodoForm.jsx with:
   - Form for creating new todos
   - Title input field (required)
   - Description textarea (optional)
   - Submit button with loading state
   - Form validation and error display
   - Cancel button to close form
   - Support for editing existing todos

3. Create frontend/src/pages/DashboardPage.jsx with:
   - Header with user greeting
   - Stats summary (total, completed, pending)
   - TodoForm for adding new todos
   - TodoList component displaying user's todos
   - Search/filter controls
   - Empty state when user has no todos

4. Create frontend/src/hooks/useTodos.js with:
   - Custom hook for todo operations
   - Functions: fetchTodos(), createTodo(), updateTodo(), deleteTodo(), toggleTodo()
   - Loading and error states
   - Optimistic updates for better UX
   - Error handling and retry mechanisms

5. Include proper accessibility features:
   - Keyboard navigation
   - Screen reader support
   - Focus management
   - ARIA labels

6. Add animations and transitions for smooth UX
7. Include confirmation dialogs for destructive actions
8. Add keyboard shortcuts where appropriate

Use Headless UI components for accessible interactive elements and proper form validation.
```

---

#### Step 5.4: Implement chat interface components
- **Category:** Frontend
- **Dependencies:** Step 5.3
- **Files:** frontend/src/pages/ChatPage.jsx, frontend/src/components/ChatInterface.jsx, frontend/src/components/MessageBubble.jsx
- **Acceptance Criteria:**
  - [ ] Chat page with conversation interface
  - [ ] Message bubbles for user and AI messages
  - [ ] Input area with message composition
  - [ ] Real-time message sending and receiving
  - [ ] Session management within chat

**Claude Prompt:**
```
Create chat interface components for the AI-powered todo chatbot frontend:

1. Create frontend/src/components/MessageBubble.jsx with:
   - Displays individual chat messages
   - Different styling for user vs AI messages
   - Timestamp display
   - Loading indicator for AI responses
   - Proper text formatting and line breaks
   - Avatar differentiation for user/AI

2. Create frontend/src/components/ChatInterface.jsx with:
   - Message history display area
   - Auto-scrolling to latest message
   - Message input field with send button
   - Support for multi-line input (Shift+Enter for new lines)
   - Send button disabled during AI processing
   - Typing indicators for AI responses
   - Error display for failed messages

3. Create frontend/src/pages/ChatPage.jsx with:
   - Full chat page layout
   - Session selector/dropdown (if multiple sessions)
   - New session creation button
   - ChatInterface component
   - Sidebar with recent sessions (optional)
   - Connection status indicator

4. Create frontend/src/hooks/useChat.js with:
   - Custom hook for chat operations
   - Functions: sendMessage(), createSession(), loadSession(), loadSessions()
   - Real-time message handling
   - Loading states for AI processing
   - Error handling for chat operations
   - WebSocket or polling implementation for real-time updates

5. Include rich interaction features:
   - Quick reply suggestions
   - Ability to edit sent messages
   - Copy message functionality
   - Attachment support (future extension)

6. Add accessibility features:
   - Screen reader announcements
   - Keyboard navigation
   - Focus indicators
   - ARIA live regions for new messages

7. Implement smooth scrolling and message animations
8. Add offline support indicators

Use Headless UI for accessible chat components and proper real-time interaction patterns.
```

---

### Phase 6: Testing

#### Step 6.1: Set up testing framework and utilities
- **Category:** Testing
- **Dependencies:** Step 1.1
- **Files:** jest.config.js, src/tests/setup.js, src/tests/utils/testHelpers.js
- **Acceptance Criteria:**
  - [ ] Jest configuration for backend testing
  - [ ] Test database setup/teardown utilities
  - [ ] Mock services for external dependencies
  - [ ] Test utilities for common operations

**Claude Prompt:**
```
Set up comprehensive testing framework and utilities for the AI-powered todo chatbot:

1. Create jest.config.js with:
   - Test environment configuration (node)
   - Module name mapping
   - Coverage thresholds
   - Test file patterns
   - Setup files configuration

2. Create src/tests/setup.js with:
   - Global test setup
   - Database connection for tests
   - Cleanup functions
   - Mock services initialization

3. Create src/tests/utils/testHelpers.js with:
   - createUserForTest(userData) function
   - createTodoForTest(userId, todoData) function
   - createChatSessionForTest(userId, sessionData) function
   - createChatMessageForTest(sessionId, messageData) function
   - clearTestData() function
   - generateAuthToken(userId) function
   - mockDatabaseConnection() function
   - mockOpenAIClient() function

4. Install and configure testing dependencies:
   - jest
   - supertest
   - @types/jest (if using TypeScript)
   - nodemon (for development)

5. Create src/tests/integration/ directory structure
6. Create src/tests/unit/ directory structure
7. Create src/tests/e2e/ directory structure (planned)

6. Include proper test database configuration:
   - Separate database for tests
   - Migration setup for test database
   - Teardown after test runs

7. Add common test patterns and best practices in comments

Ensure tests can run independently and don't interfere with each other or production data.
```

---

#### Step 6.2: Implement unit tests for models
- **Category:** Testing
- **Dependencies:** Step 6.1, Step 1.3, Step 1.4, Step 1.5
- **Files:** src/tests/unit/models/User.test.js, src/tests/unit/models/Todo.test.js, src/tests/unit/models/ChatSession.test.js
- **Acceptance Criteria:**
  - [ ] Unit tests for User model methods
  - [ ] Unit tests for Todo model methods
  - [ ] Unit tests for ChatSession and ChatMessage models
  - [ ] Proper mocking and test data isolation

**Claude Prompt:**
```
Create comprehensive unit tests for the data models of the AI-powered todo chatbot:

1. Create src/tests/unit/models/User.test.js with tests for:
   - User.create(email, password, name) method
     * Valid user creation
     * Duplicate email handling
     * Password hashing verification
     * Input validation tests
     * Error handling scenarios

   - User.findById(id) method
     * Successful user retrieval
     * Non-existent user handling
     * Database error handling

   - User.findByEmail(email) method
     * Successful email lookup
     * Non-existent email handling
     * Case sensitivity tests

   - User.validatePassword(plainPassword) method
     * Correct password validation
     * Incorrect password rejection
     * Edge case handling

2. Create src/tests/unit/models/Todo.test.js with tests for:
   - Todo.create(userId, title, description) method
     * Valid todo creation
     * Required field validation
     * Invalid user ID handling
     * Database constraint tests

   - Todo.findById(id) method
     * Successful todo retrieval
     * Non-existent todo handling
     * Database error scenarios

   - Todo.findByUserId(userId) method
     * Correct user todo retrieval
     * Empty results handling
     * Invalid user ID tests

   - Todo.update(id, updates) method
     * Successful updates
     * Partial updates
     * Non-existent todo handling

   - Todo.delete(id) method
     * Successful deletion
     * Non-existent todo handling
     * Cascade effect verification

   - Todo.toggleCompleted(id) method
     * Status toggle functionality
     * Non-existent todo handling

3. Create src/tests/unit/models/ChatSession.test.js with tests for:
   - ChatSession.create(userId, title) method
     * Valid session creation
     * Required field validation
     * Invalid user ID handling

   - ChatSession.findById(id) method
     * Successful session retrieval
     * Non-existent session handling

   - ChatSession.findByUserId(userId) method
     * Correct user session retrieval
     * Empty results handling

   - ChatSession.updateTitle(id, title) method
     * Successful title updates
     * Non-existent session handling

4. Create src/tests/unit/models/ChatMessage.test.js with tests for:
   - ChatMessage.create(sessionId, role, content) method
     * Valid message creation
     * Role validation ('user'/'assistant')
     * Required field validation
     * Invalid session ID handling

   - ChatMessage.findBySessionId(sessionId) method
     * Successful message retrieval
     * Empty session handling
     * Chronological ordering verification

5. Include proper test data cleanup after each test
6. Use mocks for database connections where appropriate
7. Test both positive and negative scenarios
8. Verify proper error messages and types

Use the test helpers from src/tests/utils/testHelpers.js for creating test data.
```

---

## Validation Checklist
- [x] All spec requirements covered
- [x] No circular dependencies
- [x] Each step is atomic and testable
- [x] Prompts are self-contained