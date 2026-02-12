"""TagInput component for managing task tags."""

import React, { useState, useEffect } from 'react';
import { getTags, createTag } from '../lib/api';

interface Tag {
  id: number;
  name: string;
  color?: string;
}

interface TagInputProps {
  value: number[];
  onChange: (tagIds: number[]) => void;
  disabled?: boolean;
}

export default function TagInput({ value, onChange, disabled }: TagInputProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTagName, setNewTagName] = useState('');
  const [showInput, setShowInput] = useState(false);

  useEffect(() => {
    loadTags();
  }, []);

  const loadTags = async () => {
    try {
      const data = await getTags();
      setTags(data);
    } catch (err) {
      console.error('Failed to load tags:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTag = (tagId: number) => {
    if (value.includes(tagId)) {
      onChange(value.filter(id => id !== tagId));
    } else {
      onChange([...value, tagId]);
    }
  };

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;

    try {
      const newTag = await createTag({ name: newTagName.trim() });
      setTags([...tags, newTag]);
      onChange([...value, newTag.id]);
      setNewTagName('');
      setShowInput(false);
    } catch (err) {
      alert('Failed to create tag');
      console.error(err);
    }
  };

  if (loading) {
    return <div className="text-sm text-gray-500">Loading tags...</div>;
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Tags
      </label>

      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <button
            key={tag.id}
            type="button"
            onClick={() => handleToggleTag(tag.id)}
            disabled={disabled}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
              value.includes(tag.id)
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            style={
              value.includes(tag.id) && tag.color
                ? { backgroundColor: tag.color, borderColor: tag.color }
                : undefined
            }
          >
            {tag.name}
          </button>
        ))}

        {!showInput && !disabled && (
          <button
            type="button"
            onClick={() => setShowInput(true)}
            className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 border-2 border-dashed border-gray-300"
          >
            + New Tag
          </button>
        )}
      </div>

      {showInput && (
        <div className="flex gap-2 mt-2">
          <input
            type="text"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateTag()}
            placeholder="Tag name"
            className="flex-1 px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
          />
          <button
            type="button"
            onClick={handleCreateTag}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Add
          </button>
          <button
            type="button"
            onClick={() => {
              setShowInput(false);
              setNewTagName('');
            }}
            className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
