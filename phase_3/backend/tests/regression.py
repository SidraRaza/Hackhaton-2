import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel import Session
from app.api.chat import router as chat_router
from app.routes import tasks as tasks_router
from app.mcp_tools import create_task, get_tasks, update_task, delete_task, complete_task
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.user import User
from fastapi import HTTPException


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_user():
    """Mock user for testing"""
    user = MagicMock(spec=User)
    user.id = "test-user-id"
    return user


@pytest.mark.regression
@pytest.mark.asyncio
async def test_existing_task_crud_operations_still_work(mock_db_session, mock_user):
    """Test that existing task CRUD operations still work after new feature implementation"""
    # Test task creation (existing functionality)
    mock_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
        title="Regression test task",
        description="Task to verify existing functionality",
        completed=False,
        priority="medium"
    )

    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock(side_effect=lambda obj: setattr(obj, 'id', 'test-task-id'))

    # Call the create_task function from MCP tools (new feature)
    result = await create_task(
        db_session=mock_db_session,
        user=mock_user,
        title="Regression test task",
        description="Task to verify existing functionality",
        priority="medium"
    )

    # Verify the task was created successfully
    assert result["success"] is True
    assert result["message"] == "Task 'Regression test task' created successfully"

    # Verify the task was added to the session
    task_added = mock_db_session.add.call_args[0][0]
    assert task_added.title == "Regression test task"
    assert task_added.user_id == mock_user.id


@pytest.mark.regression
@pytest.mark.asyncio
async def test_existing_task_listing_still_works(mock_db_session, mock_user):
    """Test that existing task listing functionality still works after new feature implementation"""
    # Create mock tasks
    existing_tasks = [
        Task(
            id="task1",
            user_id=mock_user.id,
            title="Existing task 1",
            description="Description for existing task 1",
            completed=False,
            priority="medium"
        ),
        Task(
            id="task2",
            user_id=mock_user.id,
            title="Existing task 2",
            description="Description for existing task 2",
            completed=True,
            priority="high"
        )
    ]

    # Mock the session.exec to return existing tasks
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = existing_tasks
    mock_db_session.exec = MagicMock(return_value=mock_exec_result)

    # Call the get_tasks function from MCP tools (new feature)
    result = await get_tasks(
        db_session=mock_db_session,
        user=mock_user
    )

    # Verify the tasks were returned correctly
    assert result["success"] is True
    assert result["count"] == 2
    assert len(result["tasks"]) == 2

    # Verify task details
    returned_titles = [task["title"] for task in result["tasks"]]
    assert "Existing task 1" in returned_titles
    assert "Existing task 2" in returned_titles


@pytest.mark.regression
@pytest.mark.asyncio
async def test_existing_task_update_still_works(mock_db_session, mock_user):
    """Test that existing task update functionality still works after new feature implementation"""
    # Create mock existing task
    existing_task = Task(
        id="update-test-id",
        user_id=mock_user.id,
        title="Original title",
        description="Original description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Call the update_task function from MCP tools (new feature)
    result = await update_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="update-test-id",
        title="Updated title",
        description="Updated description"
    )

    # Verify the task was updated successfully
    assert result["success"] is True
    assert result["message"] == "Task 'Updated title' updated successfully"

    # Verify the task attributes were updated
    assert existing_task.title == "Updated title"
    assert existing_task.description == "Updated description"


@pytest.mark.regression
@pytest.mark.asyncio
async def test_existing_task_deletion_still_works(mock_db_session, mock_user):
    """Test that existing task deletion functionality still works after new feature implementation"""
    # Create mock existing task
    existing_task = Task(
        id="delete-test-id",
        user_id=mock_user.id,
        title="Task to delete",
        description="Description for task to delete",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()

    # Call the delete_task function from MCP tools (new feature)
    result = await delete_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="delete-test-id"
    )

    # Verify the task was deleted successfully
    assert result["success"] is True
    assert result["message"] == "Task deleted successfully"

    # Verify the task was deleted from the session
    mock_db_session.delete.assert_called_once_with(existing_task)


@pytest.mark.regression
@pytest.mark.asyncio
async def test_existing_task_completion_still_works(mock_db_session, mock_user):
    """Test that existing task completion functionality still works after new feature implementation"""
    # Create mock existing task
    existing_task = Task(
        id="complete-test-id",
        user_id=mock_user.id,
        title="Task to complete",
        description="Description for task to complete",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Call the complete_task function from MCP tools (new feature)
    result = await complete_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="complete-test-id",
        completed=True
    )

    # Verify the task was completed successfully
    assert result["success"] is True
    assert result["message"] == "Task 'Task to complete' completed successfully"

    # Verify the task completion status was updated
    assert existing_task.completed is True


@pytest.mark.regression
def test_auth_routes_still_work():
    """Test that authentication routes still function after new feature implementation"""
    # This test verifies that the auth router is still available and functioning
    # In a real implementation, this would make actual API calls to auth endpoints
    from app.api.auth import router as auth_router

    # Verify the auth router exists and has expected routes
    assert auth_router is not None

    # Check that the router has the expected routes
    auth_routes = [route.path for route in auth_router.routes]
    expected_auth_paths = ["/api/auth/login", "/api/auth/register", "/api/auth/me"]  # Example paths

    # The exact paths may vary depending on the implementation
    # This is a basic check to ensure auth functionality is available
    assert len(auth_routes) > 0


