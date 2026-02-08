import { useState, useEffect } from 'react';

// Define the type for saved filters
export interface SavedFilter {
  id: string;
  name: string;
  filters: any; // This would be more specific in a real implementation
  createdAt: Date;
  updatedAt: Date;
}

// Define the type for the hook's return value
export interface UseSavedFiltersReturn {
  savedFilters: SavedFilter[];
  saveFilter: (name: string, filters: any) => void;
  loadFilter: (id: string) => SavedFilter | undefined;
  deleteFilter: (id: string) => void;
  updateFilter: (id: string, updates: Partial<SavedFilter>) => void;
  getFilterByName: (name: string) => SavedFilter | undefined;
}

export const useSavedFilters = (): UseSavedFiltersReturn => {
  const [savedFilters, setSavedFilters] = useState<SavedFilter[]>([]);

  // Load saved filters from localStorage on mount
  useEffect(() => {
    const storedFilters = localStorage.getItem('taskFilters');
    if (storedFilters) {
      try {
        const parsedFilters = JSON.parse(storedFilters);
        // Convert string dates back to Date objects
        const filtersWithDates = parsedFilters.map((filter: any) => ({
          ...filter,
          createdAt: new Date(filter.createdAt),
          updatedAt: new Date(filter.updatedAt),
        }));
        setSavedFilters(filtersWithDates);
      } catch (error) {
        console.error('Failed to parse saved filters from localStorage:', error);
        setSavedFilters([]);
      }
    }
  }, []);

  // Save filters to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('taskFilters', JSON.stringify(savedFilters));
    } catch (error) {
      console.error('Failed to save filters to localStorage:', error);
    }
  }, [savedFilters]);

  const saveFilter = (name: string, filters: any) => {
    // Check if a filter with this name already exists
    const existingFilter = savedFilters.find(filter => filter.name === name);

    if (existingFilter) {
      // Update the existing filter
      updateFilter(existingFilter.id, {
        filters,
        updatedAt: new Date()
      });
    } else {
      // Create a new filter
      const newFilter: SavedFilter = {
        id: `filter_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name,
        filters,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      setSavedFilters(prev => [...prev, newFilter]);
    }
  };

  const loadFilter = (id: string) => {
    return savedFilters.find(filter => filter.id === id);
  };

  const deleteFilter = (id: string) => {
    setSavedFilters(prev => prev.filter(filter => filter.id !== id));
  };

  const updateFilter = (id: string, updates: Partial<SavedFilter>) => {
    setSavedFilters(prev =>
      prev.map(filter =>
        filter.id === id
          ? { ...filter, ...updates, updatedAt: new Date() }
          : filter
      )
    );
  };

  const getFilterByName = (name: string) => {
    return savedFilters.find(filter => filter.name === name);
  };

  return {
    savedFilters,
    saveFilter,
    loadFilter,
    deleteFilter,
    updateFilter,
    getFilterByName,
  };
};