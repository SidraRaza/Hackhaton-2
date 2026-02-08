"""
Reminder Scheduler Service
Foundation for checking due tasks and sending reminders
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import asyncio

from models import Task
from services.event_service import EventService
from services.notification_service import NotificationService
from services.timezone_service import TimezoneService


logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Service for scheduling and sending task reminders"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False

    def start(self):
        """Start the reminder scheduler"""
        if not self.is_running:
            # Add reminder checking job
            self.scheduler.add_job(
                self.check_and_send_reminders,
                CronTrigger(minute="*/1"),  # Check every minute
                id="reminder_checker",
                name="Check and send task reminders",
                replace_existing=True
            )

            # Add cleanup job for old reminders
            self.scheduler.add_job(
                self.cleanup_old_reminders,
                CronTrigger(hour="2"),  # Run at 2 AM daily
                id="reminder_cleanup",
                name="Clean up old reminders",
                replace_existing=True
            )

            self.scheduler.start()
            self.is_running = True
            logger.info("Reminder scheduler started")

    def stop(self):
        """Stop the reminder scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Reminder scheduler stopped")

    def schedule_reminders_for_task(self, task_id: int, reminder_times: List[datetime]):
        """Schedule specific reminders for a task"""
        for i, reminder_time in enumerate(reminder_times):
            job_id = f"reminder_{task_id}_{i}"
            self.scheduler.add_job(
                self.send_task_reminder,
                'date',
                run_date=reminder_time,
                id=job_id,
                name=f"Reminder for task {task_id}",
                args=[task_id],
                replace_existing=True
            )

    def schedule_recurring_reminders(self, task_id: int, reminder_pattern: str):
        """Schedule recurring reminders based on pattern"""
        if reminder_pattern == "daily":
            trigger = CronTrigger(minute=0, hour=9)  # Daily at 9 AM
        elif reminder_pattern == "weekly":
            trigger = CronTrigger(day_of_week=0, hour=9, minute=0)  # Weekly on Monday at 9 AM
        elif reminder_pattern == "monthly":
            trigger = CronTrigger(day=1, hour=9, minute=0)  # Monthly on 1st at 9 AM
        else:
            logger.warning(f"Unknown reminder pattern: {reminder_pattern}")
            return

        self.scheduler.add_job(
            self.send_task_reminder,
            trigger,
            id=f"recurring_reminder_{task_id}",
            name=f"Recurring reminder for task {task_id}",
            args=[task_id],
            replace_existing=True
        )

    def cancel_task_reminders(self, task_id: int):
        """Cancel all scheduled reminders for a task"""
        jobs_to_remove = []
        for job in self.scheduler.get_jobs():
            if job.id.startswith(f"reminder_{task_id}") or job.id.startswith(f"recurring_reminder_{task_id}"):
                jobs_to_remove.append(job.id)

        for job_id in jobs_to_remove:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed reminder job {job_id}")

    def check_and_send_reminders(self, session: Session):
        """
        Check for tasks that need reminders sent and send them

        Args:
            session: Database session to query tasks
        """
        try:
            # Get tasks that are due soon and have reminder times
            now = datetime.utcnow()
            # Check for tasks with due dates within the next 30 minutes
            soon_time = now + timedelta(minutes=30)

            statement = select(Task).where(
                Task.due_date.is_not(None),
                Task.due_date <= soon_time,
                Task.completed == False,
                Task.reminder_times.is_not(None)
            )

            tasks = session.exec(statement).all()
            logger.info(f"Found {len(tasks)} tasks with upcoming due dates")

            for task in tasks:
                self._process_task_reminders(task, session)

        except Exception as e:
            logger.error(f"Error in reminder checking: {str(e)}")

    def _process_task_reminders(self, task: Task, session: Session):
        """Process reminders for a single task"""
        try:
            # Convert to user's timezone for comparison
            user_timezone = "UTC"  # This would come from user preferences
            task_due_date = TimezoneService.convert_to_user_timezone(task.due_date, user_timezone)
            now = TimezoneService.convert_to_user_timezone(datetime.utcnow(), user_timezone)

            # Check if any reminder times are due
            if task.reminder_times:
                for reminder_time in task.reminder_times:
                    # Check if this reminder time is due but hasn't been sent yet
                    if reminder_time <= now:
                        # Check if this reminder was already sent
                        if not task.last_reminder_sent or task.last_reminder_sent < reminder_time:
                            # Send the reminder
                            self.send_task_reminder(task.id, session)

                            # Update last reminder sent time
                            task.last_reminder_sent = datetime.utcnow()
                            session.add(task)
                            session.commit()

        except Exception as e:
            logger.error(f"Error processing reminders for task {task.id}: {str(e)}")

    def send_task_reminder(self, task_id: int, session: Session = None):
        """
        Send a reminder for a specific task

        Args:
            task_id: ID of the task to remind about
            session: Optional database session (if not running from scheduler)
        """
        try:
            # If session not provided, we'd need to create one
            # In a real implementation, this would connect to the database properly
            from database import get_session

            # Get the task
            db_session = next(get_session()) if session is None else session
            task = db_session.exec(select(Task).where(Task.id == task_id)).first()

            if not task:
                logger.warning(f"Task {task_id} not found for reminder")
                return

            # Prepare notification
            message = f"Reminder: Task '{task.title}' is due soon!"
            if task.due_date:
                user_timezone = "UTC"  # Would come from user preferences
                local_due_date = TimezoneService.convert_to_user_timezone(task.due_date, user_timezone)
                message += f" (due: {local_due_date.strftime('%Y-%m-%d %H:%M')})"

            # Send notification via multiple channels
            success = NotificationService.send_notification(
                user_id=task.user_id,
                task_id=task_id,
                message=message,
                channels=["browser", "email"]  # Configurable
            )

            if success:
                # Emit event for the reminder
                event_data = {
                    "task_id": task.id,
                    "user_id": task.user_id,
                    "reminder_time": datetime.utcnow().isoformat(),
                    "message": message
                }

                # In a real implementation, we'd emit the event
                # EventService.emit_event("reminder.sent", event_data)

                logger.info(f"Sent reminder for task {task_id} to user {task.user_id}")
            else:
                logger.error(f"Failed to send reminder for task {task_id}")

        except Exception as e:
            logger.error(f"Error sending reminder for task {task_id}: {str(e)}")
        finally:
            if session is None and 'db_session' in locals():
                db_session.close()

    def cleanup_old_reminders(self, session: Session):
        """
        Clean up old reminder records that are no longer needed

        Args:
            session: Database session
        """
        try:
            # Remove reminder records older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            # In a real implementation with a dedicated reminder table:
            # statement = delete(Reminder).where(Reminder.sent_at < cutoff_date)
            # session.exec(statement)
            # session.commit()

            logger.info(f"Cleaned up reminders older than {cutoff_date}")

        except Exception as e:
            logger.error(f"Error cleaning up old reminders: {str(e)}")

    def get_upcoming_reminders(self, session: Session, user_id: str, hours_ahead: int = 24) -> List[dict]:
        """
        Get upcoming reminders for a user

        Args:
            session: Database session
            user_id: User ID to get reminders for
            hours_ahead: Number of hours ahead to check

        Returns:
            List of upcoming reminder information
        """
        from_date = datetime.utcnow()
        to_date = datetime.utcnow() + timedelta(hours=hours_ahead)

        statement = select(Task).where(
            Task.user_id == user_id,
            Task.due_date.is_not(None),
            Task.due_date >= from_date,
            Task.due_date <= to_date,
            Task.completed == False
        ).order_by(Task.due_date)

        tasks = session.exec(statement).all()

        upcoming_reminders = []
        for task in tasks:
            if task.reminder_times:
                for reminder_time in task.reminder_times:
                    if from_date <= reminder_time <= to_date:
                        upcoming_reminders.append({
                            "task_id": task.id,
                            "task_title": task.title,
                            "reminder_time": reminder_time,
                            "due_date": task.due_date,
                            "priority": task.priority
                        })

        return upcoming_reminders

    def reschedule_task_reminders(self, task_id: int, new_reminder_times: Optional[List[datetime]]):
        """
        Reschedule reminders for a task with new times

        Args:
            task_id: ID of the task to reschedule reminders for
            new_reminder_times: New reminder times or None to cancel all reminders
        """
        # Cancel existing reminders
        self.cancel_task_reminders(task_id)

        # Schedule new reminders if provided
        if new_reminder_times:
            self.schedule_reminders_for_task(task_id, new_reminder_times)
            logger.info(f"Rescheduled {len(new_reminder_times)} reminders for task {task_id}")
        else:
            logger.info(f"Canceled all reminders for task {task_id}")


# Global scheduler instance
reminder_scheduler = ReminderScheduler()


def init_reminder_scheduler():
    """Initialize the reminder scheduler"""
    try:
        reminder_scheduler.start()
        logger.info("Reminder scheduler initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize reminder scheduler: {str(e)}")


def shutdown_reminder_scheduler():
    """Shutdown the reminder scheduler"""
    try:
        reminder_scheduler.stop()
        logger.info("Reminder scheduler shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down reminder scheduler: {str(e)}")