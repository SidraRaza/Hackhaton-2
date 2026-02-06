'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { SidebarState } from '../lib/types';

interface SidebarContextType {
  sidebarState: SidebarState;
  toggleSidebar: () => void;
  collapseSidebar: () => void;
  expandSidebar: () => void;
  updateSidebarWidth: (width: number) => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export const SidebarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarState, setSidebarState] = useState<SidebarState>(() => {
    // Initialize from localStorage or default
    const savedState = localStorage.getItem('sidebarState');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        // Ensure we have proper date objects
        return {
          ...parsed,
          lastUpdated: new Date(parsed.lastUpdated)
        };
      } catch (e) {
        console.warn('Failed to parse sidebar state from localStorage, using defaults');
      }
    }

    // Default state
    return {
      id: 'sidebar-main',
      isVisible: true,
      isCollapsed: false,
      width: 256, // 64 when collapsed, 256 when expanded (matching existing values)
      position: 'left',
      lastUpdated: new Date(),
    };
  });

  // Save to localStorage whenever sidebarState changes
  useEffect(() => {
    localStorage.setItem('sidebarState', JSON.stringify(sidebarState));
  }, [sidebarState]);

  const toggleSidebar = () => {
    setSidebarState(prev => ({
      ...prev,
      isCollapsed: !prev.isCollapsed,
      lastUpdated: new Date()
    }));
  };

  const collapseSidebar = () => {
    setSidebarState(prev => ({
      ...prev,
      isCollapsed: true,
      lastUpdated: new Date()
    }));
  };

  const expandSidebar = () => {
    setSidebarState(prev => ({
      ...prev,
      isCollapsed: false,
      lastUpdated: new Date()
    }));
  };

  const updateSidebarWidth = (width: number) => {
    if (width > 0) {
      setSidebarState(prev => ({
        ...prev,
        width,
        lastUpdated: new Date()
      }));
    }
  };

  const value = {
    sidebarState,
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    updateSidebarWidth,
  };

  return (
    <SidebarContext.Provider value={value}>
      {children}
    </SidebarContext.Provider>
  );
};

export const useSidebar = (): SidebarContextType => {
  const context = useContext(SidebarContext);
  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
};