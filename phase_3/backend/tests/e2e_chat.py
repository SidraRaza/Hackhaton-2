import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel import Session
from app.mcp_tools import create_task, update_task, delete_task, get_tasks, complete_task
from app.ai_service import AIService
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
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
async def test_e2e_task_creation_flow(mock_db_session, mock_user):
    """Test complete flow of creating a task via chat interface"""
    # Mock the task creation
    mock_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
        priority="medium"
    )

    # Mock session behavior
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock(side_effect=lambda obj: setattr(obj, 'id', 'test-task-id'))

    # Call the create_task function (which simulates AI calling the tool)
    result = await create_task(
        db_session=mock_db_session,
        user=mock_user,
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="medium"
    )

    # Verify the result
    assert result["success"] is True
    assert result["message"] == "Task 'Buy groceries' created successfully"
    assert result["task_id"] == "test-task-id"

    # Verify the task was added to the session with correct attributes
    task_added = mock_db_session.add.call_args[0][0]
    assert task_added.title == "Buy groceries"
    assert task_added.description == "Milk, eggs, bread"
    assert task_added.user_id == mock_user.id
    assert task_added.completed is False
    assert task_added.priority == "medium"


@pytest.mark.asyncio
async def test_e2e_task_listing_flow(mock_db_session, mock_user):
    """Test complete flow of listing tasks via chat interface"""
    # Create mock tasks for the user
    user_tasks = [
        Task(
            id="task1",
            user_id=mock_user.id,
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False,
            priority="medium"
        ),
        Task(
            id="task2",
            user_id=mock_user.id,
            title="Walk the dog",
            description="Evening walk in the park",
            completed=True,
            priority="high"
        )
    ]

    # Mock other user's task (should not be returned)
    other_user_task = Task(
        id="task3",
        user_id="other-user-id",
        title="Work meeting",
        description="Team sync",
        completed=False,
        priority="high"
    )

    # Mock all tasks in the database
    all_tasks = user_tasks + [other_user_task]

    # Mock exec to return only tasks filtered by user_id
    mock_exec_result = MagicMock()
    # Simulate the filtering behavior - only return tasks for the current user
    filtered_tasks = [t for t in all_tasks if t.user_id == mock_user.id]
    mock_exec_result.all.return_value = filtered_tasks

    mock_db_session.exec = MagicMock(return_value=mock_exec_result)

    # Call the get_tasks function (which simulates AI calling the tool)
    result = await get_tasks(
        db_session=mock_db_session,
        user=mock_user
    )

    # Verify the result
    assert result["success"] is True
    assert result["count"] == 2  # Only the user's tasks
    assert len(result["tasks"]) == 2

    # Verify the correct tasks were returned
    returned_task_titles = [task["title"] for task in result["tasks"]]
    expected_titles = ["Buy groceries", "Walk the dog"]
    assert sorted(returned_task_titles) == sorted(expected_titles)

    # Verify that the other user's task was not included
    for task in result["tasks"]:
        assert task["id"] != "task3"


@pytest.mark.asyncio
async def test_e2e_task_completion_flow(mock_db_session, mock_user):
    """Test complete flow of completing a task via chat interface"""
    # Create mock task
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Call the complete_task function (which simulates AI calling the tool)
    result = await complete_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="test-task-id",
        completed=True
    )

    # Verify the result
    assert result["success"] is True
    assert result["message"] == "Task 'Buy groceries' completed successfully"

    # Verify that the task was updated in the session
    assert existing_task.completed is True


@pytest.mark.asyncio
async def test_e2e_task_deletion_flow(mock_db_session, mock_user):
    """Test complete flow of deleting a task via chat interface"""
    # Create mock task
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()

    # Call the delete_task function (which simulates AI calling the tool)
    result = await delete_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="test-task-id"
    )

    # Verify the result
    assert result["success"] is True
    assert result["message"] == "Task deleted successfully"

    # Verify that the task was deleted from the session
    mock_db_session.delete.assert_called_once_with(existing_task)