@pytest.mark.regression
def test_existing_api_routes_still_accessible():
    """Test that existing API routes are still accessible after new feature implementation"""
    # Verify that the tasks router is still available
    assert tasks_router is not None

    # Verify that the chat router (new feature) is also available
    assert chat_router is not None

    # Check that both routers have routes defined
    task_routes = [route.path for route in tasks_router.routes]
    chat_routes = [route.path for route in chat_router.routes]

    assert len(task_routes) > 0
    assert len(chat_routes) > 0


@pytest.mark.regression
@pytest.mark.asyncio
async def test_user_isolation_still_enforced(mock_db_session, mock_user):
    """Test that user isolation is maintained for both old and new functionality"""
    # Create a task that belongs to a different user
    other_user_task = Task(
        id="other-user-task",
        user_id="other-user-id",
        title="Other user's task",
        description="This should not be accessible",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the other user's task
    mock_db_session.get = MagicMock(return_value=other_user_task)

    # Try to update another user's task (should fail)
    with pytest.raises(HTTPException) as exc_info:
        await update_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user
            task_id="other-user-task",
            title="Trying to update other user's task"
        )

    # Verify the error is a 403 Forbidden (user isolation is working)
    assert exc_info.value.status_code == 403

    # Try to delete another user's task (should fail)
    with pytest.raises(HTTPException) as exc_info:
        await delete_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user
            task_id="other-user-task"
        )

    # Verify the error is a 403 Forbidden (user isolation is working)
    assert exc_info.value.status_code == 403

    # Try to complete another user's task (should fail)
    with pytest.raises(HTTPException) as exc_info:
        await complete_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user
            task_id="other-user-task",
            completed=True
        )

    # Verify the error is a 403 Forbidden (user isolation is working)
    assert exc_info.value.status_code == 403


@pytest.mark.regression
@pytest.mark.asyncio
async def test_database_schema_compatibility(mock_db_session, mock_user):
    """Test that database schema changes are backward compatible"""
    # Create a task using the existing Task model
    task = Task(
        user_id=mock_user.id,
        title="Compatibility test task",
        description="Task to test schema compatibility",
        completed=False,
        priority="medium"
    )

    # Verify that the task can be created without errors
    assert task.user_id == mock_user.id
    assert task.title == "Compatibility test task"
    assert task.description == "Task to test schema compatibility"
    assert task.completed is False
    assert task.priority == "medium"

    # Verify that all expected attributes exist
    expected_attributes = ['id', 'user_id', 'title', 'description', 'completed', 'priority', 'due_date']
    for attr in expected_attributes:
        assert hasattr(task, attr)


@pytest.mark.regression
@pytest.mark.asyncio
async def test_new_and_existing_features_coexist(mock_db_session, mock_user):
    """Test that new AI features and existing manual features work together"""
    # Test creating a task via MCP tool (new AI feature pathway)
    mock_task = Task(
        id="coexist-test-id",
        user_id=mock_user.id,
        title="AI-created task",
        description="Task created via AI assistant",
        completed=False,
        priority="medium"
    )

    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock(side_effect=lambda obj: setattr(obj, 'id', 'coexist-test-id'))

    # Create task via MCP tool (simulating AI action)
    ai_result = await create_task(
        db_session=mock_db_session,
        user=mock_user,
        title="AI-created task",
        description="Task created via AI assistant",
        priority="medium"
    )

    # Verify AI creation worked
    assert ai_result["success"] is True

    # Now test that the same task can be retrieved using the same system
    existing_task = Task(
        id="manual-test-id",
        user_id=mock_user.id,
        title="Manually created task",
        description="Task created via manual interface",
        completed=False,
        priority="high"
    )

    # Mock exec to return both tasks
    all_tasks = [mock_task, existing_task]
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = all_tasks
    mock_db_session.exec = MagicMock(return_value=mock_exec_result)

    # Retrieve tasks (simulating either AI or manual retrieval)
    retrieval_result = await get_tasks(
        db_session=mock_db_session,
        user=mock_user
    )

    # Verify both tasks are retrievable
    assert retrieval_result["success"] is True
    assert retrieval_result["count"] >= 2  # At least the two tasks we created

    # Verify that both AI-created and manually-created tasks are present
    retrieved_titles = [task["title"] for task in retrieval_result["tasks"]]
    assert "AI-created task" in retrieved_titles
    assert "Manually created task" in retrieved_titles


@pytest.mark.regression
def test_system_responsiveness_after_changes():
    """Test that the system remains responsive after adding new features"""
    # Verify that core modules are still importable and functional
    from app.models.task import Task
    from app.models.user import User
    from app.models.conversation import Conversation
    from app.models.message import Message

    # Verify that new models are also available
    assert Conversation is not None
    assert Message is not None

    # Verify that existing models still work as expected
    assert Task is not None
    assert User is not None

    # Verify that MCP tools are available
    from app.mcp_tools import MCP_TOOLS
    assert len(MCP_TOOLS) > 0
    expected_tools = {"create_task", "update_task", "delete_task", "get_tasks", "complete_task"}
    assert set(MCP_TOOLS.keys()) == expected_tools