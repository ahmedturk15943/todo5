"""FilterPanel component for advanced filtering."""

import React from 'react';

interface FilterPanelProps {
  filters: {
    status?: 'incomplete' | 'complete';
    priority?: 'high' | 'medium' | 'low';
    tags?: string[];
  };
  onFilterChange: (filters: any) => void;
  onClearFilters: () => void;
}

export default function FilterPanel({ filters, onFilterChange, onClearFilters }: FilterPanelProps) {
  const hasActiveFilters = filters.status || filters.priority || (filters.tags && filters.tags.length > 0);

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Status Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Status
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="status"
              checked={!filters.status}
              onChange={() => onFilterChange({ ...filters, status: undefined })}
              className="h-4 w-4 text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">All</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="status"
              checked={filters.status === 'incomplete'}
              onChange={() => onFilterChange({ ...filters, status: 'incomplete' })}
              className="h-4 w-4 text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">Incomplete</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="status"
              checked={filters.status === 'complete'}
              onChange={() => onFilterChange({ ...filters, status: 'complete' })}
              className="h-4 w-4 text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">Complete</span>
          </label>
        </div>
      </div>

      {/* Priority Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Priority
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="priority"
              checked={!filters.priority}
              onChange={() => onFilterChange({ ...filters, priority: undefined })}
              className="h-4 w-4 text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">All</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="priority"
              checked={filters.priority === 'high'}
              onChange={() => onFilterChange({ ...filters, priority: 'high' })}
              className="h-4 w-4 text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">
              <span className="inline-block w-2 h-2 rounded-full bg-red-500 mr-1"></span>
              High
            </span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="priority"
              checked={filters.priority === 'medium'}
              onChange={() => onFilterChange({ ...filters, priority: 'medium' })}
              className="h-4 w-4 text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">
              <span className="inline-block w-2 h-2 rounded-full bg-yellow-500 mr-1"></span>
              Medium
            </span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="priority"
              checked={filters.priority === 'low'}
              onChange={() => onFilterChange({ ...filters, priority: 'low' })}
              className="h-4 w-4 text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">
              <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1"></span>
              Low
            </span>
          </label>
        </div>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            Active filters:
            <div className="mt-2 flex flex-wrap gap-2">
              {filters.status && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {filters.status}
                </span>
              )}
              {filters.priority && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {filters.priority} priority
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
