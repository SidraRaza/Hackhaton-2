import { useState } from 'react';
import { useSavedFilters } from '@/hooks/useSavedFilters';
import { Save, FolderOpen, Trash2, X } from 'lucide-react';

// Define the same interface here to avoid circular dependency
interface FilterParams {
  search?: string;
  priority?: string; // Using string instead of enum to avoid import issues
  tag_ids?: number[];
  completed?: boolean;
  has_due_date?: boolean;
  overdue?: boolean;
  due_date_from?: string;
  due_date_to?: string;
  sort_by?: string; // Using string instead of SortField to avoid import issues
  sort_order?: string; // Using string instead of SortOrder to avoid import issues
  secondary_sort?: string; // Using string instead of SortField to avoid import issues
  secondary_order?: string; // Using string instead of SortOrder to avoid import issues
  use_saved_filters?: boolean;
  save_filters?: boolean;
}

interface SavedFilterControlsProps {
  currentFilters: FilterParams;
  onLoadFilter: (filters: Partial<FilterParams>) => void;
  onApplyFilters: () => void;
}

export const SavedFilterControls = ({
  currentFilters,
  onLoadFilter,
  onApplyFilters
}: SavedFilterControlsProps) => {
  const { savedFilters, saveFilter: saveFilterFn, loadFilter: loadFilterFn, deleteFilter: deleteFilterFn } = useSavedFilters();
  const [filterName, setFilterName] = useState('');
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false);
  const [isLoadDialogOpen, setIsLoadDialogOpen] = useState(false);

  const handleSaveFilter = () => {
    if (filterName.trim()) {
      // Create a simplified filter object to save (excluding name and timestamps)
      const filterToSave = {
        ...currentFilters,
        name: filterName.trim(),
        saved_at: new Date().toISOString()
      };
      saveFilterFn(filterName.trim(), filterToSave);
      setFilterName('');
      setIsSaveDialogOpen(false);
    }
  };

  const handleLoadSavedFilter = (id: string) => {
    const savedFilter = loadFilterFn(id);
    if (savedFilter) {
      // Extract just the filter settings, excluding the metadata
      const { name, saved_at, ...filterSettings } = savedFilter.filters;
      onLoadFilter(filterSettings);
      onApplyFilters();
    }
    setIsLoadDialogOpen(false);
  };

  const handleDeleteFilter = (id: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent event bubbling
    deleteFilterFn(id);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, callback: () => void) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      callback();
    }
  };

  return (
    <div className="flex flex-col sm:flex-row gap-2">
      {/* Save Filter Button and Modal */}
      <div className="relative inline-block">
        <button
          onClick={() => setIsSaveDialogOpen(true)}
          className="inline-flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <Save className="h-4 w-4" />
          <span>Save Filter</span>
        </button>

        {isSaveDialogOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div
              className="fixed inset-0 bg-black bg-opacity-50"
              onClick={() => setIsSaveDialogOpen(false)}
            ></div>
            <div className="relative bg-white rounded-lg shadow-xl p-6 w-full max-w-md z-50">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Save Current Filter</h3>

              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Enter filter name..."
                  value={filterName}
                  onChange={(e) => setFilterName(e.target.value)}
                  onKeyDown={(e) => handleKeyDown(e, handleSaveFilter)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
                <button
                  onClick={handleSaveFilter}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Save
                </button>
              </div>

              <button
                onClick={() => setIsSaveDialogOpen(false)}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-500"
              >
                <span className="sr-only">Close</span>
                <X className="h-6 w-6" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Load Filter Button and Modal */}
      <div className="relative inline-block">
        <button
          onClick={() => setIsLoadDialogOpen(true)}
          className="inline-flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <FolderOpen className="h-4 w-4" />
          <span>Load Filter</span>
        </button>

        {isLoadDialogOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div
              className="fixed inset-0 bg-black bg-opacity-50"
              onClick={() => setIsLoadDialogOpen(false)}
            ></div>
            <div className="relative bg-white rounded-lg shadow-xl p-6 w-full max-w-md z-50 max-h-[70vh] overflow-y-auto">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Load Saved Filter</h3>

              <div className="pt-2">
                {savedFilters.length > 0 ? (
                  <ul className="space-y-2">
                    {savedFilters.map((filter) => (
                      <li
                        key={filter.id}
                        className="flex items-center justify-between p-2 border rounded-md hover:bg-gray-50 cursor-pointer"
                        onClick={() => handleLoadSavedFilter(filter.id)}
                      >
                        <span className="truncate">{filter.name}</span>
                        <button
                          onClick={(e) => handleDeleteFilter(filter.id, e)}
                          className="text-red-500 hover:text-red-700 ml-2"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 italic">No saved filters yet</p>
                )}
              </div>

              <button
                onClick={() => setIsLoadDialogOpen(false)}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-500"
              >
                <span className="sr-only">Close</span>
                <X className="h-6 w-6" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};