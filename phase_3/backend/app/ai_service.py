import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlmodel import Session, select
from uuid import UUID

import openai
from openai import OpenAI
from pydantic import BaseModel

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.task import Task
from app.config.settings import settings


class ToolCallResult(BaseModel):
    """Represents the result of a tool call"""
    tool_call_id: str
    name: str
    result: Any


class AIService:
    """
    Service for handling AI interactions using OpenAI's API.
    Uses the Assistants API for conversation management and tool calling.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

        # System prompt for task management
        self.system_prompt = """You are a helpful AI assistant for task management. You can help users create, update, delete, list, and complete tasks.

        You have access to the following tools:
        - create_task: Create a new task with title, description, due_date, and priority
        - update_task: Update an existing task
        - delete_task: Delete a task
        - get_tasks: Get all tasks for the user
        - complete_task: Mark a task as completed or not completed

        Always respond in a friendly and helpful manner. When using tools, make sure to validate the parameters carefully.
        If you're unsure about any details, ask the user for clarification before proceeding.
        """

    def create_assistant(self):
        """Create an assistant with the task management tools"""
        try:
            assistant = self.client.beta.assistants.create(
                name="Task Management Assistant",
                description="An AI assistant for managing tasks",
                model=self.model,
                instructions=self.system_prompt,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "create_task",
                            "description": "Create a new task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Title of the task"},
                                    "description": {"type": "string", "description": "Description of the task"},
                                    "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority of the task"}
                                },
                                "required": ["title"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "update_task",
                            "description": "Update an existing task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "ID of the task to update"},
                                    "title": {"type": "string", "description": "New title of the task"},
                                    "description": {"type": "string", "description": "New description of the task"},
                                    "due_date": {"type": "string", "description": "New due date in YYYY-MM-DD format"},
                                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority of the task"},
                                    "completed": {"type": "boolean", "description": "Whether the task is completed"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "delete_task",
                            "description": "Delete a task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "ID of the task to delete"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_tasks",
                            "description": "Get all tasks for the user",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "filter_completed": {"type": "boolean", "description": "Filter tasks by completion status"}
                                }
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "complete_task",
                            "description": "Mark a task as completed or not completed",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "ID of the task to update"},
                                    "completed": {"type": "boolean", "description": "Whether the task is completed"}
                                },
                                "required": ["task_id", "completed"]
                            }
                        }
                    }
                ]
            )
            return assistant
        except Exception as e:
            print(f"Error creating assistant: {e}")
            raise

    async def process_message(
        self,
        db_session: Session,
        user_id: str,
        conversation_id: Optional[str],
        message_content: str
    ) -> tuple[str, str, List[ToolCallResult]]:
        """
        Process a user message and return AI response with any tool calls executed

        Args:
            db_session: Database session
            user_id: ID of the user
            conversation_id: ID of the conversation (None for new conversation)
            message_content: User's message

        Returns:
            Tuple of (response_content, conversation_id, tool_call_results)
        """
        # Get or create assistant
        assistant = self.create_assistant()

        # Get or create thread for conversation
        if conversation_id:
            # Load existing conversation and messages from DB to recreate thread state
            conversation = db_session.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Invalid conversation or unauthorized access")

            # Create thread and add existing messages
            thread = self.client.beta.threads.create()

            # Add recent messages to the thread (up to max context)
            statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.timestamp.desc())
                .limit(settings.DEFAULT_MAX_CONTEXT_MESSAGES)
            )
            messages = db_session.exec(statement).all()

            # Add messages in reverse chronological order to maintain proper sequence
            for msg in reversed(messages):
                self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role=msg.role,
                    content=msg.content
                )
        else:
            # Create new thread for new conversation
            thread = self.client.beta.threads.create()

            # Create new conversation record
            new_conversation = Conversation(
                user_id=user_id,
                title=message_content[:50] + "..." if len(message_content) > 50 else message_content
            )
            db_session.add(new_conversation)
            db_session.commit()
            db_session.refresh(new_conversation)
            conversation_id = str(new_conversation.id)

        # Add user message to thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )

        # Run the assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for the run to complete
        while run.status in ['queued', 'in_progress']:
            await asyncio.sleep(0.5)
            run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Handle tool calls if any
        tool_call_results = []
        if run.status == 'requires_action' and run.required_action.type == 'submit_tool_outputs':
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            # Execute each tool call
            tool_outputs = []
            for tool_call in tool_calls:
                try:
                    # Extract function name and arguments
                    func_name = tool_call.function.name
                    func_args = eval(tool_call.function.arguments)  # Note: In production, use json.loads instead

                    # Execute the function based on name
                    result = await self._execute_tool_call(
                        db_session,
                        user_id,
                        func_name,
                        func_args
                    )

                    # Store result
                    tool_call_result = ToolCallResult(
                        tool_call_id=tool_call.id,
                        name=func_name,
                        result=result
                    )
                    tool_call_results.append(tool_call_result)

                    # Add to outputs for assistant
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": str(result)
                    })
                except Exception as e:
                    print(f"Error executing tool call {tool_call.function.name}: {e}")
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": f"Error: {str(e)}"
                    })

            # Submit tool outputs
            run = self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

            # Wait for the run to complete after tool outputs
            while run.status in ['queued', 'in_progress']:
                await asyncio.sleep(0.5)
                run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Get the assistant's response
        messages = self.client.beta.threads.messages.list(thread_id=thread.id, order="asc")
        assistant_responses = [
            msg.content[0].text.value
            for msg in messages.data
            if msg.role == "assistant"
        ]

        # Combine all assistant responses
        response_content = " ".join(assistant_responses) if assistant_responses else "I couldn't process your request."

        return response_content, conversation_id, tool_call_results

    async def _execute_tool_call(
        self,
        db_session: Session,
        user_id: str,
        func_name: str,
        func_args: Dict
    ) -> Any:
        """Execute a tool call based on its name and arguments"""
        if func_name == "create_task":
            return await self._create_task(db_session, user_id, func_args)
        elif func_name == "update_task":
            return await self._update_task(db_session, user_id, func_args)
        elif func_name == "delete_task":
            return await self._delete_task(db_session, user_id, func_args)
        elif func_name == "get_tasks":
            return await self._get_tasks(db_session, user_id, func_args)
        elif func_name == "complete_task":
            return await self._complete_task(db_session, user_id, func_args)
        else:
            raise ValueError(f"Unknown function: {func_name}")

    async def _create_task(self, db_session: Session, user_id: str, args: Dict) -> Dict:
        """Create a new task"""
        # Prepare task data
        task_data = {
            "user_id": user_id,
            "title": args.get("title"),
            "description": args.get("description", ""),
            "completed": args.get("completed", False),
            "priority": args.get("priority", "medium")
        }

        # Handle due_date if provided
        if "due_date" in args and args["due_date"]:
            from datetime import datetime
            task_data["due_date"] = datetime.strptime(args["due_date"], "%Y-%m-%d")

        # Create task
        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        return {"success": True, "task_id": str(task.id), "message": f"Task '{task.title}' created successfully"}

    async def _update_task(self, db_session: Session, user_id: str, args: Dict) -> Dict:
        """Update an existing task"""
        task_id = args.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")

        # Get the task
        task = db_session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Check user ownership
        if task.user_id != user_id:
            raise ValueError("Unauthorized: Cannot modify another user's task")

        # Update task fields if provided
        update_fields = ["title", "description", "due_date", "priority", "completed"]
        for field in update_fields:
            if field in args:
                value = args[field]
                if field == "due_date" and value:
                    from datetime import datetime
                    value = datetime.strptime(value, "%Y-%m-%d")
                setattr(task, field, value)

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        return {"success": True, "task_id": str(task.id), "message": f"Task '{task.title}' updated successfully"}

    async def _delete_task(self, db_session: Session, user_id: str, args: Dict) -> Dict:
        """Delete a task"""
        task_id = args.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")

        # Get the task
        task = db_session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Check user ownership
        if task.user_id != user_id:
            raise ValueError("Unauthorized: Cannot delete another user's task")

        # Delete the task
        db_session.delete(task)
        db_session.commit()

        return {"success": True, "task_id": task_id, "message": f"Task deleted successfully"}

    async def _get_tasks(self, db_session: Session, user_id: str, args: Dict) -> Dict:
        """Get tasks for the user"""
        # Build query with user filter
        query = select(Task).where(Task.user_id == user_id)

        # Apply completion filter if specified
        filter_completed = args.get("filter_completed")
        if filter_completed is not None:
            query = query.where(Task.completed == filter_completed)

        # Execute query
        tasks = db_session.exec(query).all()

        # Format response
        tasks_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority
            }
            if task.due_date:
                task_dict["due_date"] = task.due_date.isoformat()
            tasks_list.append(task_dict)

        return {
            "success": True,
            "count": len(tasks_list),
            "tasks": tasks_list
        }

    async def _complete_task(self, db_session: Session, user_id: str, args: Dict) -> Dict:
        """Mark a task as completed or not completed"""
        task_id = args.get("task_id")
        completed = args.get("completed")

        if not task_id or completed is None:
            raise ValueError("task_id and completed status are required")

        # Get the task
        task = db_session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")

        # Check user ownership
        if task.user_id != user_id:
            raise ValueError("Unauthorized: Cannot modify another user's task")

        # Update completion status
        task.completed = completed
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        status_str = "completed" if completed else "marked as incomplete"
        return {
            "success": True,
            "task_id": str(task.id),
            "message": f"Task '{task.title}' {status_str} successfully"
        }


# Global AI service instance
ai_service = AIService()