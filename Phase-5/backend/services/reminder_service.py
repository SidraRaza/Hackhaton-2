"""
Reminder Service for handling task reminders and notifications
"""
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

from models import Task, Reminder, ReminderChannel, ReminderStatus
from services.timezone_service import TimezoneService


logger = logging.getLogger(__name__)


class ReminderService:
    """Service for managing task reminders and notifications"""

    @staticmethod
    def create_reminder(
        session: Session,
        task_id: int,
        user_id: str,
        reminder_time: datetime,
        channel: ReminderChannel = ReminderChannel.BROWSER,
        message: Optional[str] = None
    ) -> Reminder:
        """
        Create a new reminder for a task

        Args:
            session: Database session
            task_id: ID of the task to remind about
            user_id: User ID for authorization
            reminder_time: When to send the reminder
            channel: How to send the reminder
            message: Custom reminder message

        Returns:
            Created Reminder object
        """
        # Convert reminder time to UTC for storage
        from ..services.timezone_service import TimezoneService
        utc_reminder_time = TimezoneService.convert_from_user_timezone(reminder_time, "UTC")

        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            reminder_time=utc_reminder_time,
            channel=channel,
            status=ReminderStatus.PENDING,
            message=message
        )

        session.add(reminder)
        session.commit()
        session.refresh(reminder)

        logger.info(f"Created reminder for task {task_id} at {reminder_time} via {channel}")
        return reminder

    @staticmethod
    def create_multiple_reminders(
        session: Session,
        task_id: int,
        user_id: str,
        reminder_times: List[datetime],
        channel: ReminderChannel = ReminderChannel.BROWSER
    ) -> List[Reminder]:
        """
        Create multiple reminders for a single task

        Args:
            session: Database session
            task_id: ID of the task to remind about
            user_id: User ID for authorization
            reminder_times: List of times to send reminders
            channel: How to send the reminders

        Returns:
            List of created Reminder objects
        """
        reminders = []
        for reminder_time in reminder_times:
            reminder = ReminderService.create_reminder(
                session, task_id, user_id, reminder_time, channel
            )
            reminders.append(reminder)

        logger.info(f"Created {len(reminders)} reminders for task {task_id}")
        return reminders

    @staticmethod
    def get_pending_reminders(
        session: Session,
        current_time: Optional[datetime] = None,
        user_timezone: str = "UTC"
    ) -> List[Reminder]:
        """
        Get all pending reminders that should be sent now

        Args:
            session: Database session
            current_time: Current time for comparison (defaults to now)
            user_timezone: Timezone to use for comparison

        Returns:
            List of pending reminders ready to be sent
        """
        if current_time is None:
            current_time = datetime.utcnow()

        # Convert current time to UTC for comparison
        utc_current_time = TimezoneService.convert_from_user_timezone(current_time, "UTC")

        statement = select(Reminder).where(
            Reminder.status == ReminderStatus.PENDING,
            Reminder.reminder_time <= utc_current_time
        )

        reminders = session.exec(statement).all()
        logger.info(f"Found {len(reminders)} pending reminders ready to send")
        return reminders

    @staticmethod
    def get_user_reminders(
        session: Session,
        user_id: str,
        status: Optional[ReminderStatus] = None
    ) -> List[Reminder]:
        """
        Get all reminders for a user

        Args:
            session: Database session
            user_id: User ID to filter by
            status: Optional status filter

        Returns:
            List of user's reminders
        """
        statement = select(Reminder).where(Reminder.user_id == user_id)

        if status:
            statement = statement.where(Reminder.status == status)

        statement = statement.order_by(Reminder.reminder_time.desc())
        reminders = session.exec(statement).all()

        return reminders

    @staticmethod
    def get_task_reminders(
        session: Session,
        task_id: int,
        user_id: str
    ) -> List[Reminder]:
        """
        Get all reminders for a specific task

        Args:
            session: Database session
            task_id: Task ID to filter by
            user_id: User ID for authorization

        Returns:
            List of reminders for the task
        """
        statement = select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.user_id == user_id
        ).order_by(Reminder.reminder_time)

        return session.exec(statement).all()

    @staticmethod
    def update_reminder_status(
        session: Session,
        reminder_id: int,
        status: ReminderStatus,
        sent_at: Optional[datetime] = None
    ) -> Optional[Reminder]:
        """
        Update the status of a reminder

        Args:
            session: Database session
            reminder_id: ID of the reminder to update
            status: New status for the reminder
            sent_at: When the reminder was sent (for SENT status)

        Returns:
            Updated Reminder object or None if not found
        """
        reminder = session.exec(
            select(Reminder).where(Reminder.id == reminder_id)
        ).first()

        if reminder:
            reminder.status = status
            if sent_at:
                reminder.sent_at = sent_at
            reminder.updated_at = datetime.utcnow()

            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            logger.info(f"Updated reminder {reminder_id} status to {status}")
            return reminder

        return None

    @staticmethod
    def delete_reminder(
        session: Session,
        reminder_id: int,
        user_id: str
    ) -> bool:
        """
        Delete a reminder

        Args:
            session: Database session
            reminder_id: ID of the reminder to delete
            user_id: User ID for authorization

        Returns:
            True if reminder was deleted, False otherwise
        """
        reminder = session.exec(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id
            )
        ).first()

        if reminder:
            session.delete(reminder)
            session.commit()
            logger.info(f"Deleted reminder {reminder_id}")
            return True

        return False

    @staticmethod
    def cancel_task_reminders(
        session: Session,
        task_id: int,
        user_id: str
    ) -> int:
        """
        Cancel all pending reminders for a completed task

        Args:
            session: Database session
            task_id: ID of the task whose reminders to cancel
            user_id: User ID for authorization

        Returns:
            Number of cancelled reminders
        """
        reminders = session.exec(
            select(Reminder).where(
                Reminder.task_id == task_id,
                Reminder.user_id == user_id,
                Reminder.status == ReminderStatus.PENDING
            )
        ).all()

        cancelled_count = 0
        for reminder in reminders:
            reminder.status = ReminderStatus.CANCELLED
            reminder.updated_at = datetime.utcnow()
            session.add(reminder)
            cancelled_count += 1

        session.commit()
        logger.info(f"Cancelled {cancelled_count} reminders for completed task {task_id}")
        return cancelled_count

    @staticmethod
    async def send_reminder_notification(reminder: Reminder) -> bool:
        """
        Send a reminder notification via the specified channel

        Args:
            reminder: Reminder object to send

        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            if reminder.channel == ReminderChannel.BROWSER:
                # Send browser notification
                await ReminderService.send_browser_notification(reminder)
            elif reminder.channel == ReminderChannel.EMAIL:
                # Send email notification
                await ReminderService.send_email_notification(reminder)
            elif reminder.channel == ReminderChannel.SMS:
                # Send SMS notification
                await ReminderService.send_sms_notification(reminder)
            elif reminder.channel == ReminderChannel.PUSH:
                # Send push notification
                await ReminderService.send_push_notification(reminder)

            # Update reminder status to SENT
            from services.database import get_session
            # Note: This would require a proper session, simplified for example
            # In practice, this would be handled by the caller

            logger.info(f"Sent reminder {reminder.id} for task {reminder.task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send reminder {reminder.id}: {str(e)}")
            return False

    @staticmethod
    async def send_browser_notification(reminder: Reminder) -> None:
        """
        Send browser notification for a reminder

        Args:
            reminder: Reminder object to send
        """
        # This would typically integrate with frontend via WebSocket or similar
        # For now, just log the action
        logger.info(f"Browser notification sent for task {reminder.task_id}: {reminder.message or 'Task reminder'}")

    @staticmethod
    async def send_email_notification(reminder: Reminder) -> None:
        """
        Send email notification for a reminder

        Args:
            reminder: Reminder object to send
        """
        # This would integrate with an email service
        logger.info(f"Email notification sent for task {reminder.task_id}: {reminder.message or 'Task reminder'}")

    @staticmethod
    async def send_sms_notification(reminder: Reminder) -> None:
        """
        Send SMS notification for a reminder

        Args:
            reminder: Reminder object to send
        """
        # This would integrate with an SMS service like Twilio
        logger.info(f"SMS notification sent for task {reminder.task_id}: {reminder.message or 'Task reminder'}")

    @staticmethod
    async def send_push_notification(reminder: Reminder) -> None:
        """
        Send push notification for a reminder

        Args:
            reminder: Reminder object to send
        """
        # This would integrate with push notification services
        logger.info(f"Push notification sent for task {reminder.task_id}: {reminder.message or 'Task reminder'}")

    @staticmethod
    def calculate_reminder_times(
        due_date: datetime,
        reminder_intervals: List[str],
        user_timezone: str = "UTC"
    ) -> List[datetime]:
        """
        Calculate reminder times based on due date and intervals

        Args:
            due_date: When the task is due
            reminder_intervals: List of intervals like ["1h", "1d", "30m"] (1 hour, 1 day, 30 minutes before)
            user_timezone: User's timezone for calculations

        Returns:
            List of calculated reminder times
        """
        reminder_times = []
        for interval in reminder_intervals:
            try:
                # Parse interval string like "1h", "2d", "30m"
                value = int(interval[:-1])
                unit = interval[-1]

                if unit == 'm':  # minutes
                    reminder_time = due_date - timedelta(minutes=value)
                elif unit == 'h':  # hours
                    reminder_time = due_date - timedelta(hours=value)
                elif unit == 'd':  # days
                    reminder_time = due_date - timedelta(days=value)
                elif unit == 'w':  # weeks
                    reminder_time = due_date - timedelta(weeks=value)
                else:
                    continue  # Skip invalid intervals

                # Only add if reminder time is in the future
                if reminder_time > datetime.utcnow():
                    reminder_times.append(reminder_time)
            except ValueError:
                # Skip invalid interval formats
                continue

        return sorted(reminder_times)

    @staticmethod
    def schedule_reminders_for_task(
        session: Session,
        task: Task,
        reminder_intervals: List[str] = ["1h", "1d"],
        channel: ReminderChannel = ReminderChannel.BROWSER
    ) -> List[Reminder]:
        """
        Schedule default reminders for a task based on its due date

        Args:
            session: Database session
            task: Task object to schedule reminders for
            reminder_intervals: List of intervals before due date
            channel: Channel to send reminders through

        Returns:
            List of scheduled reminders
        """
        if not task.due_date:
            return []

        # Calculate reminder times
        reminder_times = ReminderService.calculate_reminder_times(
            task.due_date,
            reminder_intervals
        )

        # Create reminders
        reminders = []
        for reminder_time in reminder_times:
            reminder = ReminderService.create_reminder(
                session,
                task.id,
                task.user_id,
                reminder_time,
                channel,
                f"Reminder: Task '{task.title}' is due soon!"
            )
            reminders.append(reminder)

        logger.info(f"Scheduled {len(reminders)} reminders for task {task.id}")
        return reminders

    @staticmethod
    def get_upcoming_reminders(
        session: Session,
        user_id: str,
        hours_ahead: int = 24
    ) -> List[Reminder]:
        """
        Get reminders scheduled in the next specified hours

        Args:
            session: Database session
            user_id: User ID to filter by
            hours_ahead: Number of hours ahead to check

        Returns:
            List of upcoming reminders
        """
        from_time = datetime.utcnow()
        to_time = datetime.utcnow() + timedelta(hours=hours_ahead)

        statement = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.status == ReminderStatus.PENDING,
            Reminder.reminder_time >= from_time,
            Reminder.reminder_time <= to_time
        ).order_by(Reminder.reminder_time)

        return session.exec(statement).all()

    @staticmethod
    def snooze_reminder(
        session: Session,
        reminder_id: int,
        user_id: str,
        minutes: int = 5
    ) -> Optional[Reminder]:
        """
        Snooze a reminder by rescheduling it

        Args:
            session: Database session
            reminder_id: ID of the reminder to snooze
            user_id: User ID for authorization
            minutes: Number of minutes to snooze for

        Returns:
            Updated Reminder object with new time, or None if not found
        """
        reminder = session.exec(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id,
                Reminder.status == ReminderStatus.PENDING
            )
        ).first()

        if reminder:
            # Reschedule the reminder to a later time
            new_time = datetime.utcnow() + timedelta(minutes=minutes)
            reminder.reminder_time = new_time
            reminder.updated_at = datetime.utcnow()

            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            logger.info(f"Snoozed reminder {reminder_id} to {new_time}")
            return reminder

        return None