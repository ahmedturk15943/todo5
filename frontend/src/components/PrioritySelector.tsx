"""PrioritySelector component for selecting task priority."""

import React from 'react';

interface PrioritySelectorProps {
  value: 'high' | 'medium' | 'low';
  onChange: (priority: 'high' | 'medium' | 'low') => void;
  disabled?: boolean;
}

export default function PrioritySelector({ value, onChange, disabled }: PrioritySelectorProps) {
  const priorities = [
    { value: 'high', label: 'High', color: 'bg-red-100 text-red-800 border-red-300' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
    { value: 'low', label: 'Low', color: 'bg-green-100 text-green-800 border-green-300' },
  ];

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Priority
      </label>
      <div className="flex gap-2">
        {priorities.map((priority) => (
          <button
            key={priority.value}
            type="button"
            onClick={() => onChange(priority.value as any)}
            disabled={disabled}
            className={`px-4 py-2 rounded-md border-2 text-sm font-medium transition-all ${
              value === priority.value
                ? priority.color + ' border-current'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {priority.label}
          </button>
        ))}
      </div>
    </div>
  );
}
