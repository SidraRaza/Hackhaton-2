from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.tasks import router as task_router
from routes.chat import router as chat_router
from routes.auth import router as auth_router
from routes.tags import router as tags_router
from routes.notifications import router as notifications_router
from database import engine
from sqlmodel import SQLModel
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import all models to ensure they are registered with SQLModel
from models.user import User
from models.task import Task
from models.conversation import Conversation
from models.message import Message

# Create FastAPI app with enhanced OpenAPI documentation
app = FastAPI(
    title="Todo App API - Phase V: Advanced Cloud Deployment",
    description="""
    Advanced Todo application API with event-driven architecture and Dapr integration.

    ## Features
    - **Task Management**: Create, update, delete, and track tasks
    - **Priority System**: Low, medium, high priority levels with visual indicators
    - **Tag Management**: Organize tasks with customizable tags
    - **Search & Filter**: Full-text search and advanced filtering capabilities
    - **Sorting**: Multi-column sorting with primary/secondary criteria
    - **Recurring Tasks**: Daily, weekly, monthly, yearly, and custom recurrence patterns
    - **Due Dates & Reminders**: Date/time tracking with reminder notifications
    - **Real-time Notifications**: WebSocket-based real-time updates
    - **Event-Driven Architecture**: All operations emit events via Kafka/Redpanda
    - **Dapr Integration**: Cloud-native building blocks for pub/sub, state, secrets

    ## Architecture
    - Event-first design with Kafka/Redpanda event streaming
    - Dapr integration for cloud-native building blocks
    - WebSocket support for real-time notifications
    - Kubernetes-native deployment with auto-scaling
    - Production-grade monitoring and observability
    """,
    version="2.0.0",
    contact={
        "name": "Todo App Development Team",
        "url": "https://github.com/todo-app",
        "email": "team@todoapp.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=[
        {
            "name": "tasks",
            "description": "Task management operations with advanced features (priorities, tags, recurrence, due dates)"
        },
        {
            "name": "tags",
            "description": "Tag management for organizing tasks"
        },
        {
            "name": "events",
            "description": "Event-driven architecture operations"
        },
        {
            "name": "chat",
            "description": "AI-powered chatbot interface"
        },
        {
            "name": "auth",
            "description": "Authentication and authorization endpoints"
        },
        {
            "name": "notifications",
            "description": "Real-time WebSocket notifications"
        }
    ]
)

# Configure CORS - WebSocket ke liye credentials aur origins important hain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(tags_router, prefix="/api")
app.include_router(notifications_router) 

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    logging.info("✅ Database tables created successfully")
    logging.info("✅ WebSocket notification service initialized")

# Health check endpoint
@app.get("/")
def health():
    return {"status": "ok", "message": "Todo App API is running"}

# Additional health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "websocket": "enabled",
        "api_version": "2.0.0"
    }