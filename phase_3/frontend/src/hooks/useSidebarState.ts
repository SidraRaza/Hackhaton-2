import { useState, useEffect } from 'react';

interface SidebarState {
  isVisible: boolean;
  isCollapsed: boolean;
  width: number;
}

export const useSidebarState = (initialWidth: number = 256) => {
  const [sidebarState, setSidebarState] = useState<SidebarState>(() => {
    // Initialize from localStorage or use initial state
    const savedState = typeof window !== 'undefined' ? localStorage.getItem('sidebarState') : null;

    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        return {
          isVisible: parsed.isVisible ?? true,
          isCollapsed: parsed.isCollapsed ?? false,
          width: parsed.width ?? initialWidth,
        };
      } catch (e) {
        console.warn('Failed to parse sidebar state from localStorage, using defaults');
      }
    }

    return {
      isVisible: true,
      isCollapsed: false,
      width: initialWidth,
    };
  });

  // Save to localStorage whenever sidebarState changes
  useEffect(() => {
    localStorage.setItem('sidebarState', JSON.stringify(sidebarState));
  }, [sidebarState]);

  const toggleVisibility = () => {
    setSidebarState(prev => ({
      ...prev,
      isVisible: !prev.isVisible,
    }));
  };

  const toggleCollapse = () => {
    setSidebarState(prev => ({
      ...prev,
      isCollapsed: !prev.isCollapsed,
    }));
  };

  const setWidth = (width: number) => {
    if (width > 0) {
      setSidebarState(prev => ({
        ...prev,
        width,
      }));
    }
  };

  const expand = () => {
    setSidebarState(prev => ({
      ...prev,
      isCollapsed: false,
    }));
  };

  const collapse = () => {
    setSidebarState(prev => ({
      ...prev,
      isCollapsed: true,
    }));
  };

  return {
    sidebarState,
    toggleVisibility,
    toggleCollapse,
    setWidth,
    expand,
    collapse,
  };
};