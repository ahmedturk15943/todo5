"""useSearch hook for advanced search and filtering."""

import { useState, useCallback } from 'react';
import apiClient from '../lib/api';

interface SearchFilters {
  status?: 'incomplete' | 'complete';
  priority?: 'high' | 'medium' | 'low';
  tags?: string[];
  due_date_start?: string;
  due_date_end?: string;
}

export function useSearch() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string, filters?: SearchFilters) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (filters?.status) params.append('status', filters.status);
      if (filters?.priority) params.append('priority', filters.priority);
      if (filters?.tags) params.append('tags', filters.tags.join(','));
      if (filters?.due_date_start) params.append('due_date_start', filters.due_date_start);
      if (filters?.due_date_end) params.append('due_date_end', filters.due_date_end);

      const response = await apiClient.get(`/api/search?${params}`);
      setResults(response.data);
    } catch (err) {
      setError('Search failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
  }, []);

  return {
    search,
    loading,
    results,
    error,
    clearResults
  };
}
