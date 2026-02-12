"""Recurring task management page."""

import React, { useEffect, useState } from 'react';
import { getRecurringPatterns, deactivateRecurringPattern } from '../lib/api';

interface RecurringPattern {
  id: number;
  frequency: string;
  interval: number;
  start_date: string;
  is_active: boolean;
  current_occurrence: number;
  max_occurrences?: number;
}

export default function RecurringPage() {
  const [patterns, setPatterns] = useState<RecurringPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPatterns();
  }, []);

  const loadPatterns = async () => {
    try {
      setLoading(true);
      const data = await getRecurringPatterns();
      setPatterns(data);
    } catch (err) {
      setError('Failed to load recurring patterns');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivate = async (patternId: number) => {
    if (!confirm('Deactivate this recurring pattern? No new occurrences will be created.')) {
      return;
    }

    try {
      await deactivateRecurringPattern(patternId);
      await loadPatterns();
    } catch (err) {
      alert('Failed to deactivate pattern');
      console.error(err);
    }
  };

  if (loading) {
    return <div className="p-4">Loading recurring patterns...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-600">{error}</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Recurring Tasks</h1>

      {patterns.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p>No recurring patterns yet.</p>
          <p className="text-sm mt-2">Create a task with recurrence to get started.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {patterns.map((pattern) => (
            <div
              key={pattern.id}
              className="bg-white rounded-lg shadow p-4 border border-gray-200"
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium text-lg">
                    {pattern.frequency.charAt(0).toUpperCase() + pattern.frequency.slice(1)}
                    {pattern.interval > 1 && ` (every ${pattern.interval})`}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Started: {new Date(pattern.start_date).toLocaleDateString()}
                  </div>
                  {pattern.max_occurrences && (
                    <div className="text-sm text-gray-600">
                      Occurrences: {pattern.current_occurrence} / {pattern.max_occurrences}
                    </div>
                  )}
                  <div className="mt-2">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        pattern.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {pattern.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                {pattern.is_active && (
                  <button
                    onClick={() => handleDeactivate(pattern.id)}
                    className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
                  >
                    Deactivate
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
