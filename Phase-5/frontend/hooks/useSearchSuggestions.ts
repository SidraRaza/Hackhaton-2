import { useState, useEffect, useCallback } from 'react';
import { TaskService } from '@/services/taskService';

interface SearchSuggestion {
  id: string;
  text: string;
  type: 'recent_search' | 'popular_task' | 'similar_task' | 'filter_suggestion';
}

interface UseSearchSuggestionsReturn {
  suggestions: SearchSuggestion[];
  loading: boolean;
  error: string | null;
  getSuggestions: (query: string) => Promise<SearchSuggestion[]>;
  getRecentSearches: () => string[];
  clearRecentSearches: () => void;
  addSearchToHistory: (query: string) => void;
}

export const useSearchSuggestions = (): UseSearchSuggestionsReturn => {
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getSuggestions = useCallback(async (query: string): Promise<SearchSuggestion[]> => {
    if (!query || query.trim().length < 2) {
      setSuggestions([]);
      return [];
    }

    setLoading(true);
    setError(null);

    try {
      // Get suggestions from the search service
      // For now, implement mock suggestions based on recent searches and popular tasks
      const recentSearches = getRecentSearches();
      const filteredRecents = recentSearches
        .filter(search =>
          search.toLowerCase().includes(query.toLowerCase())
        )
        .slice(0, 3); // Limit to 3 recent suggestions

      // Mock popular tasks suggestions (in a real implementation, this would come from the backend)
      const popularTasks = [
        'meeting',
        'report',
        'follow up',
        'review',
        'deadline'
      ].filter(task =>
        task.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 2); // Limit to 2 popular suggestions

      // Combine suggestions
      const recentSuggestions: SearchSuggestion[] = filteredRecents.map(search => ({
        id: `recent_${search}`,
        text: search,
        type: 'recent_search'
      }));

      const popularSuggestions: SearchSuggestion[] = popularTasks.map(task => ({
        id: `popular_${task}`,
        text: task,
        type: 'popular_task'
      }));

      const newSuggestions = [...recentSuggestions, ...popularSuggestions];

      setSuggestions(newSuggestions);
      return newSuggestions;
    } catch (err: any) {
      console.error('Failed to get search suggestions:', err);
      setError('Failed to load search suggestions');

      // Fallback to recent searches from localStorage
      const recentSearches = getRecentSearches();
      const filteredRecents = recentSearches
        .filter(search =>
          search.toLowerCase().includes(query.toLowerCase())
        )
        .slice(0, 5) // Limit to 5 suggestions
        .map(search => ({
          id: `recent_${search}`,
          text: search,
          type: 'recent_search' as const
        }));

      setSuggestions(filteredRecents);
      return filteredRecents;
    } finally {
      setLoading(false);
    }
  }, []);

  const getRecentSearches = useCallback((): string[] => {
    try {
      const recentSearchesStr = localStorage.getItem('recentTaskSearches');
      if (recentSearchesStr) {
        return JSON.parse(recentSearchesStr);
      }
    } catch (error) {
      console.error('Failed to parse recent searches:', error);
    }
    return [];
  }, []);

  const saveRecentSearch = useCallback((query: string) => {
    try {
      // Get existing recent searches
      const recentSearches = getRecentSearches();

      // Add new search to the beginning, removing duplicates
      const updatedSearches = [query, ...recentSearches.filter(search => search !== query)].slice(0, 10); // Keep max 10 recent searches

      localStorage.setItem('recentTaskSearches', JSON.stringify(updatedSearches));
    } catch (error) {
      console.error('Failed to save recent search:', error);
    }
  }, []);

  const clearRecentSearches = useCallback(() => {
    try {
      localStorage.removeItem('recentTaskSearches');
      setSuggestions([]);
    } catch (error) {
      console.error('Failed to clear recent searches:', error);
    }
  }, []);

  // Add search term to recent searches when a search is performed
  const addSearchToHistory = useCallback((query: string) => {
    if (query.trim()) {
      saveRecentSearch(query.trim());
    }
  }, [saveRecentSearch]);

  return {
    suggestions,
    loading,
    error,
    getSuggestions,
    getRecentSearches,
    clearRecentSearches,
    addSearchToHistory
  };
};

// Export a helper function to parse natural language search queries
export const parseNaturalLanguageQuery = (query: string): { searchTerm: string; filters: any } => {
  const lowerQuery = query.toLowerCase();

  // Initialize filter object
  const filters: any = {};
  let searchTerm = query;

  // Extract priority terms
  const priorityMatches = lowerQuery.match(/(high|medium|low)\s*priority/);
  if (priorityMatches) {
    filters.priority = priorityMatches[1];
    searchTerm = searchTerm.replace(new RegExp(priorityMatches[0], 'gi'), '').trim();
  }

  // Extract due date terms
  const dueDateMatches = lowerQuery.match(/due\s+(?:in\s+)?(\d+)\s*(days?|weeks?|hours?|minutes?|months?)/);
  if (dueDateMatches) {
    // This would be more complex in a real implementation
    filters.due_soon = true;
    searchTerm = searchTerm.replace(new RegExp(dueDateMatches[0], 'gi'), '').trim();
  }

  // Extract completion status
  if (lowerQuery.includes('completed') || lowerQuery.includes('done')) {
    filters.completed = true;
    searchTerm = searchTerm.replace(/completed|done/gi, '').trim();
  } else if (lowerQuery.includes('pending') || lowerQuery.includes('not done') || lowerQuery.includes('incomplete')) {
    filters.completed = false;
    searchTerm = searchTerm.replace(/pending|not done|incomplete/gi, '').trim();
  }

  // Extract date references
  if (lowerQuery.includes('today')) {
    filters.due_today = true;
    searchTerm = searchTerm.replace(/today/gi, '').trim();
  } else if (lowerQuery.includes('tomorrow')) {
    filters.due_tomorrow = true;
    searchTerm = searchTerm.replace(/tomorrow/gi, '').trim();
  }

  return {
    searchTerm: searchTerm.trim(),
    filters
  };
};