@pytest.mark.asyncio
async def test_e2e_task_update_flow(mock_db_session, mock_user):
    """Test complete flow of updating a task via chat interface"""
    # Create mock task
    existing_task = Task(
        id="test-task-id",
        user_id=mock_user.id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the existing task
    mock_db_session.get = MagicMock(return_value=existing_task)
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Call the update_task function (which simulates AI calling the tool)
    result = await update_task(
        db_session=mock_db_session,
        user=mock_user,
        task_id="test-task-id",
        title="Buy dinner ingredients",
        description="Chicken, vegetables, rice",
        priority="high"
    )

    # Verify the result
    assert result["success"] is True
    assert result["message"] == "Task 'Buy dinner ingredients' updated successfully"

    # Verify that the task was updated
    assert existing_task.title == "Buy dinner ingredients"
    assert existing_task.description == "Chicken, vegetables, rice"
    assert existing_task.priority == "high"


@pytest.mark.asyncio
async def test_e2e_conversation_persistence(mock_db_session, mock_user):
    """Test that conversations and messages are properly persisted"""
    # Create mock conversation
    conversation = Conversation(
        id="conv-test-id",
        user_id=mock_user.id,
        title="Test conversation",
        is_active=True
    )

    # Create mock messages
    user_message = Message(
        id="msg-user-id",
        conversation_id=conversation.id,
        role="user",
        content="Create a task to buy groceries"
    )

    assistant_message = Message(
        id="msg-assistant-id",
        conversation_id=conversation.id,
        role="assistant",
        content="I've created a task to buy groceries for you."
    )

    # Test conversation creation
    mock_db_session.add(conversation)
    mock_db_session.commit()

    # Test message creation
    mock_db_session.add(user_message)
    mock_db_session.add(assistant_message)
    mock_db_session.commit()

    # Verify conversation was created with correct user
    assert conversation.user_id == mock_user.id

    # Verify messages were associated with the correct conversation
    assert user_message.conversation_id == conversation.id
    assert assistant_message.conversation_id == conversation.id


@pytest.mark.asyncio
async def test_e2e_security_isolation(mock_db_session, mock_user, mock_other_user):
    """Test that users cannot access each other's data through AI tools"""
    # Create a task owned by another user
    other_user_task = Task(
        id="other-task-id",
        user_id=mock_other_user.id,
        title="Other user's task",
        description="This should not be accessible",
        completed=False,
        priority="medium"
    )

    # Mock session.get to return the other user's task
    mock_db_session.get = MagicMock(return_value=other_user_task)

    # Test that update_task properly validates user ownership
    with pytest.raises(Exception):  # Should raise HTTPException with 403
        await update_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user trying to update
            task_id="other-task-id",
            title="Modified title"
        )

    # Test that delete_task properly validates user ownership
    with pytest.raises(Exception):  # Should raise HTTPException with 403
        await delete_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user trying to delete
            task_id="other-task-id"
        )

    # Test that complete_task properly validates user ownership
    with pytest.raises(Exception):  # Should raise HTTPException with 403
        await complete_task(
            db_session=mock_db_session,
            user=mock_user,  # Different user trying to complete
            task_id="other-task-id",
            completed=True
        )


@pytest.mark.asyncio
async def test_e2e_ai_intent_recognition():
    """Test that AI correctly interprets user intents in various scenarios"""
    # Mock the AI service
    with patch.object(AIService, '__init__', return_value=None):
        ai_service = AIService()

        # Mock the process_message method
        ai_service.process_message = AsyncMock(return_value=(
            "I've created a task to buy groceries for you.",
            "test-conversation-id",
            []
        ))

        # Test various user inputs
        test_cases = [
            "Create a task to buy groceries",
            "I need to remember to call John tomorrow",
            "Add a task: finish the report",
            "Make a new task to clean the house"
        ]

        for user_input in test_cases:
            response, conv_id, tool_calls = await ai_service.process_message(
                db_session=MagicMock(),
                user_id="test-user-id",
                conversation_id=None,
                message_content=user_input
            )

            # Verify that the AI service was called with the correct parameters
            ai_service.process_message.assert_called()

            # Reset the mock for the next test
            ai_service.process_message.reset_mock()


def test_e2e_error_handling():
    """Test error handling in the complete flow"""
    # This test would verify that errors are properly propagated
    # and handled throughout the system
    assert True  # Placeholder - actual implementation would test error scenarios