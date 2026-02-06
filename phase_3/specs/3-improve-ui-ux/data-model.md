# Data Model: Premium SaaS UI/UX for Todo App

## Overview
This document defines the data structures and entities relevant to the UI/UX improvements for the todo app. Since we're only modifying the frontend presentation layer while maintaining existing backend functionality, the data model focuses on the UI state and component data structures.

## Key Entities

### 1. Task Card Entity
**Entity Name**: TaskCard
**Fields**:
- id: string | unique identifier for the task
- title: string | task title displayed prominently
- description: string | optional detailed task description
- priority: 'low' | 'medium' | 'high' | task priority level for badge display
- status: 'todo' | 'in-progress' | 'completed' | task completion status
- dueDate: Date | optional deadline for the task
- createdAt: Date | creation timestamp
- updatedAt: Date | last modification timestamp
- isEditing: boolean | UI state indicating if task is currently being edited

**Relationships**: None (individual task representation)
**Validation Rules**:
- title must not be empty
- priority must be one of the allowed values
- dueDate must be a valid date if provided

### 2. UI Configuration Entity
**Entity Name**: UIConfig
**Fields**:
- theme: 'dark' | 'light' | current theme preference
- sidebarCollapsed: boolean | sidebar collapse state
- animationsEnabled: boolean | whether to show animations
- fontSize: 'small' | 'normal' | 'large' | text size preference

**Relationships**: Singleton configuration entity
**Validation Rules**:
- theme must be one of the allowed values
- fontSize must be one of the allowed values

### 3. Navigation Item Entity
**Entity Name**: NavItem
**Fields**:
- id: string | unique identifier
- label: string | display text for the navigation item
- href: string | route path
- icon: string | icon identifier
- isActive: boolean | whether this is the current route

**Relationships**: Part of navigation collection
**Validation Rules**:
- href must be a valid route format
- label must not be empty

### 4. Chat Message Entity
**Entity Name**: ChatMessage
**Fields**:
- id: string | unique identifier
- sender: 'user' | 'assistant' | message origin
- content: string | message text content
- timestamp: Date | message creation time
- status: 'sent' | 'delivered' | 'read' | delivery status

**Relationships**: Part of chat thread collection
**Validation Rules**:
- content must not be empty
- sender must be one of the allowed values

### 5. User Profile Entity
**Entity Name**: UserProfile
**Fields**:
- id: string | user identifier
- name: string | user's display name
- email: string | user's email address
- avatar: string | URL to user's avatar image
- preferences: UIConfig | user's UI configuration preferences

**Relationships**: Associated with tasks and chat messages
**Validation Rules**:
- email must be valid email format
- name must not be empty

## State Transitions

### Task Card State Transitions
- **Normal View** ↔ **Edit Mode**: Triggered by user clicking edit button
- **Active** ↔ **Hovered**: Triggered by mouse enter/leave events
- **Visible** ↔ **Animating**: During add/remove operations

### Sidebar State Transitions
- **Expanded** ↔ **Collapsed**: Triggered by collapse/expand button click
- **Visible** ↔ **Hidden**: On mobile devices when overlay menu is toggled

### Theme State Transitions
- **Dark Mode** ↔ **Light Mode**: Triggered by theme toggle switch

## UI-Specific Data Structures

### Dashboard Layout State
```typescript
interface DashboardLayoutState {
  sidebarWidth: number;
  isSidebarCollapsed: boolean;
  navbarHeight: number;
  contentPadding: number;
}
```

### Task Filtering Options
```typescript
interface TaskFilters {
  status: Array<'todo' | 'in-progress' | 'completed'>;
  priority: Array<'low' | 'medium' | 'high'>;
  searchTerm: string;
  dueDateRange: { start: Date; end: Date } | null;
}
```

### Animation States
```typescript
interface AnimationState {
  isAdding: boolean;
  isRemoving: boolean;
  isEditing: boolean;
  isTransitioning: boolean;
}
```

## Validation Rules Summary

1. **Required Field Validation**: All entities have required fields that must be populated
2. **Type Validation**: Fields must match their specified data types
3. **Enum Validation**: Enum fields must match one of the allowed values
4. **Format Validation**: Email and URL fields must follow proper formats
5. **Relationship Validation**: Related entities must exist before creating associations