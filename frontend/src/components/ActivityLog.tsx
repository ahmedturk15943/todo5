"""ActivityLog component for displaying activity history."""

import React from 'react';
import { formatDistanceToNow } from 'date-fns';

interface Activity {
  id: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  task_id?: number;
  changes?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

interface ActivityLogProps {
  activities: Activity[];
  isLoading?: boolean;
}

const actionColors: Record<string, string> = {
  created: 'bg-green-100 text-green-800',
  updated: 'bg-blue-100 text-blue-800',
  completed: 'bg-purple-100 text-purple-800',
  uncompleted: 'bg-yellow-100 text-yellow-800',
  deleted: 'bg-red-100 text-red-800',
  restored: 'bg-indigo-100 text-indigo-800',
};

const actionIcons: Record<string, string> = {
  created: '➕',
  updated: '✏️',
  completed: '✅',
  uncompleted: '↩️',
  deleted: '🗑️',
  restored: '♻️',
};

export default function ActivityLog({ activities, isLoading }: ActivityLogProps) {
  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-gray-600">Loading activity history...</p>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No activity history yet</p>
      </div>
    );
  }

  const formatChanges = (changes: Record<string, any> | undefined) => {
    if (!changes) return null;

    return (
      <div className="mt-2 text-sm text-gray-600 space-y-1">
        {Object.entries(changes).map(([key, value]) => (
          <div key={key} className="flex items-start">
            <span className="font-medium mr-2">{key}:</span>
            {typeof value === 'object' && value !== null ? (
              <span>
                <span className="line-through text-gray-400">{value.old}</span>
                {' → '}
                <span className="text-gray-900">{value.new}</span>
              </span>
            ) : (
              <span>{JSON.stringify(value)}</span>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div
          key={activity.id}
          className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              {/* Action Icon */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${actionColors[activity.action] || 'bg-gray-100 text-gray-800'}`}>
                <span className="text-lg">{actionIcons[activity.action] || '📝'}</span>
              </div>

              {/* Activity Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${actionColors[activity.action] || 'bg-gray-100 text-gray-800'}`}>
                    {activity.action}
                  </span>
                  <span className="text-sm text-gray-500">
                    {activity.entity_type}
                    {activity.entity_id && ` #${activity.entity_id}`}
                  </span>
                </div>

                {/* Changes */}
                {formatChanges(activity.changes)}

                {/* Metadata */}
                {activity.metadata && (
                  <div className="mt-2 text-xs text-gray-400">
                    {activity.metadata.source && (
                      <span className="mr-2">Source: {activity.metadata.source}</span>
                    )}
                    {activity.metadata.device_id && (
                      <span>Device: {activity.metadata.device_id}</span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Timestamp */}
            <div className="flex-shrink-0 ml-4 text-sm text-gray-500">
              {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
