import { apiClient } from '@/lib/api';
import { Task, TaskFilters } from './taskService';

export interface SearchSuggestion {
  id: string;
  text: string;
  type: 'recent_search' | 'popular_task' | 'similar_task' | 'filter_suggestion';
}

export interface SearchResults {
  tasks: Task[];
  total: number;
  query: string;
  filtersApplied: TaskFilters;
  suggestions: SearchSuggestion[];
  tookMs: number;
}

export interface NaturalLanguageQueryResult {
  query: string;
  extractedFilters: Partial<TaskFilters>;
  searchTerms: string[];
}

export class SearchService {
  /**
   * Perform full-text search across tasks
   */
  static async searchTasks(
    query: string,
    filters?: TaskFilters
  ): Promise<SearchResults> {
    const startTime = Date.now();

    const params = new URLSearchParams();
    params.set('search', query);

    // Add any additional filters
    if (filters) {
      if (filters.priority) {
        filters.priority.forEach(p => params.append('priority', p));
      }
      if (filters.tags) {
        filters.tags.forEach(t => params.append('tags', t.toString()));
      }
      if (filters.due_date_from) {
        params.set('due_date_from', filters.due_date_from);
      }
      if (filters.due_date_to) {
        params.set('due_date_to', filters.due_date_to);
      }
      if (filters.status_filter) {
        params.set('status_filter', filters.status_filter);
      }
      if (filters.sort) {
        params.set('sort', filters.sort);
      }
      if (filters.sort_order) {
        params.set('sort_order', filters.sort_order);
      }
      if (filters.use_saved_filters !== undefined) {
        params.set('use_saved_filters', filters.use_saved_filters.toString());
      }
      if (filters.save_filters !== undefined) {
        params.set('save_filters', filters.save_filters.toString());
      }
    }

    const queryString = params.toString();
    const endpoint = `/tasks/search${queryString ? '?' + queryString : ''}`;

    const response = await apiClient.get<any>(endpoint);

    const result: SearchResults = {
      tasks: response.tasks || response || [],
      total: response.total || response.length || 0,
      query,
      filtersApplied: filters || {},
      suggestions: response.suggestions || [],
      tookMs: Date.now() - startTime
    };

    return result;
  }

  /**
   * Parse natural language query to extract filters and search terms
   */
  static async parseNaturalLanguageQuery(query: string): Promise<NaturalLanguageQueryResult> {
    // This is a simplified implementation - in a real app, this would be more sophisticated
    // using NLP libraries or backend processing

    const lowerQuery = query.toLowerCase();
    const extractedFilters: Partial<TaskFilters> = {};
    const searchTerms: string[] = [];

    // Extract priority terms
    if (lowerQuery.includes('high priority') || lowerQuery.includes('high prio') || lowerQuery.includes('urgent')) {
      extractedFilters.priority = ['high'];
    } else if (lowerQuery.includes('medium priority') || lowerQuery.includes('medium prio')) {
      extractedFilters.priority = ['medium'];
    } else if (lowerQuery.includes('low priority') || lowerQuery.includes('low prio')) {
      extractedFilters.priority = ['low'];
    }

    // Extract completion status
    if (lowerQuery.includes('completed') || lowerQuery.includes('done')) {
      extractedFilters.status_filter = 'completed';
    } else if (lowerQuery.includes('pending') || lowerQuery.includes('incomplete') || lowerQuery.includes('not done')) {
      extractedFilters.status_filter = 'pending';
    }

    // Extract due date terms
    const today = new Date();
    if (lowerQuery.includes('today')) {
      extractedFilters.due_date_from = today.toISOString().split('T')[0];
      const tomorrow = new Date();
      tomorrow.setDate(today.getDate() + 1);
      extractedFilters.due_date_to = tomorrow.toISOString().split('T')[0];
    } else if (lowerQuery.includes('tomorrow')) {
      const tomorrow = new Date();
      tomorrow.setDate(today.getDate() + 1);
      extractedFilters.due_date_from = tomorrow.toISOString().split('T')[0];
      const dayAfter = new Date();
      dayAfter.setDate(today.getDate() + 2);
      extractedFilters.due_date_to = dayAfter.toISOString().split('T')[0];
    } else if (lowerQuery.includes('this week')) {
      const endOfWeek = new Date();
      endOfWeek.setDate(today.getDate() + (7 - today.getDay()));
      extractedFilters.due_date_from = today.toISOString().split('T')[0];
      extractedFilters.due_date_to = endOfWeek.toISOString().split('T')[0];
    } else if (lowerQuery.includes('overdue')) {
      extractedFilters.overdue = true;
    }

    // Extract search terms (remove known filter terms)
    const filterTerms = ['high priority', 'medium priority', 'low priority', 'high prio', 'medium prio', 'low prio', 'urgent', 'completed', 'done', 'pending', 'incomplete', 'not done', 'today', 'tomorrow', 'this week', 'overdue'];
    let cleanQuery = query;

    filterTerms.forEach(term => {
      cleanQuery = cleanQuery.replace(new RegExp(term, 'gi'), '');
    });

    // Extract remaining search terms
    const terms = cleanQuery.trim().split(/\s+/).filter(term => term.length > 0);
    searchTerms.push(...terms);

    return {
      query,
      extractedFilters,
      searchTerms
    };
  }

