import React, { useState } from 'react';
import { Task } from '@/services/taskService';
import { RecurrencePatternEnum } from '@/services/taskService';

interface RecurringTaskCompletionModalProps {
  task: Task;
  isOpen: boolean;
  onClose: () => void;
  onComplete: (options: {
    mark_series_complete?: boolean;
    skip_next_occurrence?: boolean;
    recurrence_action?: string;
    create_next_occurrence?: boolean;
  }) => void;
  isLoading?: boolean;
}

export const RecurringTaskCompletionModal = ({
  task,
  isOpen,
  onClose,
  onComplete,
  isLoading = false
}: RecurringTaskCompletionModalProps) => {
  const [selectedOption, setSelectedOption] = useState<string>('complete_this_only');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const options = {
      mark_series_complete: selectedOption === 'complete_series',
      skip_next_occurrence: selectedOption === 'skip_next',
      recurrence_action: selectedOption === 'end_series' ? 'end_series' : 'create_next',
      create_next_occurrence: selectedOption !== 'skip_next' && selectedOption !== 'end_series',
    };

    onComplete(options);
    // Let parent component handle closing after processing
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      ></div>
      <div className="relative bg-white rounded-lg shadow-xl p-6 w-full max-w-md z-50">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Complete Recurring Task
        </h3>

        <p className="text-sm text-gray-600 mb-4">
          "{task.title}" is a recurring task. How would you like to handle it?
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-3">
            <label className="flex items-start gap-3">
              <input
                type="radio"
                name="completion-option"
                value="complete_this_only"
                checked={selectedOption === 'complete_this_only'}
                onChange={(e) => setSelectedOption(e.target.value)}
                className="mt-1"
              />
              <div>
                <span className="font-medium">Complete this occurrence only</span>
                <p className="text-sm text-gray-500">
                  Complete only this instance, next occurrence remains scheduled
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3">
              <input
                type="radio"
                name="completion-option"
                value="complete_series"
                checked={selectedOption === 'complete_series'}
                onChange={(e) => setSelectedOption(e.target.value)}
              />
              <div>
                <span className="font-medium">Complete entire series</span>
                <p className="text-sm text-gray-500">
                  Complete this and all future occurrences of this task
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3">
              <input
                type="radio"
                name="completion-option"
                value="skip_next"
                checked={selectedOption === 'skip_next'}
                onChange={(e) => setSelectedOption(e.target.value)}
              />
              <div>
                <span className="font-medium">Skip next occurrence</span>
                <p className="text-sm text-gray-500">
                  Complete this one and skip the next scheduled occurrence
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3">
              <input
                type="radio"
                name="completion-option"
                value="end_series"
                checked={selectedOption === 'end_series'}
                onChange={(e) => setSelectedOption(e.target.value)}
              />
              <div>
                <span className="font-medium">End the series</span>
                <p className="text-sm text-gray-500">
                  Complete this one and cancel all future occurrences
                </p>
              </div>
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={recurringTaskCompletionLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={recurringTaskCompletionLoading}
            >
              {recurringTaskCompletionLoading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : 'Confirm'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};