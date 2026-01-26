import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel import Session, select
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


@pytest.mark.asyncio
async def test_create_task_success(mock_db_session, mock_user):
    """Test successful task creation"""
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
    assert "task_id" in result

    # Verify session methods were called
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_task_success(mock_db_session, mock_user):
    """Test successful task update"""
    # Mock existing task
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
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
        title="New Title",
        description="New Description"
    )

    # Assertions
    assert result["success"] is True
    assert result["message"] == "Task 'New Title' updated successfully"

    # Verify session methods were called
    mock_db_session.get.assert_called_once_with(Task, "test-task-id")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_task_unauthorized(mock_db_session, mock_user):
    """Test updating a task owned by another user (should fail)"""
    # Mock existing task owned by different user
    existing_task = Task(
        id="test-task-id",
        user_id="different-user-id",
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)

    # Call the function and expect an exception
    with pytest.raises(Exception):  # Should raise HTTPException
        await update_task(
            db_session=mock_db_session,
            user=mock_user,
            task_id="test-task-id",
            title="New Title"
        )


@pytest.mark.asyncio
async def test_delete_task_success(mock_db_session, mock_user):
    """Test successful task deletion"""
    # Mock existing task
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
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

    # Verify session methods were called
    mock_db_session.get.assert_called_once_with(Task, "test-task-id")
    mock_db_session.delete.assert_called_once_with(existing_task)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_tasks_success(mock_db_session, mock_user):
    """Test successful task retrieval"""
    # Mock tasks
    mock_tasks = [
        Task(
            id="task1",
            user_id=mock_user.id,
            title="Task 1",
            description="Description 1",
            completed=False,
            priority="medium"
        ),
        Task(
            id="task2",
            user_id=mock_user.id,
            title="Task 2",
            description="Description 2",
            completed=True,
            priority="high"
        )
    ]

    # Mock exec to return the tasks
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = mock_tasks
    mock_db_session.exec = MagicMock(return_value=mock_exec_result)

    # Call the function
    result = await get_tasks(
        db_session=mock_db_session,
        user=mock_user
    )

    # Assertions
    assert result["success"] is True
    assert result["count"] == 2
    assert len(result["tasks"]) == 2


@pytest.mark.asyncio
async def test_complete_task_success(mock_db_session, mock_user):
    """Test successful task completion"""
    # Mock existing task
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
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

    # Verify session methods were called
    mock_db_session.get.assert_called_once_with(Task, "test-task-id")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_complete_task_unauthorized(mock_db_session, mock_user):
    """Test completing a task owned by another user (should fail)"""
    # Mock existing task owned by different user
    existing_task = Task(
        id="test-task-id",
        user_id="different-user-id",
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)

    # Call the function and expect an exception
    with pytest.raises(Exception):  # Should raise HTTPException
        await complete_task(
            db_session=mock_db_session,
            user=mock_user,
            task_id="test-task-id",
            completed=True
        )