  /**
   * Get search suggestions as user types
   */
  static async getSuggestions(query: string): Promise<SearchSuggestion[]> {
    if (!query || query.trim().length < 2) {
      return [];
    }

    try {
      // In a real implementation, this would call an endpoint like /api/tasks/search/suggestions
      // For now, we'll simulate with mock data based on recent searches and popular tasks
      const suggestions: SearchSuggestion[] = [];

      // Add recent search suggestions
      const recentSearches = localStorage.getItem('recentTaskSearches');
      if (recentSearches) {
        try {
          const searches = JSON.parse(recentSearches);
          const filteredSearches = searches.filter((s: string) =>
            s.toLowerCase().includes(query.toLowerCase())
          );

          filteredSearches.forEach((search: string) => {
            suggestions.push({
              id: `recent-${search}`,
              text: search,
              type: 'recent_search'
            });
          });
        } catch (error) {
          console.error('Failed to parse recent searches:', error);
        }
      }

      // Add filter suggestions based on query
      if (query.toLowerCase().includes('pri')) {
        suggestions.push({
          id: 'suggestion-priority-high',
          text: 'High Priority Tasks',
          type: 'filter_suggestion'
        });
        suggestions.push({
          id: 'suggestion-priority-medium',
          text: 'Medium Priority Tasks',
          type: 'filter_suggestion'
        });
        suggestions.push({
          id: 'suggestion-priority-low',
          text: 'Low Priority Tasks',
          type: 'filter_suggestion'
        });
      }

      if (query.toLowerCase().includes('due')) {
        suggestions.push({
          id: 'suggestion-due-today',
          text: 'Tasks Due Today',
          type: 'filter_suggestion'
        });
        suggestions.push({
          id: 'suggestion-due-overdue',
          text: 'Overdue Tasks',
          type: 'filter_suggestion'
        });
      }

      return suggestions.slice(0, 10); // Limit to 10 suggestions
    } catch (error) {
      console.error('Failed to get search suggestions:', error);
      return [];
    }
  }

  /**
   * Save search query to recent searches
   */
  static saveRecentSearch(query: string): void {
    try {
      const recentSearches = localStorage.getItem('recentTaskSearches');
      let searches: string[] = [];

      if (recentSearches) {
        try {
          searches = JSON.parse(recentSearches);
        } catch (error) {
          console.error('Failed to parse recent searches:', error);
        }
      }

      // Add query to beginning of array and limit to 10 items
      searches = [query, ...searches.filter((s) => s !== query)].slice(0, 10);

      localStorage.setItem('recentTaskSearches', JSON.stringify(searches));
    } catch (error) {
      console.error('Failed to save recent search:', error);
    }
  }

  /**
   * Get recent search queries
   */
  static getRecentSearches(): string[] {
    try {
      const recentSearches = localStorage.getItem('recentTaskSearches');
      if (recentSearches) {
        return JSON.parse(recentSearches);
      }
      return [];
    } catch (error) {
      console.error('Failed to get recent searches:', error);
      return [];
    }
  }
}