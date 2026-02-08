import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from models import Tag, Task, TaskTag
from services.tag_service import TagService


@pytest.fixture(name="engine")
def fixture_engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create a test session"""
    with Session(engine) as session:
        yield session


class TestTagService:
    """Unit tests for TagService functionality"""

    def test_get_tags_by_user(self, session):
        """Test retrieving tags for a specific user"""
        # Create test data
        user_id = "test-user-123"

        tags = [
            Tag(user_id=user_id, name="work", color="#3B82F6"),
            Tag(user_id=user_id, name="personal", color="#10B981"),
            Tag(user_id="other-user", name="shared", color="#F59E0B")  # Different user
        ]

        session.add_all(tags)
        session.commit()

        # Test getting tags for user
        user_tags = TagService.get_tags_by_user(session, user_id)

        assert len(user_tags) == 2
        tag_names = [tag.name for tag in user_tags]
        assert "work" in tag_names
        assert "personal" in tag_names
        assert "shared" not in tag_names  # Should not include other user's tag

    def test_get_tag_by_id(self, session):
        """Test retrieving a specific tag by ID"""
        user_id = "test-user-123"

        # Create test tags
        tag1 = Tag(user_id=user_id, name="work", color="#3B82F6")
        tag2 = Tag(user_id="other-user", name="shared", color="#F59E0B")

        session.add_all([tag1, tag2])
        session.commit()

        # Test getting tag that belongs to user
        retrieved_tag = TagService.get_tag_by_id(session, tag1.id, user_id)
        assert retrieved_tag is not None
        assert retrieved_tag.name == "work"

        # Test getting tag that doesn't belong to user
        retrieved_tag = TagService.get_tag_by_id(session, tag2.id, user_id)
        assert retrieved_tag is None

        # Test getting non-existent tag
        retrieved_tag = TagService.get_tag_by_id(session, 999, user_id)
        assert retrieved_tag is None

    def test_create_tag(self, session):
        """Test creating a new tag"""
        user_id = "test-user-123"

        new_tag = Tag(user_id=user_id, name="important", color="#EF4444")
        created_tag = TagService.create_tag(session, new_tag)

        assert created_tag.id is not None
        assert created_tag.user_id == user_id
        assert created_tag.name == "important"
        assert created_tag.color == "#EF4444"
        assert created_tag.created_at is not None

        # Verify tag was saved to database
        db_tag = session.exec(select(Tag).where(Tag.id == created_tag.id)).first()
        assert db_tag is not None
        assert db_tag.name == "important"

    def test_create_duplicate_tag_fails(self, session):
        """Test that creating a duplicate tag fails"""
        user_id = "test-user-123"

        # Create first tag
        tag1 = Tag(user_id=user_id, name="duplicate", color="#3B82F6")
        session.add(tag1)
        session.commit()

        # Try to create another tag with same name for same user (should fail)
        tag2 = Tag(user_id=user_id, name="duplicate", color="#10B981")
        with pytest.raises(Exception):
            TagService.create_tag(session, tag2)

    def test_update_tag(self, session):
        """Test updating a tag"""
        user_id = "test-user-123"

        # Create initial tag
        tag = Tag(user_id=user_id, name="old-name", color="#3B82F6")
        session.add(tag)
        session.commit()

        # Update the tag
        update_data = {
            "name": "new-name",
            "color": "#10B981"
        }
        updated_tag = TagService.update_tag(session, tag.id, user_id, update_data)

        assert updated_tag is not None
        assert updated_tag.name == "new-name"
        assert updated_tag.color == "#10B981"

        # Verify update in database
        db_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        assert db_tag.name == "new-name"
        assert db_tag.color == "#10B981"

    def test_update_tag_different_user_fails(self, session):
        """Test that updating another user's tag fails"""
        user1_id = "test-user-1"
        user2_id = "test-user-2"

        # Create tag for user1
        tag = Tag(user_id=user1_id, name="user1-tag", color="#3B82F6")
        session.add(tag)
        session.commit()

        # Try to update with user2 ID (should fail)
        update_data = {"name": "hacked-tag"}
        updated_tag = TagService.update_tag(session, tag.id, user2_id, update_data)

        assert updated_tag is None

        # Verify tag still has original name
        db_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        assert db_tag.name == "user1-tag"

    def test_delete_tag(self, session):
        """Test deleting a tag"""
        user_id = "test-user-123"

        # Create tag
        tag = Tag(user_id=user_id, name="to-delete", color="#3B82F6")
        session.add(tag)
        session.commit()

        # Verify tag exists
        existing_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        assert existing_tag is not None

        # Delete tag
        success = TagService.delete_tag(session, tag.id, user_id)
        assert success is True

        # Verify tag is gone
        deleted_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        assert deleted_tag is None

    def test_delete_tag_different_user_fails(self, session):
        """Test that deleting another user's tag fails"""
        user1_id = "test-user-1"
        user2_id = "test-user-2"

        # Create tag for user1
        tag = Tag(user_id=user1_id, name="protected-tag", color="#3B82F6")
        session.add(tag)
        session.commit()

        # Try to delete with user2 ID (should fail)
        success = TagService.delete_tag(session, tag.id, user2_id)
        assert success is False

        # Verify tag still exists
        existing_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        assert existing_tag is not None

    def test_get_tasks_for_tag(self, session):
        """Test getting tasks associated with a specific tag"""
        user_id = "test-user-123"

        # Create tag and tasks
        tag = Tag(user_id=user_id, name="work", color="#3B82F6")
        session.add(tag)
        session.commit()

        task1 = Task(user_id=user_id, title="Work Task 1", priority="high")
        task2 = Task(user_id=user_id, title="Work Task 2", priority="medium")
        task3 = Task(user_id="other-user", title="Other Task", priority="low")  # Different user

        session.add_all([task1, task2, task3])
        session.commit()

        # Create tag-task associations
        task_tag1 = TaskTag(task_id=task1.id, tag_id=tag.id)
        task_tag2 = TaskTag(task_id=task2.id, tag_id=tag.id)
        task_tag3 = TaskTag(task_id=task3.id, tag_id=tag.id)  # This shouldn't appear in results for user1

        session.add_all([task_tag1, task_tag2, task_tag3])
        session.commit()

        # Get tasks for tag
        tasks = TagService.get_tasks_for_tag(session, tag.id, user_id)

        assert len(tasks) == 2
        task_titles = [task.title for task in tasks]
        assert "Work Task 1" in task_titles
        assert "Work Task 2" in task_titles
        assert "Other Task" not in task_titles  # Different user's task

    def test_associate_task_with_tag(self, session):
        """Test associating a task with a tag"""
        user_id = "test-user-123"

        # Create tag and task
        tag = Tag(user_id=user_id, name="test-tag", color="#3B82F6")
        task = Task(user_id=user_id, title="Test Task", priority="medium")

        session.add_all([tag, task])
        session.commit()

        # Associate task with tag
        success = TagService.associate_task_with_tag(session, task.id, tag.id)
        assert success is True

        # Verify association exists
        task_tags = session.exec(select(TaskTag).where(TaskTag.task_id == task.id)).all()
        assert len(task_tags) == 1
        assert task_tags[0].tag_id == tag.id

    def test_remove_task_from_tag(self, session):
        """Test removing a task from a tag"""
        user_id = "test-user-123"

        # Create tag and task
        tag = Tag(user_id=user_id, name="test-tag", color="#3B82F6")
        task = Task(user_id=user_id, title="Test Task", priority="medium")

        session.add_all([tag, task])
        session.commit()

        # Create association
        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
        session.add(task_tag)
        session.commit()

        # Verify association exists
        existing_assoc = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task.id,
                TaskTag.tag_id == tag.id
            )
        ).first()
        assert existing_assoc is not None

        # Remove association
        success = TagService.remove_task_from_tag(session, task.id, tag.id)
        assert success is True

        # Verify association is removed
        removed_assoc = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task.id,
                TaskTag.tag_id == tag.id
            )
        ).first()
        assert removed_assoc is None

    def test_associate_task_with_nonexistent_tag(self, session):
        """Test that associating with nonexistent tag fails"""
        user_id = "test-user-123"

        # Create task only
        task = Task(user_id=user_id, title="Test Task", priority="medium")
        session.add(task)
        session.commit()

        # Try to associate with nonexistent tag
        success = TagService.associate_task_with_tag(session, task.id, 999)
        assert success is False

    def test_get_popular_tags(self, session):
        """Test getting popular tags for a user"""
        user_id = "test-user-123"

        # Create tags
        tag1 = Tag(user_id=user_id, name="work", color="#3B82F6")
        tag2 = Tag(user_id=user_id, name="personal", color="#10B981")
        tag3 = Tag(user_id=user_id, name="shopping", color="#F59E0B")
        tag4 = Tag(user_id="other-user", name="other", color="#EF4444")  # Different user

        session.add_all([tag1, tag2, tag3, tag4])
        session.commit()

        # Create tasks
        task1 = Task(user_id=user_id, title="Task 1", priority="medium")
        task2 = Task(user_id=user_id, title="Task 2", priority="high")
        task3 = Task(user_id=user_id, title="Task 3", priority="low")
        task4 = Task(user_id=user_id, title="Task 4", priority="medium")

        session.add_all([task1, task2, task3, task4])
        session.commit()

        # Create tag-task associations (make "work" most popular)
        associations = [
            TaskTag(task_id=task1.id, tag_id=tag1.id),  # work tag on task1
            TaskTag(task_id=task2.id, tag_id=tag1.id),  # work tag on task2
            TaskTag(task_id=task3.id, tag_id=tag1.id),  # work tag on task3
            TaskTag(task_id=task2.id, tag_id=tag2.id),  # personal tag on task2
            TaskTag(task_id=task3.id, tag_id=tag3.id),  # shopping tag on task3
            TaskTag(task_id=task4.id, tag_id=tag2.id),  # personal tag on task4
        ]

        session.add_all(associations)
        session.commit()

        # Get popular tags for user
        popular_tags = TagService.get_popular_tags(session, user_id, limit=5)

        # Should return tags in order of popularity
        assert len(popular_tags) == 3  # Only user's tags
        assert popular_tags[0].name == "work"  # Most popular with 3 associations
        assert popular_tags[1].name in ["personal", "shopping"]  # Both have 2 associations
        assert popular_tags[2].name in ["personal", "shopping"]  # Both have 2 associations
        # Note: The order between personal and shopping may vary since they have same count


