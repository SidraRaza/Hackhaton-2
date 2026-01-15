from sqlmodel import Session, select
from models.task import Task, TaskUpdate
from typing import List


def create_task(session: Session, task: Task) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_tasks(session: Session, user_id: int) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks


def get_task(session: Session, task_id: int) -> Task:
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    return task


def update_task(session: Session, task_id: int, task_update: TaskUpdate) -> Task:
    task = session.get(Task, task_id)
    if not task:
        return None

    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int):
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()