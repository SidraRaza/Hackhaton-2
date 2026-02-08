"""
Timezone Service for handling timezone conversions and due date management
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import pytz
from dateutil import parser


class TimezoneService:
    """Service for handling timezone conversions for due dates and reminders"""

    @staticmethod
    def convert_to_user_timezone(
        utc_datetime: datetime,
        user_timezone: str = "UTC"
    ) -> datetime:
        """
        Convert a UTC datetime to the user's local timezone

        Args:
            utc_datetime: Datetime in UTC
            user_timezone: Target timezone (e.g., 'America/New_York', 'Europe/London')

        Returns:
            Datetime in user's timezone
        """
        if utc_datetime.tzinfo is None:
            # If datetime is naive, assume it's UTC
            utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)

        # Get the target timezone
        target_tz = pytz.timezone(user_timezone)
        # Convert from UTC to target timezone
        return utc_datetime.astimezone(target_tz)

    @staticmethod
    def convert_from_user_timezone(
        user_datetime: datetime,
        user_timezone: str = "UTC"
    ) -> datetime:
        """
        Convert a user's local datetime to UTC

        Args:
            user_datetime: Datetime in user's timezone
            user_timezone: User's timezone (e.g., 'America/New_York', 'Europe/London')

        Returns:
            Datetime in UTC
        """
        if user_datetime.tzinfo is None:
            # If datetime is naive, treat it as being in user's timezone
            user_tz = pytz.timezone(user_timezone)
            user_datetime = user_tz.localize(user_datetime)

        # Convert to UTC
        utc_dt = user_datetime.astimezone(timezone.utc)
        return utc_dt

    @staticmethod
    def get_timezone_aware_datetime(
        date_str: str,
        time_str: str,
        timezone_str: str = "UTC"
    ) -> Optional[datetime]:
        """
        Create a timezone-aware datetime from date and time strings

        Args:
            date_str: Date string in format 'YYYY-MM-DD'
            time_str: Time string in format 'HH:MM' or 'HH:MM:SS'
            timezone_str: Timezone string (default: UTC)

        Returns:
            Timezone-aware datetime object or None if invalid
        """
        try:
            # Parse date and time
            if time_str:
                datetime_str = f"{date_str}T{time_str}"
            else:
                datetime_str = f"{date_str}T00:00:00"

            # Create naive datetime
            naive_dt = datetime.fromisoformat(datetime_str.replace("T", " "))

            # Attach timezone
            user_tz = pytz.timezone(timezone_str)
            aware_dt = user_tz.localize(naive_dt)

            return aware_dt
        except Exception:
            return None

    @staticmethod
    def is_overdue(
        due_date: datetime,
        user_timezone: str = "UTC",
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if a task is overdue based on user's timezone

        Args:
            due_date: The due date/time for the task
            user_timezone: User's timezone for comparison
            current_time: Current time to compare against (defaults to now)

        Returns:
            bool: True if task is overdue, False otherwise
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Ensure due_date is timezone-aware
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        # Convert both to user's timezone for comparison
        user_current_time = TimezoneService.convert_to_user_timezone(current_time, user_timezone)
        user_due_date = TimezoneService.convert_to_user_timezone(due_date, user_timezone)

        return user_due_date < user_current_time

    @staticmethod
    def days_until_due(
        due_date: datetime,
        user_timezone: str = "UTC",
        current_time: Optional[datetime] = None
    ) -> Optional[int]:
        """
        Calculate days until due date in user's timezone

        Args:
            due_date: The due date/time for the task
            user_timezone: User's timezone for calculation
            current_time: Current time to compare against (defaults to now)

        Returns:
            int: Number of days until due (negative if overdue), or None if no due date
        """
        if not due_date:
            return None

        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Ensure due_date is timezone-aware
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        # Convert both to user's timezone for comparison
        user_current_time = TimezoneService.convert_to_user_timezone(current_time, user_timezone)
        user_due_date = TimezoneService.convert_to_user_timezone(due_date, user_timezone)

        # Calculate difference in days
        diff = user_due_date.date() - user_current_time.date()
        return diff.days

    @staticmethod
    def get_business_days_until_due(
        due_date: datetime,
        user_timezone: str = "UTC",
        current_time: Optional[datetime] = None
    ) -> Optional[int]:
        """
        Calculate business days until due date (excluding weekends)

        Args:
            due_date: The due date/time for the task
            user_timezone: User's timezone for calculation
            current_time: Current time to compare against (defaults to now)

        Returns:
            int: Number of business days until due, or None if no due date
        """
        if not due_date:
            return None

        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Ensure due_date is timezone-aware
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        # Convert both to user's timezone for comparison
        user_current_time = TimezoneService.convert_to_user_timezone(current_time, user_timezone)
        user_due_date = TimezoneService.convert_to_user_timezone(due_date, user_timezone)

        # Calculate business days between dates
        current_date = user_current_time.date()
        due_date_only = user_due_date.date()

        business_days = 0
        current = current_date

        while current <= due_date_only:
            # Check if it's a business day (Monday-Friday)
            if current.weekday() < 5:  # 0-4 are Monday-Friday
                business_days += 1
            current += timedelta(days=1)

        return business_days

    @staticmethod
    def parse_natural_language_date(
        date_input: str,
        user_timezone: str = "UTC",
        reference_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Parse natural language date expressions like "tomorrow", "next Monday", etc.

        Args:
            date_input: Natural language date string
            user_timezone: User's timezone for the parsed date
            reference_date: Reference date for relative calculations (defaults to now)

        Returns:
            Timezone-aware datetime object or None if invalid
        """
        if not date_input:
            return None

        if reference_date is None:
            reference_date = datetime.now(timezone.utc)

        # Normalize input
        input_lower = date_input.lower().strip()

        # Handle relative dates
        if input_lower == "today":
            return datetime.now(pytz.timezone(user_timezone))
        elif input_lower == "tomorrow":
            tomorrow = reference_date + timedelta(days=1)
            return tomorrow.replace(tzinfo=None).replace(tzinfo=pytz.timezone(user_timezone))
        elif input_lower == "yesterday":
            yesterday = reference_date - timedelta(days=1)
            return yesterday.replace(tzinfo=None).replace(tzinfo=pytz.timezone(user_timezone))

        # Handle expressions like "next Monday", "in 3 days", etc.
        if "next" in input_lower:
            if "monday" in input_lower:
                return TimezoneService._get_next_weekday(reference_date, 0, user_timezone)
            elif "tuesday" in input_lower:
                return TimezoneService._get_next_weekday(reference_date, 1, user_timezone)
            elif "wednesday" in input_lower:
                return TimezoneService._get_next_weekday(reference_date, 2, user_timezone)
            elif "thursday" in input_lower:
                return TimezoneService._get_next_weekday(reference_date, 3, user_timezone)
            elif "friday" in input_lower:
                return TimezoneService._get_next_weekday(reference_date, 4, user_timezone)
            elif "saturday" in input_lower:
                return TimezoneService._get_next_weekday(reference_date, 5, user_timezone)
            elif "sunday" in input_lower:
                return TimezoneService._get_next_weekday(reference_date, 6, user_timezone)

        if "in" in input_lower:
            # Handle "in 3 days", "in 2 weeks", etc.
            import re
            match = re.search(r"in\s+(\d+)\s+(day|week|month|year)", input_lower)
            if match:
                quantity = int(match.group(1))
                unit = match.group(2)

                if unit == "day" or unit.endswith("days"):
                    new_date = reference_date + timedelta(days=quantity)
                elif unit == "week" or unit.endswith("weeks"):
                    new_date = reference_date + timedelta(weeks=quantity)
                elif unit == "month":
                    # Approximate: add 30 days per month
                    new_date = reference_date + timedelta(days=quantity * 30)
                elif unit == "year" or unit.endswith("years"):
                    new_date = reference_date.replace(year=reference_date.year + quantity)
                else:
                    return None

                return new_date.replace(tzinfo=None).replace(tzinfo=pytz.timezone(user_timezone))

        # Handle specific time expressions
        if "at" in input_lower:
            # Split date and time parts
            parts = input_lower.split(" at ")
            if len(parts) == 2:
                date_part = parts[0]
                time_part = parts[1]

                # Parse the date part
                date_obj = parser.parse(date_part)
                # Parse the time part
                time_obj = parser.parse(time_part)

                # Combine them respecting the user's timezone
                combined = datetime.combine(date_obj.date(), time_obj.time())
                user_tz = pytz.timezone(user_timezone)
                return user_tz.localize(combined)

        # Try to parse as standard date/time
        try:
            parsed_dt = parser.parse(date_input)
            if parsed_dt.tzinfo is None:
                # If no timezone info, assume it's in user's timezone
                user_tz = pytz.timezone(user_timezone)
                parsed_dt = user_tz.localize(parsed_dt)
            else:
                # If timezone info exists, convert to user's timezone
                parsed_dt = parsed_dt.astimezone(pytz.timezone(user_timezone))
            return parsed_dt
        except:
            return None

    @staticmethod
    def _get_next_weekday(ref_date: datetime, weekday: int, user_timezone: str) -> datetime:
        """
        Get the next occurrence of a specific weekday from reference date

        Args:
            ref_date: Reference date
            weekday: Weekday (0=Monday, 6=Sunday)
            user_timezone: User's timezone

        Returns:
            Next occurrence of the weekday as a timezone-aware datetime
        """
        user_ref_date = TimezoneService.convert_to_user_timezone(ref_date, user_timezone)
        days_ahead = weekday - user_ref_date.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        next_date = user_ref_date + timedelta(days_ahead)
        return next_date

    @staticmethod
    def format_datetime_for_display(
        datetime_obj: datetime,
        user_timezone: str = "UTC",
        format_type: str = "full"
    ) -> str:
        """
        Format datetime for display in user's timezone

        Args:
            datetime_obj: Datetime to format
            user_timezone: User's timezone
            format_type: How to format ('full', 'date', 'time', 'relative')

        Returns:
            Formatted datetime string
        """
        if datetime_obj.tzinfo is None:
            datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)

        user_dt = TimezoneService.convert_to_user_timezone(datetime_obj, user_timezone)

        if format_type == "full":
            return user_dt.strftime("%A, %B %d, %Y at %I:%M %p %Z")
        elif format_type == "date":
            return user_dt.strftime("%B %d, %Y")
        elif format_type == "time":
            return user_dt.strftime("%I:%M %p %Z")
        elif format_type == "relative":
            now = datetime.now(timezone.utc)
            user_now = TimezoneService.convert_to_user_timezone(now, user_timezone)
            diff = user_dt - user_now

            if diff.days == 0:
                # Same day
                if diff.seconds < 3600:  # Less than 1 hour
                    mins = diff.seconds // 60
                    return f"in {mins} minutes" if mins > 0 else "now"
                else:
                    hours = diff.seconds // 3600
                    return f"in {hours} hours" if hours > 0 else "today"
            elif diff.days == 1:
                return "tomorrow"
            elif diff.days == -1:
                return "yesterday"
            elif diff.days < 7:
                return user_dt.strftime("%A at %I:%M %p")
            else:
                return user_dt.strftime("%b %d at %I:%M %p")

    @staticmethod
    def validate_timezone(timezone_str: str) -> bool:
        """
        Validate if the given timezone string is valid

        Args:
            timezone_str: Timezone string to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False

    @staticmethod
    def get_common_timezones() -> list[str]:
        """
        Get a list of common timezones

        Returns:
            List of common timezone strings
        """
        return [
            "UTC",
            "US/Eastern",
            "US/Central",
            "US/Mountain",
            "US/Pacific",
            "Europe/London",
            "Europe/Paris",
            "Europe/Berlin",
            "Asia/Tokyo",
            "Asia/Shanghai",
            "Asia/Kolkata",
            "Australia/Sydney"
        ]