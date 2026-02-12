"""RecurrenceSelector component for selecting recurrence patterns."""

import React, { useState } from 'react';

interface RecurrenceSelectorProps {
  value?: RecurrencePattern;
  onChange: (pattern: RecurrencePattern | null) => void;
}

interface RecurrencePattern {
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom';
  interval: number;
  weeklyDays?: number[];
  monthlyDay?: number;
  endType: 'never' | 'after_occurrences' | 'by_date';
  endDate?: string;
  maxOccurrences?: number;
}

export default function RecurrenceSelector({ value, onChange }: RecurrenceSelectorProps) {
  const [enabled, setEnabled] = useState(!!value);
  const [frequency, setFrequency] = useState<'daily' | 'weekly' | 'monthly' | 'custom'>(
    value?.frequency || 'daily'
  );
  const [interval, setInterval] = useState(value?.interval || 1);
  const [weeklyDays, setWeeklyDays] = useState<number[]>(value?.weeklyDays || []);
  const [monthlyDay, setMonthlyDay] = useState(value?.monthlyDay || 1);
  const [endType, setEndType] = useState<'never' | 'after_occurrences' | 'by_date'>(
    value?.endType || 'never'
  );
  const [endDate, setEndDate] = useState(value?.endDate || '');
  const [maxOccurrences, setMaxOccurrences] = useState(value?.maxOccurrences || 10);

  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const handleToggle = () => {
    const newEnabled = !enabled;
    setEnabled(newEnabled);

    if (!newEnabled) {
      onChange(null);
    } else {
      updatePattern();
    }
  };

  const updatePattern = () => {
    const pattern: RecurrencePattern = {
      frequency,
      interval,
      endType,
    };

    if (frequency === 'weekly') {
      pattern.weeklyDays = weeklyDays;
    }

    if (frequency === 'monthly') {
      pattern.monthlyDay = monthlyDay;
    }

    if (endType === 'by_date') {
      pattern.endDate = endDate;
    }

    if (endType === 'after_occurrences') {
      pattern.maxOccurrences = maxOccurrences;
    }

    onChange(pattern);
  };

  const toggleWeekDay = (day: number) => {
    const newDays = weeklyDays.includes(day)
      ? weeklyDays.filter(d => d !== day)
      : [...weeklyDays, day].sort();
    setWeeklyDays(newDays);
  };

  React.useEffect(() => {
    if (enabled) {
      updatePattern();
    }
  }, [frequency, interval, weeklyDays, monthlyDay, endType, endDate, maxOccurrences]);

  return (
    <div className="space-y-4">
      <div className="flex items-center">
        <input
          type="checkbox"
          id="recurring"
          checked={enabled}
          onChange={handleToggle}
          className="h-4 w-4 text-blue-600 rounded"
        />
        <label htmlFor="recurring" className="ml-2 text-sm font-medium text-gray-700">
          Recurring task
        </label>
      </div>

      {enabled && (
        <div className="space-y-4 pl-6 border-l-2 border-gray-200">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repeat
            </label>
            <div className="flex gap-2">
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value as any)}
                className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="custom">Custom</option>
              </select>
              <input
                type="number"
                min="1"
                value={interval}
                onChange={(e) => setInterval(parseInt(e.target.value))}
                className="w-20 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>

          {frequency === 'weekly' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Repeat on
              </label>
              <div className="flex gap-2">
                {weekDays.map((day, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => toggleWeekDay(index)}
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      weeklyDays.includes(index)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    {day}
                  </button>
                ))}
              </div>
            </div>
          )}

          {frequency === 'monthly' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Day of month
              </label>
              <input
                type="number"
                min="1"
                max="31"
                value={monthlyDay}
                onChange={(e) => setMonthlyDay(parseInt(e.target.value))}
                className="w-20 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ends
            </label>
            <select
              value={endType}
              onChange={(e) => setEndType(e.target.value as any)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="never">Never</option>
              <option value="by_date">On date</option>
              <option value="after_occurrences">After occurrences</option>
            </select>
          </div>

          {endType === 'by_date' && (
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          )}

          {endType === 'after_occurrences' && (
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1"
                value={maxOccurrences}
                onChange={(e) => setMaxOccurrences(parseInt(e.target.value))}
                className="w-20 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">occurrences</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
