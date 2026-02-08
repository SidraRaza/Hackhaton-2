// components/tasks/TagInputWrapper.tsx
// Wrapper to convert between tag IDs and Tag objects

import React, { useMemo } from 'react';
import { TagInput } from './TagInput';

interface Tag {
  id: number;
  name: string;
  color: string;
}

interface TagInputWrapperProps {
  value: number[];  // Tag IDs
  onChange: (tagIds: number[]) => void;  // Returns tag IDs
  availableTags: Tag[];  // All available tags
  placeholder?: string;
  disabled?: boolean;
  maxTags?: number;
  className?: string;
}

export function TagInputWrapper({
  value,
  onChange,
  availableTags,
  placeholder,
  disabled,
  maxTags,
  className
}: TagInputWrapperProps) {
  // Convert tag IDs to Tag objects
  const selectedTags = useMemo(() => {
    return value
      .map(id => availableTags.find(tag => tag.id === id))
      .filter((tag): tag is Tag => tag !== undefined);
  }, [value, availableTags]);

  // Handle tag changes - convert back to IDs
  const handleChange = (tags: Tag[]) => {
    onChange(tags.map(tag => tag.id));
  };

  return (
    <TagInput
      value={selectedTags}
      onChange={handleChange}
      allTags={availableTags}
      placeholder={placeholder}
      disabled={disabled}
      maxTags={maxTags}
      className={className}
    />
  );
}