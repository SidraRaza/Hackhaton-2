"""Search service for natural language task search and filtering"""

from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy import text
from datetime import datetime
from dateutil.parser import parse

from models import Task
from services.task_service import TaskService


class SearchService:
    """Service for handling natural language search and advanced filtering"""

    @staticmethod
    def search_tasks_with_filters(
        session: Session,
        user_id: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search tasks with natural language query and advanced filters

        Args:
            session: Database session
            user_id: User ID for authorization
            query: Natural language search query
            filters: Additional filters to apply

        Returns:
            List of search results with task objects and relevance scores
        """
        if not query and not filters:
            # If no query and no filters, return all tasks
            return TaskService.get_tasks_by_user(session, user_id)

        # Prepare base statement
        statement = select(Task).where(Task.user_id == user_id)

        # Apply filters if provided
        if filters:
            # Priority filter
            if filters.get("priority"):
                priorities = filters["priority"]
                if isinstance(priorities, list):
                    statement = statement.where(Task.priority.in_(priorities))
                else:
                    statement = statement.where(Task.priority == priorities)

            # Status filter
            if filters.get("status") and filters["status"] != "all":
                if filters["status"] == "pending":
                    statement = statement.where(Task.completed == False)
                elif filters["status"] == "completed":
                    statement = statement.where(Task.completed == True)

            # Due date filters
            if filters.get("due_date_from"):
                due_from = filters["due_date_from"]
                if isinstance(due_from, str):
                    due_from = parse(due_from)
                statement = statement.where(Task.due_date >= due_from)

            if filters.get("due_date_to"):
                due_to = filters["due_date_to"]
                if isinstance(due_to, str):
                    due_to = parse(due_to)
                statement = statement.where(Task.due_date <= due_to)

            # Recurrence pattern filter
            if filters.get("recurrence_pattern"):
                statement = statement.where(Task.recurrence_pattern == filters["recurrence_pattern"])

        # Apply search if provided
        if query:
            # Use PostgreSQL full-text search if available, otherwise LIKE
            try:
                # Try full-text search first
                statement = statement.where(
                    text("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')) @@ plainto_tsquery('english', :search_term)")
                ).bindparam(search_term=query)
            except:
                # Fallback to basic LIKE search
                statement = statement.where(
                    (Task.title.ilike(f"%{query}%")) |
                    (Task.description.is_not(None) & Task.description.ilike(f"%{query}%"))
                )

        # Apply sorting
        sort_field = filters.get("sort", "created_at")
        sort_order = filters.get("sort_order", "desc")

        if sort_field == "relevance" and query:
            # If sorting by relevance and we have a query, use ts_rank
            try:
                statement = statement.order_by(
                    text("ts_rank(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')), plainto_tsquery('english', :search_term)) DESC")
                ).bindparam(search_term=query)
            except:
                # Fallback to created_at sort
                if sort_order == "desc":
                    statement = statement.order_by(Task.created_at.desc())
                else:
                    statement = statement.order_by(Task.created_at.asc())
        elif sort_field == "priority":
            if sort_order == "desc":
                statement = statement.order_by(Task.priority.desc())
            else:
                statement = statement.order_by(Task.priority.asc())
        elif sort_field == "due_date":
            if sort_order == "desc":
                statement = statement.order_by(Task.due_date.desc())
            else:
                statement = statement.order_by(Task.due_date.asc())
        elif sort_field == "title":
            if sort_order == "desc":
                statement = statement.order_by(Task.title.desc())
            else:
                statement = statement.order_by(Task.title.asc())
        elif sort_field == "completed":
            if sort_order == "desc":
                statement = statement.order_by(Task.completed.desc())
            else:
                statement = statement.order_by(Task.completed.asc())
        else:  # Default to created_at
            if sort_order == "desc":
                statement = statement.order_by(Task.created_at.desc())
            else:
                statement = statement.order_by(Task.created_at.asc())

        # Apply limit
        limit = filters.get("limit", 50)
        statement = statement.limit(limit)

        tasks = session.exec(statement).all()

        # Create results with relevance scores
        results = []
        for task in tasks:
            result = {
                "task": task,
                "relevance_score": 0.5  # Default score if no actual ranking available
            }
            results.append(result)

        return results

    @staticmethod
    def parse_natural_language_query(query: str) -> Dict[str, Any]:
        """
        Parse natural language query to extract search terms and filters

        Args:
            query: Natural language query string

        Returns:
            Dictionary with parsed search terms and extracted filters
        """
        import re

        parsed_result = {
            "search_terms": [],
            "filters": {}
        }

        query_lower = query.lower()

        # Extract priority mentions
        priority_patterns = {
            "high": [r"high priority", r"urgent", r"critical", r"asap", r"important"],
            "medium": [r"medium priority", r"normal", r"regular", r"standard"],
            "low": [r"low priority", r"not urgent", r"later", r"whenever"]
        }

        for priority, patterns in priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    if "priority" not in parsed_result["filters"]:
                        parsed_result["filters"]["priority"] = []
                    if priority not in parsed_result["filters"]["priority"]:
                        parsed_result["filters"]["priority"].append(priority)

        # Extract date mentions
        date_patterns = [
            r"due (today|tomorrow)",
            r"due (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"due in \d+ days?",
            r"due in \d+ weeks?",
            r"due in \d+ months?",
            r"due by .*",
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                # In a real implementation, we would parse these dates properly
                # For now, we'll just note that dates were mentioned
                parsed_result["filters"]["date_mentioned"] = True

        # Extract tag mentions
        tag_pattern = r"(?:tag|with) ([a-zA-Z0-9_-]+)"
        tag_matches = re.findall(tag_pattern, query_lower)
        if tag_matches:
            parsed_result["filters"]["tags"] = tag_matches

        # Extract status mentions
        if "completed" in query_lower or "done" in query_lower:
            parsed_result["filters"]["status"] = "completed"
        elif "pending" in query_lower or "not done" in query_lower:
            parsed_result["filters"]["status"] = "pending"

        # Extract the main search terms (remove filter-related terms)
        clean_query = query
        for priority, patterns in priority_patterns.items():
            for pattern in patterns:
                clean_query = re.sub(pattern, '', clean_query, flags=re.IGNORECASE)

        for date_pattern in date_patterns:
            clean_query = re.sub(date_pattern, '', clean_query, flags=re.IGNORECASE)

        clean_query = re.sub(tag_pattern, '', clean_query, flags=re.IGNORECASE)

        # Clean up extra whitespace and extract remaining search terms
        clean_query = re.sub(r'\s+', ' ', clean_query.strip())
        parsed_result["search_terms"] = [term.strip() for term in clean_query.split() if len(term.strip()) > 2]

        return parsed_result

    @staticmethod
    def advanced_search(
        session: Session,
        user_id: str,
        natural_query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform advanced search with natural language understanding

        Args:
            session: Database session
            user_id: User ID for authorization
            natural_query: Natural language search query
            filters: Additional filters to apply

        Returns:
            List of search results with task objects and relevance scores
        """
        # Parse natural language query
        parsed_query = SearchService.parse_natural_language_query(natural_query)

        # Merge parsed filters with provided filters
        merged_filters = filters if filters else {}
        for key, value in parsed_query["filters"].items():
            if key not in merged_filters:
                merged_filters[key] = value

        # Use the parsed search terms as the main query
        search_terms = " ".join(parsed_query["search_terms"])

        # Perform search with merged filters
        return SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query=search_terms,
            filters=merged_filters
        )

    @staticmethod
    def get_search_suggestions(
        session: Session,
        user_id: str,
        partial_query: str
    ) -> List[str]:
        """
        Get search suggestions based on partial query and user's task history

        Args:
            session: Database session
            user_id: User ID for authorization
            partial_query: Partial search query

        Returns:
            List of search suggestions
        """
        # Get tasks that match the partial query
        statement = select(Task).where(
            Task.user_id == user_id
        ).where(
            (Task.title.ilike(f"%{partial_query}%")) |
            (Task.description.is_not(None) & Task.description.ilike(f"%{partial_query}%"))
        ).limit(10)

        tasks = session.exec(statement).all()

        suggestions = set()
        for task in tasks:
            if task.title and partial_query.lower() in task.title.lower():
                suggestions.add(task.title)
            if task.description and partial_query.lower() in task.description.lower():
                # Add relevant phrases from description
                import re
                phrases = re.findall(rf"[^\.]*{re.escape(partial_query)}[^\.]*\.",
                                    task.description or "", re.IGNORECASE)
                for phrase in phrases[:3]:  # Take first 3 phrases
                    suggestions.add(phrase.strip().rstrip('.'))

        return list(suggestions)[:5]  # Return top 5 suggestions