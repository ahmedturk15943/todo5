"""ReminderConfig component for configuring task reminders."""

import React, { useState } from 'react';

interface ReminderConfigProps {
  dueDate?: string;
  value?: ReminderConfig;
  onChange: (config: ReminderConfig | null) => void;
}

interface ReminderConfig {
  enabled: boolean;
  minutesBefore: number;
}

export default function ReminderConfig({ dueDate, value, onChange }: ReminderConfigProps) {
  const [enabled, setEnabled] = useState(value?.enabled || false);
  const [minutesBefore, setMinutesBefore] = useState(value?.minutesBefore || 60);

  const handleToggle = () => {
    const newEnabled = !enabled;
    setEnabled(newEnabled);

    if (!newEnabled) {
      onChange(null);
    } else {
      onChange({ enabled: true, minutesBefore });
    }
  };

  const handleMinutesChange = (minutes: number) => {
    setMinutesBefore(minutes);
    if (enabled) {
      onChange({ enabled: true, minutesBefore: minutes });
    }
  };

  if (!dueDate) {
    return (
      <div className="text-sm text-gray-500">
        Set a due date to enable reminders
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center">
        <input
          type="checkbox"
          id="reminder"
          checked={enabled}
          onChange={handleToggle}
          className="h-4 w-4 text-blue-600 rounded"
        />
        <label htmlFor="reminder" className="ml-2 text-sm font-medium text-gray-700">
          Remind me
        </label>
      </div>

      {enabled && (
        <div className="pl-6 space-y-2">
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="1"
              value={minutesBefore}
              onChange={(e) => handleMinutesChange(parseInt(e.target.value))}
              className="w-20 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">minutes before</span>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => handleMinutesChange(15)}
              className={`px-3 py-1 rounded text-sm ${
                minutesBefore === 15
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              15 min
            </button>
            <button
              type="button"
              onClick={() => handleMinutesChange(30)}
              className={`px-3 py-1 rounded text-sm ${
                minutesBefore === 30
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              30 min
            </button>
            <button
              type="button"
              onClick={() => handleMinutesChange(60)}
              className={`px-3 py-1 rounded text-sm ${
                minutesBefore === 60
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              1 hour
            </button>
            <button
              type="button"
              onClick={() => handleMinutesChange(1440)}
              className={`px-3 py-1 rounded text-sm ${
                minutesBefore === 1440
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              1 day
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
