"""
Recurrence Service for handling task recurrence patterns
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import re
from croniter import croniter
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.parser import parse


class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurrenceService:
    """Service for handling task recurrence patterns and calculations"""

    @staticmethod
    def validate_pattern(
        pattern: str,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate recurrence pattern and configuration

        Args:
            pattern: Recurrence pattern (daily, weekly, monthly, yearly, custom)
            config: Configuration for the pattern

        Returns:
            bool: True if valid, raises ValueError if invalid
        """
        if pattern not in RecurrencePattern.__members__.values():
            raise ValueError(f"Invalid recurrence pattern: {pattern}. Must be one of: {[p.value for p in RecurrencePattern]}")

        if pattern == RecurrencePattern.CUSTOM:
            if not config or "cron_expression" not in config:
                raise ValueError("Custom recurrence pattern requires 'cron_expression' in config")

            # Validate cron expression
            try:
                croniter(config["cron_expression"], datetime.now())
            except ValueError as e:
                raise ValueError(f"Invalid cron expression: {str(e)}")

        elif pattern == RecurrencePattern.WEEKLY:
            if config and "days_of_week" in config:
                days = config["days_of_week"]
                if not isinstance(days, list):
                    raise ValueError("days_of_week must be a list")
                if any(not isinstance(day, int) or day < 0 or day > 6 for day in days):
                    raise ValueError("days_of_week must contain integers 0-6 (Monday=0)")

        elif pattern == RecurrencePattern.MONTHLY:
            if config and "day_of_month" in config:
                day = config["day_of_month"]
                if not isinstance(day, int) or day < 1 or day > 31:
                    raise ValueError("day_of_month must be an integer between 1 and 31")

        return True

    @staticmethod
    def parse_recurrence_pattern(
        pattern: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse recurrence pattern and return normalized configuration

        Args:
            pattern: Recurrence pattern (daily, weekly, monthly, yearly, custom)
            config: Configuration for the pattern

        Returns:
            Dict with normalized recurrence configuration
        """
        RecurrenceService.validate_pattern(pattern, config)

        normalized_config = {"pattern": pattern}

        if pattern == RecurrencePattern.DAILY:
            # Daily pattern: occurs every N days (default 1)
            interval = 1
            if config and "interval" in config:
                interval = max(1, config["interval"])
            normalized_config["interval"] = interval
            normalized_config["rrule_freq"] = DAILY

        elif pattern == RecurrencePattern.WEEKLY:
            # Weekly pattern: occurs every N weeks on specific days
            interval = 1
            days_of_week = [0]  # Default to Monday
            if config:
                interval = max(1, config.get("interval", 1))
                days_of_week = config.get("days_of_week", [0])
            normalized_config["interval"] = interval
            normalized_config["days_of_week"] = days_of_week
            normalized_config["rrule_freq"] = WEEKLY

        elif pattern == RecurrencePattern.MONTHLY:
            # Monthly pattern: occurs every N months on specific day
            interval = 1
            day_of_month = 1  # Default to 1st of month
            if config:
                interval = max(1, config.get("interval", 1))
                day_of_month = config.get("day_of_month", 1)
            normalized_config["interval"] = interval
            normalized_config["day_of_month"] = day_of_month
            normalized_config["rrule_freq"] = MONTHLY

        elif pattern == RecurrencePattern.YEARLY:
            # Yearly pattern: occurs every N years on specific date
            interval = 1
            if config:
                interval = max(1, config.get("interval", 1))
            normalized_config["interval"] = interval
            normalized_config["rrule_freq"] = YEARLY

        elif pattern == RecurrencePattern.CUSTOM:
            # Custom pattern: use cron expression
            normalized_config["cron_expression"] = config["cron_expression"]

        return normalized_config

    @staticmethod
    def calculate_next_occurrence(
        pattern: str,
        config: Optional[Dict[str, Any]],
        current_date: Optional[datetime] = None,
        last_occurrence: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence date based on recurrence pattern

        Args:
            pattern: Recurrence pattern
            config: Configuration for the pattern
            current_date: Date to calculate from (defaults to now)
            last_occurrence: Last occurrence date (for more accurate calculation)

        Returns:
            Next occurrence datetime or None if pattern is invalid
        """
        if current_date is None:
            current_date = datetime.now()

        # If last_occurrence is provided, calculate from that date
        start_date = last_occurrence or current_date

        try:
            if pattern == RecurrencePattern.DAILY:
                interval = config.get("interval", 1) if config else 1
                return start_date + timedelta(days=interval)

            elif pattern == RecurrencePattern.WEEKLY:
                interval = config.get("interval", 1) if config else 1
                days_of_week = config.get("days_of_week", [0]) if config else [0]

                # Find next occurrence based on days of week
                next_date = start_date
                for _ in range(interval * 7):  # Look ahead up to interval weeks
                    next_date += timedelta(days=1)
                    if next_date.weekday() in days_of_week:
                        return next_date

            elif pattern == RecurrencePattern.MONTHLY:
                interval = config.get("interval", 1) if config else 1
                day_of_month = config.get("day_of_month", 1) if config else 1

                # Calculate next occurrence by adding months
                next_date = start_date
                for _ in range(interval):
                    if next_date.month == 12:
                        next_date = next_date.replace(year=next_date.year + 1, month=1)
                    else:
                        next_date = next_date.replace(month=next_date.month + 1)

                # Set the day of month, handling months with fewer days
                try:
                    next_date = next_date.replace(day=day_of_month)
                except ValueError:
                    # If the day doesn't exist in the target month (e.g., Feb 30), use last day of month
                    import calendar
                    max_day = calendar.monthrange(next_date.year, next_date.month)[1]
                    next_date = next_date.replace(day=max_day)

                return next_date

            elif pattern == RecurrencePattern.YEARLY:
                interval = config.get("interval", 1) if config else 1
                next_date = start_date.replace(year=start_date.year + interval)
                return next_date

            elif pattern == RecurrencePattern.CUSTOM:
                if not config or "cron_expression" not in config:
                    return None

                cron_expr = config["cron_expression"]
                cron_iter = croniter(cron_expr, start_date)
                next_occurrence = cron_iter.get_next(datetime)
                return next_occurrence

        except Exception as e:
            print(f"Error calculating next occurrence: {str(e)}")
            return None

    @staticmethod
    def generate_occurrences(
        pattern: str,
        config: Optional[Dict[str, Any]],
        start_date: datetime,
        end_condition: Dict[str, Any]
    ) -> List[datetime]:
        """
        Generate occurrences based on recurrence pattern and end condition

        Args:
            pattern: Recurrence pattern
            config: Configuration for the pattern
            start_date: When the recurrence starts
            end_condition: Dict with 'type' and 'value' for when to stop
                          - type: "never", "after_occurrences", "until_date"
                          - value: integer for occurrences count, datetime for until_date

        Returns:
            List of occurrence datetimes
        """
        occurrences = [start_date]

        if end_condition.get("type") == "never":
            # Generate a limited number for practical purposes
            max_occurrences = 100
        elif end_condition.get("type") == "after_occurrences":
            max_occurrences = end_condition.get("value", 10)
        elif end_condition.get("type") == "until_date":
            end_date = end_condition.get("value")
            if isinstance(end_date, str):
                end_date = parse(end_date)
        else:
            # Default to 10 occurrences
            max_occurrences = 10

        current_date = start_date
        occurrence_count = 1

        while occurrence_count < max_occurrences:
            next_occurrence = RecurrenceService.calculate_next_occurrence(
                pattern, config, current_date, current_date
            )

            if next_occurrence is None:
                break

            # If we have an end date, check if we've exceeded it
            if end_condition.get("type") == "until_date":
                end_date = end_condition.get("value")
                if isinstance(end_date, str):
                    end_date = parse(end_date)
                if next_occurrence > end_date:
                    break

            occurrences.append(next_occurrence)
            current_date = next_occurrence
            occurrence_count += 1

        return occurrences

    @staticmethod
    def parse_human_recurrence(human_input: str) -> Dict[str, Any]:
        """
        Parse natural language recurrence patterns

        Args:
            human_input: Natural language string like "every day", "weekly on Mondays", etc.

        Returns:
            Dict with pattern and config
        """
        input_lower = human_input.lower().strip()

        # Parse daily patterns
        if any(word in input_lower for word in ["daily", "every day", "each day"]):
            return {
                "pattern": "daily",
                "config": {"interval": 1}
            }

        # Parse weekly patterns
        if "weekly" in input_lower or "every week" in input_lower:
            # Look for specific days
            days_map = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }

            days_of_week = []
            for day_name, day_num in days_map.items():
                if day_name in input_lower:
                    days_of_week.append(day_num)

            # Default to same day of week if no specific day mentioned
            if not days_of_week:
                days_of_week = [datetime.now().weekday()]

            return {
                "pattern": "weekly",
                "config": {"days_of_week": days_of_week}
            }

        # Parse monthly patterns
        if "monthly" in input_lower or "every month" in input_lower:
            # Look for specific day
            day_match = re.search(r"(\d{1,2})(?:st|nd|rd|th)?", input_lower)
            if day_match:
                day_of_month = int(day_match.group(1))
                return {
                    "pattern": "monthly",
                    "config": {"day_of_month": day_of_month}
                }
            else:
                # Default to same day of month
                day_of_month = datetime.now().day
                return {
                    "pattern": "monthly",
                    "config": {"day_of_month": day_of_month}
                }

        # Parse yearly patterns
        if "yearly" in input_lower or "annual" in input_lower or "every year" in input_lower:
            return {
                "pattern": "yearly",
                "config": {"interval": 1}
            }

        # Default to daily
        return {
            "pattern": "daily",
            "config": {"interval": 1}
        }

    @staticmethod
    def create_next_occurrence(original_task: Any) -> Optional[Any]:
        """
        Create the next occurrence of a recurring task

        Args:
            original_task: Original task object with recurrence settings

        Returns:
            New task instance for next occurrence or None if not recurring
        """
        if not hasattr(original_task, 'recurrence_pattern') or not original_task.recurrence_pattern:
            return None

        if original_task.occurrences_remaining is not None and original_task.occurrences_remaining <= 0:
            # No more occurrences to create
            return None

        # Calculate next occurrence date
        next_date = RecurrenceService.calculate_next_occurrence(
            original_task.recurrence_pattern,
            original_task.recurrence_config,
            last_occurrence=original_task.due_date or datetime.now()
        )

        if not next_date:
            return None

        # Create a new task based on the original
        # This would need to be adapted based on your Task model structure
        next_task_data = {
            "user_id": original_task.user_id,
            "title": original_task.title,
            "description": original_task.description,
            "priority": getattr(original_task, 'priority', 'medium'),
            "due_date": next_date,
            "recurrence_pattern": original_task.recurrence_pattern,
            "recurrence_config": original_task.recurrence_config,
            "parent_task_id": original_task.id,
            "completed": False
        }

        # Update occurrences remaining if applicable
        if original_task.occurrences_remaining is not None:
            next_task_data["occurrences_remaining"] = original_task.occurrences_remaining - 1
        else:
            # If occurrences_remaining was None, it means indefinite recurrence
            next_task_data["occurrences_remaining"] = None

        # Create next occurrence task
        from models import Task
        next_task = Task(**next_task_data)

        return next_task