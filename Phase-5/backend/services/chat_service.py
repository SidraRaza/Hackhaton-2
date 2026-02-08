from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from models import Conversation, Message
from tools.task_tools import TaskMCPTools
from datetime import datetime


class ChatService:
    """Service class for chat-related operations"""

    @staticmethod
    def create_conversation(session: Session, user_id: str) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(session: Session, conversation_id: int, user_id: str) -> Optional[Conversation]:
        """Get a specific conversation for a user"""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return session.exec(statement).first()

    @staticmethod
    def get_all_conversations(session: Session, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc())
        return list(session.exec(statement).all())

    @staticmethod
    def delete_conversation(session: Session, conversation_id: int, user_id: str) -> bool:
        """Delete a conversation"""
        conversation = ChatService.get_conversation(session, conversation_id, user_id)
        if not conversation:
            return False
        
        # Delete all messages in the conversation
        statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = session.exec(statement).all()
        for message in messages:
            session.delete(message)
        
        # Delete the conversation
        session.delete(conversation)
        session.commit()
        return True

    @staticmethod
    def get_messages_for_conversation(session: Session, conversation_id: int, user_id: str) -> List[Message]:
        """Get all messages for a specific conversation"""
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        return list(session.exec(statement).all())

    @staticmethod
    def add_message(session: Session, user_id: str, conversation_id: int, role: str, content: str) -> Message:
        """Add a message to a conversation"""
        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def process_chat_message(
        session: Session, 
        user_id: str, 
        message_content: str, 
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Process a chat message and return response with tool calls"""
        # Get or create conversation
        if conversation_id:
            conversation = ChatService.get_conversation(session, conversation_id, user_id)
            if not conversation:
                return {
                    "success": False,
                    "error": "Conversation not found"
                }
        else:
            conversation = ChatService.create_conversation(session, user_id)

        # Add user message
        user_message = ChatService.add_message(
            session, user_id, conversation.id, "user", message_content
        )

        # Process with AI and tools
        response_text, tool_calls = ChatService._process_with_ai_and_tools(
            message_content, session, user_id
        )

        # Add assistant message
        assistant_message = ChatService.add_message(
            session, user_id, conversation.id, "assistant", response_text
        )

        return {
            "success": True,
            "conversation_id": conversation.id,
            "response": response_text,
            "tool_calls": tool_calls,
            "user_message_id": user_message.id,
            "assistant_message_id": assistant_message.id
        }

    @staticmethod
    def _process_with_ai_and_tools(
        message: str, 
        session: Session, 
        user_id: str
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Internal method to process message with AI and tool calls"""
        message_lower = message.lower()
        tool_calls = []

        # Handle task-related commands
        if "add task" in message_lower or "create task" in message_lower:
            # Extract task title from message
            task_title = ""
            if "add task" in message_lower:
                task_parts = message_lower.split("add task", 1)
                if len(task_parts) > 1:
                    task_title = task_parts[1].strip()
            elif "create task" in message_lower:
                task_parts = message_lower.split("create task", 1)
                if len(task_parts) > 1:
                    task_title = task_parts[1].strip()

            # Clean up the task title
            task_title = task_title.strip('"').strip("'").strip()

            if task_title:
                # Call add_task MCP tool
                result = TaskMCPTools.add_task(session, user_id, task_title)
                tool_calls.append({
                    "name": "add_task",
                    "arguments": {"title": task_title},
                    "result": result
                })

                if result["success"]:
                    response = f"I've created a task for you: '{result['task']['title']}'"
                else:
                    response = f"Sorry, I couldn't create the task: {result['error']}"
            else:
                response = "I need a title for the task you want to create."

        elif "show tasks" in message_lower or "list tasks" in message_lower or "my tasks" in message_lower:
            # Determine status filter
            status_filter = "all"
            if "completed" in message_lower:
                status_filter = "completed"
            elif "pending" in message_lower:
                status_filter = "pending"

            # Determine sort parameters
            sort_field = "created_at"
            sort_order = "desc"

            # Detect sort requests
            if "sort by priority" in message_lower or "by priority" in message_lower:
                sort_field = "priority"
            elif "sort by due date" in message_lower or "by due date" in message_lower or "by deadline" in message_lower:
                sort_field = "due_date"
            elif "sort by title" in message_lower or "alphabetically" in message_lower:
                sort_field = "title"
            elif "sort by creation date" in message_lower or "chronologically" in message_lower:
                sort_field = "created_at"
            elif "sort by completion" in message_lower or "by status" in message_lower:
                sort_field = "completed"

            # Detect sort order
            if "ascending" in message_lower or "oldest first" in message_lower or "lowest first" in message_lower:
                sort_order = "asc"
            elif "descending" in message_lower or "newest first" in message_lower or "highest first" in message_lower:
                sort_order = "desc"
            elif "reverse" in message_lower:
                sort_order = "desc" if sort_order == "asc" else "asc"

            # Extract other filter parameters
            priority_filter = None
            if "high priority" in message_lower or "urgent" in message_lower or "important" in message_lower:
                priority_filter = ["high"]
            elif "medium priority" in message_lower:
                priority_filter = ["medium"]
            elif "low priority" in message_lower:
                priority_filter = ["low"]
            elif "high and medium priority" in message_lower or "high or medium priority" in message_lower:
                priority_filter = ["high", "medium"]

            # Call list_tasks MCP tool with sort parameters
            result = TaskMCPTools.list_tasks(
                session,
                user_id,
                status_filter,
                priority=priority_filter,
                sort=sort_field,
                sort_order=sort_order
            )
            tool_calls.append({
                "name": "list_tasks",
                "arguments": {
                    "status": status_filter,
                    "priority": priority_filter,
                    "sort": sort_field,
                    "sort_order": sort_order
                },
                "result": result
            })

            if result["success"]:
                if result["count"] == 0:
                    response = "You don't have any tasks."
                else:
                    # Build response with sort information
                    sort_description = f"sorted by {sort_field} ({sort_order})"
                    task_list = []
                    for task in result["tasks"]:
                        priority_indicator = ""
                        if task.get("priority"):
                            priority_char = {"low": "🟢", "medium": "🟡", "high": "🔴"}[task["priority"]]
                            priority_indicator = f" {priority_char}"

                        due_date_str = ""
                        if task.get("due_date"):
                            from datetime import datetime
                            due_date = datetime.fromisoformat(task["due_date"].replace('Z', '+00:00'))
                            due_date_str = f" (due: {due_date.strftime('%b %d')})"

                        task_list.append(f"- {task['title']}{priority_indicator}{due_date_str}")

                    response = f"You have {result['count']} tasks {sort_description}:\n" + "\n".join(task_list)
            else:
                response = f"Sorry, I couldn't retrieve your tasks: {result['error']}"

        elif "complete task" in message_lower or "mark task" in message_lower:
            response = "I'd need more information to mark a specific task as complete. Please tell me which task by name or ID."

        # Handle recurring task commands
        elif any(phrase in message_lower for phrase in [
            "recurring task", "recurring", "repeat", "repeats", "repeated",
            "daily task", "weekly task", "monthly task", "yearly task",
            "every day", "every week", "every month", "every year",
            "recurrence", "recurs"
        ]):
            # Parse recurrence information from message
            recurrence_pattern = None
            due_date = None

            if any(phrase in message_lower for phrase in ["daily", "every day", "each day"]):
                recurrence_pattern = "daily"
            elif any(phrase in message_lower for phrase in ["weekly", "every week", "each week"]):
                recurrence_pattern = "weekly"
            elif any(phrase in message_lower for phrase in ["monthly", "every month", "each month"]):
                recurrence_pattern = "monthly"
            elif any(phrase in message_lower for phrase in ["yearly", "annually", "every year", "each year"]):
                recurrence_pattern = "yearly"
            elif "custom" in message_lower or "cron" in message_lower:
                recurrence_pattern = "custom"

            # Parse due date if mentioned
            import re
            date_patterns = [
                r"due\s+(\w+)\s+(\d+)",  # due Monday 15
                r"due\s+(tomorrow|today|next\s+\w+)",  # due tomorrow, due next week
                r"by\s+(\w+)\s+(\d+)",  # by Monday 15
            ]

            for pattern in date_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    # In a real implementation, we would parse the date properly
                    due_date = str(datetime.now().date())
                    break

            # Extract task title from message
            task_title = ""
            if "add recurring task" in message_lower:
                task_parts = message_lower.split("add recurring task", 1)
                if len(task_parts) > 1:
                    task_title = task_parts[1].strip()
            elif "create recurring task" in message_lower:
                task_parts = message_lower.split("create recurring task", 1)
                if len(task_parts) > 1:
                    task_title = task_parts[1].strip()
            elif "recurring task" in message_lower:
                task_parts = message_lower.split("recurring task", 1)
                if len(task_parts) > 1:
                    task_title = task_parts[1].strip()

            # Clean up the task title
            task_title = task_title.strip('"').strip("'").strip()

            if task_title and recurrence_pattern:
                # Call add_task MCP tool with recurrence information
                result = TaskMCPTools.add_task(
                    session,
                    user_id,
                    task_title,
                    recurrence_pattern=recurrence_pattern,
                    due_date=due_date
                )
                tool_calls.append({
                    "name": "add_task",
                    "arguments": {
                        "title": task_title,
                        "recurrence_pattern": recurrence_pattern,
                        "due_date": due_date
                    },
                    "result": result
                })

                if result["success"]:
                    recurrence_desc = {
                        "daily": "daily",
                        "weekly": "weekly",
                        "monthly": "monthly",
                        "yearly": "yearly",
                        "custom": "with custom pattern"
                    }.get(recurrence_pattern, "with custom pattern")

                    response = f"I've created a recurring task: '{result['task']['title']}' that repeats {recurrence_desc}"
                else:
                    response = f"Sorry, I couldn't create the recurring task: {result['error']}"
            else:
                response = "To create a recurring task, please specify a title and recurrence pattern. For example: 'Create a recurring task to water plants weekly' or 'Add a daily task to check emails'"

        elif "hello" in message_lower or "hi" in message_lower:
            response = "Hello! I'm your AI assistant. You can ask me to create, list, or manage your tasks including recurring ones and due dates."

        # Handle date/time related commands
        elif any(phrase in message_lower for phrase in [
            "due", "by", "before", "at", "on", "today", "tomorrow", "yesterday",
            "next week", "next month", "next year", "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday", "january", "february", "march",
            "april", "may", "june", "july", "august", "september", "october",
            "november", "december", "am", "pm", "morning", "evening", "afternoon"
        ]):
            # Parse date/time information from message
            import re
            from datetime import datetime, timedelta
            from dateutil.parser import parse

            # Extract date/time from message
            date_time = None
            due_phrase = ""

            # Pattern for "due tomorrow", "due next Monday", etc.
            due_pattern = r"(?:due|by|on)\s+(tomorrow|today|yesterday|next\s+\w+|\w+\s+\d{1,2}(?:st|nd|rd|th)?|\d{1,2}/\d{1,2}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2})"
            due_match = re.search(due_pattern, message_lower)
            if due_match:
                due_phrase = due_match.group(1)
                try:
                    # Parse the date expression
                    if "today" in due_phrase:
                        date_time = datetime.now()
                    elif "tomorrow" in due_phrase:
                        date_time = datetime.now() + timedelta(days=1)
                    elif "yesterday" in due_phrase:
                        date_time = datetime.now() - timedelta(days=1)
                    else:
                        # Try to parse the date using dateutil
                        date_time = parse(due_phrase)
                except:
                    # If parsing fails, try to understand the intent
                    date_time = None

            # Extract time if mentioned
            time_pattern = r"(?:at|by)\s+(\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm)|morning|afternoon|evening)"
            time_match = re.search(time_pattern, message_lower)
            time_part = None
            if time_match:
                time_str = time_match.group(1)
                if time_str in ["morning"]:
                    time_part = "09:00"
                elif time_str in ["afternoon"]:
                    time_part = "14:00"
                elif time_str in ["evening"]:
                    time_part = "18:00"
                else:
                    # Parse time expression
                    time_part = time_str

            # Extract task title if creating a task with date
            task_title = ""
            if "create" in message_lower or "add" in message_lower:
                # Extract task title from message
                if "create task" in message_lower:
                    parts = message_lower.split("create task", 1)
                    if len(parts) > 1:
                        task_title = parts[1].strip()
                elif "add task" in message_lower:
                    parts = message_lower.split("add task", 1)
                    if len(parts) > 1:
                        task_title = parts[1].strip()

                # Remove date/time phrases from title
                if due_phrase:
                    task_title = task_title.replace(f"due {due_phrase}", "").strip()
                    task_title = task_title.replace(f"by {due_phrase}", "").strip()
                if time_match:
                    task_title = task_title.replace(f"at {time_match.group(1)}", "").strip()
                    task_title = task_title.replace(f"by {time_match.group(1)}", "").strip()

            if task_title and date_time:
                # Create task with due date
                task_data = {
                    "title": task_title,
                    "due_date": date_time.isoformat()
                }

                result = TaskMCPTools.add_task(
                    session,
                    user_id,
                    task_title,
                    due_date=date_time.isoformat()
                )
                tool_calls.append({
                    "name": "add_task",
                    "arguments": task_data,
                    "result": result
                })

                if result["success"]:
                    response = f"I've created a task '{result['task']['title']}' with due date {date_time.strftime('%A, %B %d at %I:%M %p')}"
                else:
                    response = f"Sorry, I couldn't create the task: {result['error']}"
            elif date_time:
                response = f"I understood you mentioned a date/time: {date_time.strftime('%A, %B %d at %I:%M %p')}. You can create a task with a due date by saying 'create task Buy groceries due tomorrow at 3pm'"
            else:
                response = f"I recognized date/time references in your message but couldn't parse them. You can specify due dates like 'due tomorrow' or 'by January 15th at 3pm'"

        else:
            response = f"I received your message: '{message}'. You can ask me to create, list, or manage tasks including recurring ones and due dates. Try saying 'create task Buy groceries due tomorrow at 3pm' or 'list my tasks'."

        return response, tool_calls