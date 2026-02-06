from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from models.task import Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus
from models.user import User


class TaskService:
    def create_task(self, session: Session, task_data: TaskCreate, user_id: UUID) -> TaskRead:
        """
        Create a new task for a user
        """
        # Create task with user_id included
        task_dict = task_data.model_dump()
        task_dict['user_id'] = user_id
        db_task = Task(**task_dict)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return TaskRead.model_validate(db_task)

    def get_tasks(self, session: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[TaskRead]:
        """
        Get all tasks for a user with optional pagination
        """
        statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
        tasks = session.exec(statement).all()
        return [TaskRead.model_validate(task) for task in tasks]

    def get_task(self, session: Session, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Get a specific task by ID for a user
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        return task

    def update_task(self, session: Session, task_id: UUID, task_data: TaskUpdate, user_id: UUID) -> Optional[TaskRead]:
        """
        Update a specific task for a user
        """
        db_task = self.get_task(session, task_id, user_id)
        if db_task:
            update_data = task_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)

            # If status is updated to completed, set completed_at
            if task_data.status == TaskStatus.completed and db_task.status != TaskStatus.completed:
                db_task.completed_at = db_task.updated_at

            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return TaskRead.model_validate(db_task)

        return None

    def delete_task(self, session: Session, task_id: UUID, user_id: UUID) -> bool:
        """
        Delete a specific task for a user
        """
        db_task = self.get_task(session, task_id, user_id)
        if db_task:
            session.delete(db_task)
            session.commit()
            return True
        return False

    def get_user_completed_tasks(self, session: Session, user_id: UUID) -> List[TaskRead]:
        """
        Get all completed tasks for a user
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.status == TaskStatus.completed
        )
        tasks = session.exec(statement).all()
        return [TaskRead.model_validate(task) for task in tasks]

    def get_user_pending_tasks(self, session: Session, user_id: UUID) -> List[TaskRead]:
        """
        Get all pending tasks for a user
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.status == TaskStatus.pending
        )
        tasks = session.exec(statement).all()
        return [TaskRead.model_validate(task) for task in tasks]