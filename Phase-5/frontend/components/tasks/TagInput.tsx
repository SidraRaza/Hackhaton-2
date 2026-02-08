import React, { useState, useRef, KeyboardEvent } from 'react';
import { X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Tag {
  id: number;
  name: string;
  color: string;
}

interface TagInputProps {
  value: Tag[];
  onChange: (tags: Tag[]) => void;
  allTags: Tag[];
  placeholder?: string;
  disabled?: boolean;
  maxTags?: number;
  className?: string;
}

export function TagInput({
  value = [],
  onChange,
  allTags = [],
  placeholder = 'Add tags...',
  disabled = false,
  maxTags = 10,
  className
}: TagInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  // Calculate filtered tags on-the-fly (no useEffect!)
  const filteredTags = inputValue.trim()
    ? allTags.filter(tag =>
        tag.name.toLowerCase().includes(inputValue.toLowerCase()) &&
        !value.some(selectedTag => selectedTag.id === tag.id)
      )
    : [];

  const addTag = (tag: Tag) => {
    if (value.length >= maxTags) {
      alert(`Maximum ${maxTags} tags allowed`);
      return;
    }

    if (!value.some(t => t.id === tag.id)) {
      onChange([...value, tag]);
    }

    setInputValue('');
    setShowSuggestions(false);
    setActiveSuggestionIndex(-1);
  };

  const createNewTag = () => {
    if (!inputValue.trim() || value.length >= maxTags) return;

    // Check if tag already exists
    const existingTag = allTags.find(tag =>
      tag.name.toLowerCase() === inputValue.trim().toLowerCase()
    );

    if (existingTag) {
      addTag(existingTag);
      return;
    }

    // Create new tag with default color
    const newTag: Tag = {
      id: Date.now(), // Temporary ID
      name: inputValue.trim(),
      color: '#3B82F6'
    };

    onChange([...value, newTag]);
    setInputValue('');
    setShowSuggestions(false);
    setActiveSuggestionIndex(-1);
  };

  const removeTag = (tagId: number) => {
    onChange(value.filter(tag => tag.id !== tagId));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    
    if (newValue.trim()) {
      setShowSuggestions(true);
      setActiveSuggestionIndex(0);
    } else {
      setShowSuggestions(false);
      setActiveSuggestionIndex(-1);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (inputValue.trim()) {
        if (filteredTags.length > 0 && activeSuggestionIndex >= 0) {
          addTag(filteredTags[activeSuggestionIndex]);
        } else {
          createNewTag();
        }
      }
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1].id);
    } else if (e.key === 'ArrowDown' && showSuggestions && filteredTags.length > 0) {
      e.preventDefault();
      setActiveSuggestionIndex(prev =>
        prev < filteredTags.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp' && showSuggestions) {
      e.preventDefault();
      setActiveSuggestionIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setShowSuggestions(false);
      setActiveSuggestionIndex(-1);
    }
  };

  return (
    <div className={cn('relative w-full', className)}>
      {/* Selected tags */}
      <div className="flex flex-wrap gap-2 mb-2">
        {value.map(tag => (
          <div
            key={tag.id}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium"
            style={{ backgroundColor: `${tag.color}20`, color: tag.color }}
          >
            <span>{tag.name}</span>
            {!disabled && (
              <button
                type="button"
                onClick={() => removeTag(tag.id)}
                className="ml-1 p-0.5 rounded-full hover:bg-black/10"
                aria-label={`Remove ${tag.name} tag`}
              >
                <X size={14} />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => inputValue && setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={value.length >= maxTags ? `Max ${maxTags} tags` : placeholder}
          disabled={disabled || value.length >= maxTags}
          className={cn(
            'w-full px-4 py-2.5 border border-gray-300 rounded-lg',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            (disabled || value.length >= maxTags) && 'opacity-50 cursor-not-allowed'
          )}
        />

        {/* Suggestions */}
        {showSuggestions && (filteredTags.length > 0 || inputValue.trim()) && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
            {filteredTags.map((tag, index) => (
              <div
                key={tag.id}
                onMouseDown={() => addTag(tag)}
                onMouseEnter={() => setActiveSuggestionIndex(index)}
                className={cn(
                  'px-4 py-3 cursor-pointer hover:bg-gray-50 flex items-center gap-3',
                  index === activeSuggestionIndex ? 'bg-blue-50' : ''
                )}
              >
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: tag.color }}
                />
                <span>{tag.name}</span>
              </div>
            ))}

            {inputValue.trim() && !filteredTags.some(tag =>
              tag.name.toLowerCase() === inputValue.trim().toLowerCase()
            ) && (
              <div
                onMouseDown={createNewTag}
                className="px-4 py-3 cursor-pointer hover:bg-gray-50 flex items-center gap-3 text-blue-600 border-t border-gray-100"
              >
                <Plus size={16} />
                <span>Create "{inputValue.trim()}"</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Helper text */}
      {maxTags && (
        <p className="mt-1 text-sm text-gray-500">
          {value.length} of {maxTags} tags
        </p>
      )}
    </div>
  );
}

export default TagInput;