import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from models import Task, Tag, TaskTag, PriorityEnum
from services.search_service import SearchService
from services.task_service import TaskService


@pytest.fixture(name="engine")
def fixture_engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create a test session"""
    with Session(engine) as session:
        yield session


class TestSearchService:
    """Unit tests for SearchService functionality"""

    def test_search_tasks_with_empty_query_and_filters(self, session):
        """Test searching with empty query but with filters"""
        user_id = "test-user-123"

        # Create test tasks with different priorities
        tasks = [
            Task(user_id=user_id, title="Low Priority Task", priority=PriorityEnum.low),
            Task(user_id=user_id, title="High Priority Task", priority=PriorityEnum.high),
            Task(user_id=user_id, title="Medium Priority Task", priority=PriorityEnum.medium)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test with no query but with priority filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query=None,
            filters={"priority": ["high"]}
        )

        assert len(results) == 1
        assert results[0]["task"].title == "High Priority Task"

    def test_search_tasks_with_priority_filter(self, session):
        """Test searching tasks with priority filter"""
        user_id = "test-user-123"

        # Create tasks with different priorities
        tasks = [
            Task(user_id=user_id, title="Low Priority Task", priority=PriorityEnum.low),
            Task(user_id=user_id, title="High Priority Task", priority=PriorityEnum.high),
            Task(user_id=user_id, title="High Priority Task 2", priority=PriorityEnum.high),
            Task(user_id=user_id, title="Medium Priority Task", priority=PriorityEnum.medium)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test single priority filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"priority": ["high"]}
        )

        assert len(results) == 2
        titles = [result["task"].title for result in results]
        assert "High Priority Task" in titles
        assert "High Priority Task 2" in titles
        assert "Low Priority Task" not in titles

        # Test multiple priority filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"priority": ["high", "low"]}
        )

        assert len(results) == 3
        titles = [result["task"].title for result in results]
        assert "High Priority Task" in titles
        assert "High Priority Task 2" in titles
        assert "Low Priority Task" in titles
        assert "Medium Priority Task" not in titles

    def test_search_tasks_with_status_filter(self, session):
        """Test searching tasks with status filter"""
        user_id = "test-user-123"

        # Create tasks with different completion statuses
        tasks = [
            Task(user_id=user_id, title="Pending Task 1", completed=False),
            Task(user_id=user_id, title="Pending Task 2", completed=False),
            Task(user_id=user_id, title="Completed Task", completed=True)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test pending filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"status": "pending"}
        )

        assert len(results) == 2
        titles = [result["task"].title for result in results]
        assert "Pending Task 1" in titles
        assert "Pending Task 2" in titles
        assert "Completed Task" not in titles

        # Test completed filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"status": "completed"}
        )

        assert len(results) == 1
        assert results[0]["task"].title == "Completed Task"

        # Test all filter (should return all tasks)
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"status": "all"}
        )

        assert len(results) == 3

    def test_search_tasks_with_due_date_filter(self, session):
        """Test searching tasks with due date filters"""
        user_id = "test-user-123"

        # Create tasks with different due dates
        future_date = datetime.utcnow() + timedelta(days=5)
        past_date = datetime.utcnow() - timedelta(days=2)
        far_future_date = datetime.utcnow() + timedelta(days=10)

        tasks = [
            Task(user_id=user_id, title="Future Task", due_date=future_date),
            Task(user_id=user_id, title="Past Task", due_date=past_date),
            Task(user_id=user_id, title="Far Future Task", due_date=far_future_date),
            Task(user_id=user_id, title="No Due Date Task", due_date=None)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test due date from filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"due_date_from": datetime.utcnow()}
        )

        assert len(results) == 2  # Future and Far Future tasks
        titles = [result["task"].title for result in results]
        assert "Future Task" in titles
        assert "Far Future Task" in titles
        assert "Past Task" not in titles

        # Test due date to filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"due_date_to": datetime.utcnow()}
        )

        assert len(results) == 2  # Past Task and No Due Date Task
        titles = [result["task"].title for result in results]
        assert "Past Task" in titles
        assert "No Due Date Task" in titles

    def test_search_tasks_with_recurrence_filter(self, session):
        """Test searching tasks with recurrence pattern filter"""
        user_id = "test-user-123"

        # Create tasks with different recurrence patterns
        tasks = [
            Task(user_id=user_id, title="Daily Recurring Task", recurrence_pattern="daily"),
            Task(user_id=user_id, title="Weekly Recurring Task", recurrence_pattern="weekly"),
            Task(user_id=user_id, title="Non-Recurring Task", recurrence_pattern=None)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test recurrence pattern filter
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="",
            filters={"recurrence_pattern": "daily"}
        )

        assert len(results) == 1
        assert results[0]["task"].title == "Daily Recurring Task"

    def test_search_tasks_with_text_query(self, session):
        """Test searching tasks with text query"""
        user_id = "test-user-123"

        # Create tasks with different content
        tasks = [
            Task(user_id=user_id, title="Meeting with team", description="Discuss project progress"),
            Task(user_id=user_id, title="Buy groceries", description="Milk, eggs, bread"),
            Task(user_id=user_id, title="Team meeting", description="Weekly standup meeting")
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test search in title
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="meeting",
            filters={}
        )

        assert len(results) == 2  # "Meeting with team" and "Team meeting"
        titles = [result["task"].title for result in results]
        assert "Meeting with team" in titles
        assert "Team meeting" in titles

        # Test search in description
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="project",
            filters={}
        )

        assert len(results) == 1
        assert results[0]["task"].title == "Meeting with team"

    def test_search_tasks_with_combined_filters(self, session):
        """Test searching tasks with multiple filters combined"""
        user_id = "test-user-123"

        # Create tasks with various attributes
        tasks = [
            Task(user_id=user_id, title="High Priority Meeting", priority=PriorityEnum.high, completed=False),
            Task(user_id=user_id, title="Low Priority Shopping", priority=PriorityEnum.low, completed=False),
            Task(user_id=user_id, title="High Priority Completed Task", priority=PriorityEnum.high, completed=True),
            Task(user_id=user_id, title="Medium Priority Meeting", priority=PriorityEnum.medium, completed=False)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test combining priority and status filters
        results = SearchService.search_tasks_with_filters(
            session=session,
            user_id=user_id,
            query="meeting",
            filters={
                "priority": ["high"],
                "status": "pending"
            }
        )

        assert len(results) == 1
        assert results[0]["task"].title == "High Priority Meeting"

    def test_parse_natural_language_query_priority(self):
        """Test parsing natural language queries for priority mentions"""
        # Test high priority mentions
        result = SearchService.parse_natural_language_query("I need a high priority task")
        assert "high" in result["filters"]["priority"]

        # Test urgent priority mentions
        result = SearchService.parse_natural_language_query("This is urgent and important")
        assert "high" in result["filters"]["priority"]

        # Test low priority mentions
        result = SearchService.parse_natural_language_query("This is not urgent, do it later")
        assert "low" in result["filters"]["priority"]

        # Test multiple priority mentions
        result = SearchService.parse_natural_language_query("This is high priority and urgent")
        assert "high" in result["filters"]["priority"]

    def test_parse_natural_language_query_status(self):
        """Test parsing natural language queries for status mentions"""
        # Test completed status mentions
        result = SearchService.parse_natural_language_query("Show me completed tasks")
        assert result["filters"]["status"] == "completed"

        result = SearchService.parse_natural_language_query("Find done tasks")
        assert result["filters"]["status"] == "completed"

        # Test pending status mentions
        result = SearchService.parse_natural_language_query("Show me pending tasks")
        assert result["filters"]["status"] == "pending"

        result = SearchService.parse_natural_language_query("Find tasks that are not done")
        assert result["filters"]["status"] == "pending"

    def test_parse_natural_language_query_dates(self):
        """Test parsing natural language queries for date mentions"""
        # Test date mentions are detected
        result = SearchService.parse_natural_language_query("Task due today")
        assert result["filters"]["date_mentioned"] is True

        result = SearchService.parse_natural_language_query("Task due tomorrow")
        assert result["filters"]["date_mentioned"] is True

        result = SearchService.parse_natural_language_query("Task due next Monday")
        assert result["filters"]["date_mentioned"] is True

    def test_advanced_search_with_natural_query(self, session):
        """Test advanced search with natural language query"""
        user_id = "test-user-123"

        # Create test tasks
        tasks = [
            Task(user_id=user_id, title="Urgent team meeting", priority=PriorityEnum.high),
            Task(user_id=user_id, title="Regular grocery shopping", priority=PriorityEnum.medium),
            Task(user_id=user_id, title="Low priority reading", priority=PriorityEnum.low, completed=True)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test natural language search
        results = SearchService.advanced_search(
            session=session,
            user_id=user_id,
            natural_query="urgent tasks",
            filters={}
        )

        # Should find the high priority task
        assert len(results) >= 1
        found_urgent = any("urgent" in result["task"].title.lower() or
                          result["task"].priority == PriorityEnum.high for result in results)
        assert found_urgent

    def test_get_search_suggestions(self, session):
        """Test getting search suggestions"""
        user_id = "test-user-123"

        # Create tasks with different content
        tasks = [
            Task(user_id=user_id, title="Team meeting with John", description="Weekly team sync"),
            Task(user_id=user_id, title="Grocery shopping", description="Buy milk and eggs"),
            Task(user_id=user_id, title="Project meeting", description="Discuss project timeline")
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test getting suggestions for "meet"
        suggestions = SearchService.get_search_suggestions(
            session=session,
            user_id=user_id,
            partial_query="meet"
        )

        assert len(suggestions) > 0
        # Should include tasks with "meeting" in title
        assert any("meeting" in suggestion.lower() for suggestion in suggestions)


class TestTaskServiceWithFilters:
    """Test TaskService with filter functionality"""

    def test_get_tasks_by_user_with_filters(self, session):
        """Test getting tasks with filters"""
        user_id = "test-user-123"

        # Create test tasks
        tasks = [
            Task(user_id=user_id, title="High Priority Task", priority=PriorityEnum.high, completed=False),
            Task(user_id=user_id, title="Low Priority Task", priority=PriorityEnum.low, completed=True),
            Task(user_id=user_id, title="Medium Priority Task", priority=PriorityEnum.medium, completed=False)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test with filters
        filters = {
            "priority": ["high"],
            "status": "pending"
        }

        filtered_tasks = TaskService.get_tasks_by_user(session, user_id, filters)

        # Should only return high priority pending tasks
        assert len(filtered_tasks) == 1
        assert filtered_tasks[0].priority == PriorityEnum.high
        assert filtered_tasks[0].completed is False

    def test_get_tasks_by_user_with_multiple_filters(self, session):
        """Test getting tasks with multiple filters"""
        user_id = "test-user-123"

        # Create tags
        tag_work = Tag(user_id=user_id, name="work", color="#3B82F6")
        tag_personal = Tag(user_id=user_id, name="personal", color="#EF4444")
        session.add_all([tag_work, tag_personal])
        session.commit()

        # Create tasks
        task1 = Task(user_id=user_id, title="High Priority Work Task", priority=PriorityEnum.high, completed=False)
        task2 = Task(user_id=user_id, title="Low Priority Personal Task", priority=PriorityEnum.low, completed=True)
        task3 = Task(user_id=user_id, title="Medium Priority Work Task", priority=PriorityEnum.medium, completed=False)

        session.add_all([task1, task2, task3])
        session.commit()

        # Associate tasks with tags
        task_tag1 = TaskTag(task_id=task1.id, tag_id=tag_work.id)
        task_tag2 = TaskTag(task_id=task2.id, tag_id=tag_personal.id)
        task_tag3 = TaskTag(task_id=task3.id, tag_id=tag_work.id)

        session.add_all([task_tag1, task_tag2, task_tag3])
        session.commit()

        # Test with multiple filters
        filters = {
            "priority": ["high", "medium"],
            "status": "pending",
            "tags": [tag_work.id]
        }

        filtered_tasks = TaskService.get_tasks_by_user(session, user_id, filters)

        # Should return high and medium priority pending tasks with work tag
        assert len(filtered_tasks) == 2
        for task in filtered_tasks:
            assert task.priority in [PriorityEnum.high, PriorityEnum.medium]
            assert task.completed is False


class TestIntegrationSearchFilter:
    """Integration tests for search and filter functionality"""

    def test_full_text_search_integration(self, session):
        """Test full text search integration with all components"""
        user_id = "test-user-123"

        # Create a task with rich content
        task = Task(
            user_id=user_id,
            title="Urgent Project Meeting",
            description="Need to discuss the critical project timeline with stakeholders",
            priority=PriorityEnum.high,
            completed=False
        )

        session.add(task)
        session.commit()

        # Test searching with various terms
        search_terms = ["urgent", "project", "meeting", "critical", "timeline"]

        for term in search_terms:
            results = SearchService.search_tasks_with_filters(
                session=session,
                user_id=user_id,
                query=term,
                filters={}
            )

            assert len(results) >= 1
            assert any(term.lower() in result["task"].title.lower() or
                      (result["task"].description and term.lower() in result["task"].description.lower())
                      for result in results)

    def test_filter_persistence_integration(self, session):
        """Test filter persistence functionality"""
        from services.preference_service import PreferenceService

        user_id = "test-user-123"

        # Set up some saved filters for the user
        filter_updates = {
            "priority": ["high"],
            "status": "pending",
            "sort": "priority"
        }

        saved_filters = PreferenceService.update_task_filter_preferences(
            session, user_id, filter_updates
        )

        # Verify the filters were saved
        retrieved_filters = PreferenceService.get_task_filter_preferences(session, user_id)
        assert retrieved_filters["priority"] == ["high"]
        assert retrieved_filters["status"] == "pending"
        assert retrieved_filters["sort"] == "priority"

    def test_natural_language_search_integration(self, session):
        """Test natural language search end-to-end"""
        user_id = "test-user-123"

        # Create tasks with different characteristics
        tasks = [
            Task(user_id=user_id, title="Urgent client meeting", priority=PriorityEnum.high, completed=False),
            Task(user_id=user_id, title="Weekly team sync", priority=PriorityEnum.medium, completed=False),
            Task(user_id=user_id, title="Personal reading", priority=PriorityEnum.low, completed=True)
        ]

        for task in tasks:
            session.add(task)
        session.commit()

        # Test advanced search with natural language
        results = SearchService.advanced_search(
            session=session,
            user_id=user_id,
            natural_query="urgent meeting",
            filters={}
        )

        # Should find the high priority task that matches "meeting"
        assert len(results) >= 1
        found_task = results[0]["task"]
        assert PriorityEnum.high in [found_task.priority] or "meeting" in found_task.title.lower()


def test_search_performance_large_dataset():
    """Performance test for search functionality with larger dataset"""
    # This would be implemented in a real scenario with performance metrics
    pass


def test_search_edge_cases():
    """Test edge cases for search functionality"""
    # Test empty query
    assert SearchService.parse_natural_language_query("")["search_terms"] == []

    # Test query with only filter terms
    result = SearchService.parse_natural_language_query("high priority urgent")
    # Should have filters but potentially empty or minimal search terms
    assert "priority" in result["filters"]


if __name__ == "__main__":
    pytest.main([__file__])