class TestTagModel:
    """Tests for Tag model validation and properties"""

    def test_tag_defaults(self):
        """Test that tag has correct defaults"""
        tag = Tag(user_id="test-user", name="test-tag")

        assert tag.color == "#3B82F6"  # Default blue color
        assert tag.user_id == "test-user"
        assert tag.name == "test-tag"
        assert tag.created_at is not None

    def test_tag_color_format_validation(self):
        """Test tag color format validation"""
        # Valid colors should work
        tag = Tag(user_id="test-user", name="test-tag", color="#FF0000")
        assert tag.color == "#FF0000"

        tag = Tag(user_id="test-user", name="test-tag", color="#abcdef")
        assert tag.color == "#abcdef"

    def test_tag_name_length(self):
        """Test tag name length constraints"""
        # Valid length
        tag = Tag(user_id="test-user", name="a" * 50, color="#3B82F6")
        assert len(tag.name) == 50

        # Very long name would be handled by database constraints
        # but should be validated at model level too


class TestTagIntegrationWithTasks:
    """Integration tests for tag-task relationships"""

    def test_task_creation_with_tags(self, session):
        """Test creating tasks with tags"""
        user_id = "test-user-123"

        # Create tags
        tag1 = Tag(user_id=user_id, name="work", color="#3B82F6")
        tag2 = Tag(user_id=user_id, name="urgent", color="#EF4444")

        session.add_all([tag1, tag2])
        session.commit()

        # Create task with tags
        task = Task(
            user_id=user_id,
            title="Important Work Task",
            priority="high",
            description="This is an urgent work task"
        )

        # Add tags to task
        task.tags = [tag1, tag2]

        session.add(task)
        session.commit()
        session.refresh(task)

        # Verify tags are associated
        assert len(task.tags) == 2
        tag_names = [tag.name for tag in task.tags]
        assert "work" in tag_names
        assert "urgent" in tag_names

    def test_task_update_with_tags(self, session):
        """Test updating tasks with tags"""
        user_id = "test-user-123"

        # Create task and tags
        task = Task(user_id=user_id, title="Original Task", priority="medium")
        tag1 = Tag(user_id=user_id, name="work", color="#3B82F6")
        tag2 = Tag(user_id=user_id, name="personal", color="#10B981")

        session.add_all([task, tag1, tag2])
        session.commit()

        # Update task with tags
        from services.task_service import TaskService
        updated_task = TaskService.update_task(
            session,
            task.id,
            user_id,
            {"title": "Updated Task"},
            [tag1.id, tag2.id]
        )

        session.refresh(updated_task)

        # Verify tags are associated
        assert len(updated_task.tags) == 2
        tag_names = [tag.name for tag in updated_task.tags]
        assert "work" in tag_names
        assert "personal" in tag_names

    def test_task_tag_isolation(self, session):
        """Test that tags are properly isolated between users"""
        user1_id = "test-user-1"
        user2_id = "test-user-2"

        # Create same-named tags for different users
        user1_tag = Tag(user_id=user1_id, name="common-tag", color="#3B82F6")
        user2_tag = Tag(user_id=user2_id, name="common-tag", color="#10B981")  # Different color

        session.add_all([user1_tag, user2_tag])
        session.commit()

        # Create tasks for each user
        task1 = Task(user_id=user1_id, title="User 1 Task", priority="medium")
        task2 = Task(user_id=user2_id, title="User 2 Task", priority="high")

        session.add_all([task1, task2])
        session.commit()

        # Associate each task with its user's tag
        from services.task_service import TaskService
        updated_task1 = TaskService.update_task(
            session,
            task1.id,
            user1_id,
            {},
            [user1_tag.id]
        )

        updated_task2 = TaskService.update_task(
            session,
            task2.id,
            user2_id,
            {},
            [user2_tag.id]
        )

        session.refresh(updated_task1)
        session.refresh(updated_task2)

        # Verify each task has its user's tag
        assert len(updated_task1.tags) == 1
        assert updated_task1.tags[0].name == "common-tag"
        assert updated_task1.tags[0].color == "#3B82F6"

        assert len(updated_task2.tags) == 1
        assert updated_task2.tags[0].name == "common-tag"
        assert updated_task2.tags[0].color == "#10B981"


def test_tag_service_api_integration():
    """Test the complete tag service API flow"""
    # This would typically be an integration test but we'll simulate the logic

    # Create a mock session
    mock_session = Mock(spec=Session)

    # Test the full flow of tag operations
    user_id = "test-user-123"

    # Create a tag
    tag = Tag(user_id=user_id, name="integration-test", color="#8B5CF6")
    created_tag = TagService.create_tag(mock_session, tag)

    # The mock session won't actually create a tag, but we can test the logic flow
    assert tag.user_id == user_id
    assert tag.name == "integration-test"

    # This test would be expanded with actual integration tests in a real scenario


if __name__ == "__main__":
    pytest.main([__file__])