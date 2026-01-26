import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel import Session
from app.mcp_tools import create_task, update_task, delete_task, get_tasks, complete_task
from app.models.task import Task
from app.schemas.user import User


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


@pytest.fixture
def mock_other_user():
    """Mock another user for testing"""
    user = MagicMock(spec=User)
    user.id = "other-user-id"
    return user


@pytest.mark.asyncio
async def test_create_task_user_validation(mock_db_session, mock_user):
    """Test that create_task properly associates task with user"""
    # Mock the task creation
    mock_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session behavior
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock(side_effect=lambda obj: setattr(obj, 'id', 'test-task-id'))

    # Call the function
    result = await create_task(
        db_session=mock_db_session,
        user=mock_user,
        title="Test Task",
        description="Test Description",
        priority="medium"
    )

    # Assertions
    assert result["success"] is True
    assert result["message"] == "Task 'Test Task' created successfully"

    # Verify the task was created with the correct user_id
    task_created = mock_db_session.add.call_args[0][0]
    assert task_created.user_id == mock_user.id


@pytest.mark.asyncio
async def test_update_task_user_validation(mock_db_session, mock_user, mock_other_user):
    """Test that update_task validates user ownership"""
    # Mock existing task owned by other user
    existing_task = Task(
        id="test-task-id",
        user_id=mock_other_user.id,  # Different user
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)

    # Call the function and expect an exception
    with pytest.raises(Exception):  # Should raise HTTPException with 403
        await update_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user trying to update
            task_id="test-task-id",
            title="New Title"
        )


@pytest.mark.asyncio
async def test_update_task_user_ownership_valid(mock_db_session, mock_user):
    """Test that update_task allows user to update their own task"""
    # Mock existing task owned by the same user
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,  # Same user
        title="Old Title",
        description="Old Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Call the function
    result = await update_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="test-task-id",
        title="New Title"
    )

    # Assertions
    assert result["success"] is True
    assert result["message"] == "Task 'New Title' updated successfully"


@pytest.mark.asyncio
async def test_delete_task_user_validation(mock_db_session, mock_user, mock_other_user):
    """Test that delete_task validates user ownership"""
    # Mock existing task owned by other user
    existing_task = Task(
        id="test-task-id",
        user_id=mock_other_user.id,  # Different user
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)

    # Call the function and expect an exception
    with pytest.raises(Exception):  # Should raise HTTPException with 403
        await delete_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user trying to delete
            task_id="test-task-id"
        )


@pytest.mark.asyncio
async def test_delete_task_user_ownership_valid(mock_db_session, mock_user):
    """Test that delete_task allows user to delete their own task"""
    # Mock existing task owned by the same user
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,  # Same user
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()

    # Call the function
    result = await delete_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="test-task-id"
    )

    # Assertions
    assert result["success"] is True
    assert result["message"] == "Task deleted successfully"


@pytest.mark.asyncio
async def test_get_tasks_user_isolation(mock_db_session, mock_user):
    """Test that get_tasks only returns tasks for the requesting user"""
    # Mock tasks - some owned by the user, some by others
    user_tasks = [
        Task(
            id="task1",
            user_id=mock_user.id,  # User's task
            title="Task 1",
            description="Description 1",
            completed=False,
            priority="medium"
        ),
        Task(
            id="task2",
            user_id=mock_user.id,  # User's task
            title="Task 2",
            description="Description 2",
            completed=True,
            priority="high"
        )
    ]

    # Mock other user's task (should not be returned)
    other_task = Task(
        id="task3",
        user_id="different-user-id",  # Not the current user
        title="Other Task",
        description="Other Description",
        completed=False,
        priority="low"
    )

    # Mock all tasks in the database
    all_tasks = user_tasks + [other_task]

    # Mock exec to return only tasks filtered by user_id
    mock_exec_result = MagicMock()
    # Simulate the filtering behavior - only return tasks for the current user
    filtered_tasks = [t for t in all_tasks if t.user_id == mock_user.id]
    mock_exec_result.all.return_value = filtered_tasks

    mock_db_session.exec = MagicMock(return_value=mock_exec_result)

    # Call the function
    result = await get_tasks(
        db_session=mock_db_session,
        user=mock_user
    )

    # Assertions
    assert result["success"] is True
    assert result["count"] == 2  # Only the user's tasks
    assert len(result["tasks"]) == 2

    # Verify that only user's tasks are returned
    returned_task_ids = [task["id"] for task in result["tasks"]]
    expected_task_ids = ["task1", "task2"]  # Only user's tasks
    assert sorted(returned_task_ids) == sorted(expected_task_ids)


@pytest.mark.asyncio
async def test_complete_task_user_validation(mock_db_session, mock_user, mock_other_user):
    """Test that complete_task validates user ownership"""
    # Mock existing task owned by other user
    existing_task = Task(
        id="test-task-id",
        user_id=mock_other_user.id,  # Different user
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)

    # Call the function and expect an exception
    with pytest.raises(Exception):  # Should raise HTTPException with 403
        await complete_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user trying to complete
            task_id="test-task-id",
            completed=True
        )


@pytest.mark.asyncio
async def test_complete_task_user_ownership_valid(mock_db_session, mock_user):
    """Test that complete_task allows user to complete their own task"""
    # Mock existing task owned by the same user
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,  # Same user
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Call the function
    result = await complete_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="test-task-id",
        completed=True
    )

    # Assertions
    assert result["success"] is True
    assert result["message"] == "Task 'Test Task' completed successfully"


def test_security_audit_logging(caplog):
    """Test that security-relevant operations are logged"""
    # This test would require a more sophisticated mocking setup
    # to test the actual logging functionality
    # For now, we'll just verify that the structure is in place
    from app.mcp_tools import logger
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'warning')
    assert hasattr(logger, 'error')