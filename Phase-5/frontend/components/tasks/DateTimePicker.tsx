import React, { useState, useEffect } from 'react';
import { Calendar, Clock, X, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/tasks/ui/button';
import { Input } from '@/components/tasks/ui/input';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/tasks/ui/popover';
import { Label } from '@/components/tasks/ui/label';
import { Badge } from '@/components/tasks/ui/badge';

interface DateTimePickerProps {
  value: string | null; // ISO string or null
  onChange: (date: string | null) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
  showTime?: boolean;
  showDate?: boolean;
  minDate?: Date;
  maxDate?: Date;
}

export function DateTimePicker({
  value,
  onChange,
  disabled = false,
  placeholder = "Select date and time...",
  className,
  showTime = true,
  showDate = true,
  minDate,
  maxDate
}: DateTimePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(
    value ? new Date(value) : null
  );
  const [dateInput, setDateInput] = useState<string>("");
  const [timeInput, setTimeInput] = useState<string>("");

  // Update local state when value changes
  useEffect(() => {
    if (value) {
      const dateObj = new Date(value);
      setSelectedDate(dateObj);
      if (showDate) {
        setDateInput(formatDateForInput(dateObj));
      }
      if (showTime) {
        setTimeInput(formatTimeForInput(dateObj));
      }
    } else {
      setSelectedDate(null);
      setDateInput("");
      setTimeInput("");
    }
  }, [value, showDate, showTime]);

  const formatDateForInput = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Month is 0-indexed
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`; // YYYY-MM-DD
  };

  const formatTimeForInput = (date: Date): string => {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`; // HH:MM
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value;
    setDateInput(newDate);

    if (newDate && timeInput) {
      // Combine date and time
      const dateTime = new Date(`${newDate}T${timeInput}`);
      setSelectedDate(dateTime);
      onChange(dateTime.toISOString());
    } else if (newDate && !showTime) {
      // If only date is shown, set date with time at start of day
      const dateTime = new Date(`${newDate}T00:00:00`);
      setSelectedDate(dateTime);
      onChange(dateTime.toISOString());
    }
  };

  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = e.target.value;
    setTimeInput(newTime);

    if (dateInput && newTime) {
      // Combine date and time
      const dateTime = new Date(`${dateInput}T${newTime}`);
      setSelectedDate(dateTime);
      onChange(dateTime.toISOString());
    }
  };

  const handleClear = () => {
    setSelectedDate(null);
    setDateInput("");
    setTimeInput("");
    onChange(null);
    setIsOpen(false);
  };

  const handleToday = () => {
    const now = new Date();
    setSelectedDate(now);

    if (showDate) {
      const today = formatDateForInput(now);
      setDateInput(today);
    }

    if (showTime) {
      const time = formatTimeForInput(now);
      setTimeInput(time);
    }

    onChange(now.toISOString());
  };

  const handleTomorrow = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);

    setSelectedDate(tomorrow);

    if (showDate) {
      const tomorrowStr = formatDateForInput(tomorrow);
      setDateInput(tomorrowStr);
    }

    if (showTime) {
      // Default to 9 AM if time is shown
      setTimeInput("09:00");
      const dateTime = new Date(`${tomorrowStr}T09:00`);
      onChange(dateTime.toISOString());
    } else {
      onChange(tomorrow.toISOString());
    }
  };

  const handleNextWeek = () => {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);

    setSelectedDate(nextWeek);

    if (showDate) {
      const nextWeekStr = formatDateForInput(nextWeek);
      setDateInput(nextWeekStr);
    }

    if (showTime) {
      // Default to 9 AM if time is shown
      setTimeInput("09:00");
      const dateTime = new Date(`${nextWeekStr}T09:00`);
      onChange(dateTime.toISOString());
    } else {
      onChange(nextWeek.toISOString());
    }
  };

  const isValidDate = (date: Date): boolean => {
    if (minDate && date < minDate) return false;
    if (maxDate && date > maxDate) return false;
    return true;
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-full justify-start text-left font-normal",
            !value && "text-muted-foreground",
            disabled && "opacity-50 cursor-not-allowed",
            className
          )}
          disabled={disabled}
        >
          {value ? (
            <div className="flex  items-center gap-2">
              <Calendar size={16} />
              <span>{new Date(value).toLocaleString()}</span>
              <Button
                variant="ghost"
                size="sm"
                className="ml-auto h-6 w-6 p-0.5"
                onClick={(e) => {
                  e.stopPropagation();
                  handleClear();
                }}
              >
                <X size={14} />
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Calendar size={16} />
              <span>{placeholder}</span>
            </div>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-4 bg-white" align="start">
        <div className="space-y-4 ">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Set Due Date & Time</h3>
            {value && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="text-destructive"
              >
                <X size={16} />
                <span className="ml-1">Clear</span>
              </Button>
            )}
          </div>

          <div className="grid  grid-cols-1 gap-3">
            {showDate && (
              <div>
                <Label htmlFor="date-input">Date</Label>
                <Input
                  id="date-input"
                  type="date"
                  value={dateInput}
                  onChange={handleDateChange}
                  className="w-full"
                  min={minDate?.toISOString().split('T')[0]}
                  max={maxDate?.toISOString().split('T')[0]}
                />
              </div>
            )}

            {showTime && (
              <div>
                <Label htmlFor="time-input">Time</Label>
                <Input
                  id="time-input"
                  type="time"
                  value={timeInput}
                  onChange={handleTimeChange}
                  className="w-full"
                />
              </div>
            )}
          </div>

          {!value && (
            <div className="space-y-2">
              <Label>Suggested Dates</Label>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleToday}
                  className="text-xs"
                >
                  Today
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleTomorrow}
                  className="text-xs"
                >
                  Tomorrow
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNextWeek}
                  className="text-xs"
                >
                  Next Week
                </Button>
              </div>
            </div>
          )}

          {selectedDate && (
            <div className="pt-2 border-t">
              <Label>Selected</Label>
              <div className="mt-2">
                <Badge variant="secondary" className="text-sm">
                  {selectedDate.toLocaleString()}
                </Badge>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsOpen(false)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={() => setIsOpen(false)}
              disabled={!selectedDate || !isValidDate(selectedDate)}
            >
              <Check size={16} />
              <span className="ml-1">Set</span>
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Export a simple date-only picker
interface DatePickerProps {
  value: string | null;
  onChange: (date: string | null) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
  minDate?: Date;
  maxDate?: Date;
}

export function DatePicker({
  value,
  onChange,
  disabled = false,
  placeholder = "Select date...",
  className,
  minDate,
  maxDate
}: DatePickerProps) {
  return (
    <DateTimePicker
      value={value}
      onChange={onChange}
      disabled={disabled}
      placeholder={placeholder}
      className={className}
      showTime={false}
      showDate={true}
      minDate={minDate}
      maxDate={maxDate}
    />
  );
}

// Export a simple time-only picker
interface TimePickerProps {
  value: string | null;
  onChange: (time: string | null) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export function TimePicker({
  value,
  onChange,
  disabled = false,
  placeholder = "Select time...",
  className
}: TimePickerProps) {
  return (
    <DateTimePicker
      value={value}
      onChange={onChange}
      disabled={disabled}
      placeholder={placeholder}
      className={className}
      showTime={true}
      showDate={false}
    />
  );
}

// Export a utility function for parsing natural language dates
export function parseNaturalLanguageDate(input: string): Date | null {
  // Simple natural language date parser
  const lowerInput = input.toLowerCase().trim();

  // Handle relative dates
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (lowerInput === "today") {
    return today;
  } else if (lowerInput === "tomorrow") {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    return tomorrow;
  } else if (lowerInput === "yesterday") {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    yesterday.setHours(0, 0, 0, 0);
    return yesterday;
  } else if (lowerInput.includes("next week")) {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);
    return nextWeek;
  } else if (lowerInput.includes("next month")) {
    const nextMonth = new Date();
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    return nextMonth;
  } else if (lowerInput.includes("next year")) {
    const nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    return nextYear;
  }

  // Try to parse as standard date
  const parsed = new Date(input);
  if (isNaN(parsed.getTime())) {
    return null; // Invalid date
  }
  return parsed;
}

export default DateTimePicker;