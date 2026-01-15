# UI Components Specification

> **Feature**: Reusable UI Components
> **Phase**: II
> **Status**: Ready for Implementation

## Overview

Define reusable UI components for the Hackathon II Todo App using Next.js App Router with TypeScript and Tailwind CSS. Components follow mobile-first responsive design principles with server components by default and client components only for interactivity.

## Related Specs

- `@specs/features/task-crud.md` - Task UI requirements
- `@specs/features/authentication.md` - Auth UI requirements
- `@specs/ui/pages.md` - Component composition
- `@specs/ui/enhancements.md` - UI improvements and enhancements
- `@specs/api/rest-endpoints.md` - Data binding requirements

---

## Component Library

### 1. Header Component

**Purpose**: Site-wide navigation header with user authentication status

**Props Interface**:
```typescript
interface HeaderProps {
  user?: {
    id: string;
    username: string;
    fullName?: string;
  };
  onLogout?: () => void;
}
```

**Functionality**:
- Displays app title/logo
- Shows user menu when authenticated
- Shows login/register links when not authenticated
- Mobile-responsive hamburger menu
- Dark/light mode toggle (optional)

**Tailwind Classes**:
- Desktop: Fixed height, horizontal padding, flex layout
- Mobile: Collapsible menu, sticky positioning
- Color: Primary background with contrasting text
- Shadow: Subtle elevation effect

**States**:
- Authenticated: User avatar, username, logout button
- Guest: Login/register navigation links

### 2. TaskCard Component

**Purpose**: Display individual task with controls

**Props Interface**:
```typescript
interface TaskCardProps {
  task: {
    id: string;
    title: string;
    description?: string;
    status: 'pending' | 'in-progress' | 'completed';
    priority: 'low' | 'medium' | 'high';
    dueDate?: string;
    createdAt: string;
    updatedAt: string;
  };
  onToggleComplete?: (taskId: string, currentStatus: string) => void;
  onDelete?: (taskId: string) => void;
  onEdit?: (taskId: string) => void;
}
```

**Functionality**:
- Displays task title prominently
- Shows description if available
- Visual indicator for priority level
- Status badge with color coding
- Due date display with overdue warning
- Action buttons (complete, edit, delete)
- Strikethrough for completed tasks

**Tailwind Classes**:
- Background: White card with subtle border
- Priority: Color-coded badges (red/green/yellow)
- Status: Different colors for each status
- Hover: Subtle elevation and shadow effects
- Completed: Line-through text decoration

**States**:
- Pending: Normal appearance
- In Progress: Different color scheme
- Completed: Strikethrough, muted appearance
- Loading: Skeleton loader state

### 3. TaskForm Component

**Purpose**: Create or update task with validation

**Props Interface**:
```typescript
interface TaskFormProps {
  task?: {
    id?: string;
    title?: string;
    description?: string;
    priority?: 'low' | 'medium' | 'high';
    dueDate?: string;
  };
  onSubmit: (data: {
    title: string;
    description?: string;
    priority?: 'low' | 'medium' | 'high';
    dueDate?: string;
  }) => void;
  onCancel?: () => void;
  submitLabel?: string;
  isLoading?: boolean;
}
```

**Functionality**:
- Title input with character counter
- Description textarea
- Priority selection dropdown
- Due date picker
- Submit and cancel buttons
- Client-side validation
- Error display for invalid inputs

**Tailwind Classes**:
- Container: Card-style with padding
- Inputs: Consistent styling with focus states
- Buttons: Primary and secondary variants
- Validation: Error state highlighting
- Loading: Disabled state with spinner

**States**:
- Create mode: Empty form
- Edit mode: Prefilled with task data
- Validating: Shows validation feedback
- Submitting: Loading state

### 4. TaskList Component

**Purpose**: Display collection of tasks with filtering and sorting

**Props Interface**:
```typescript
interface TaskListProps {
  tasks: Array<{
    id: string;
    title: string;
    description?: string;
    status: 'pending' | 'in-progress' | 'completed';
    priority: 'low' | 'medium' | 'high';
    dueDate?: string;
    createdAt: string;
    updatedAt: string;
  }>;
  onToggleComplete?: (taskId: string, currentStatus: string) => void;
  onDelete?: (taskId: string) => void;
  onEdit?: (taskId: string) => void;
  filters?: {
    status?: 'all' | 'pending' | 'in-progress' | 'completed';
    priority?: 'all' | 'low' | 'medium' | 'high';
  };
  onFilterChange?: (filters: {
    status?: 'all' | 'pending' | 'in-progress' | 'completed';
    priority?: 'all' | 'low' | 'medium' | 'high';
  }) => void;
  sortBy?: 'created_at' | 'title' | 'due_date' | 'priority';
  sortOrder?: 'asc' | 'desc';
  onSortChange?: (sortBy: string, sortOrder: 'asc' | 'desc') => void;
}
```

**Functionality**:
- Displays multiple TaskCard components
- Filter controls for status and priority
- Sort controls for different fields
- Empty state when no tasks
- Loading state during data fetch
- Error state for API failures

**Tailwind Classes**:
- Container: Responsive grid layout
- Filters: Horizontal control bar
- Sort: Dropdown selectors
- Empty: Centered message with call to action

**States**:
- Loading: Skeleton loader cards
- Empty: Friendly message with create button
- Error: Error message with retry button
- Filtered: Shows filtered results

### 5. AuthForm Component

**Purpose**: Unified authentication form for login and registration

**Props Interface**:
```typescript
interface AuthFormProps {
  mode: 'login' | 'register';
  onSubmit: (credentials: {
    email: string;
    password: string;
    username?: string;
    fullName?: string;
  }) => void;
  onSwitchMode?: () => void;
  errorMessage?: string;
  isLoading?: boolean;
}
```

**Functionality**:
- Email input field
- Password input field
- Additional fields for registration (username, full name)
- Mode switching (login/register)
- Form validation
- Error message display
- Loading state during submission

**Tailwind Classes**:
- Container: Centered card layout
- Inputs: Consistent styling with icons
- Buttons: Primary for submit, secondary for switch
- Errors: Red text with icon

**States**:
- Login: Email and password only
- Register: All fields visible
- Validating: Shows validation feedback
- Submitting: Loading state

### 6. Button Component

**Purpose**: Consistent button styling across the application

**Props Interface**:
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}
```

**Functionality**:
- Click handling
- Loading state with spinner
- Disabled state
- Responsive sizing
- Different visual variants

**Tailwind Classes**:
- Primary: Solid background, white text
- Secondary: Border outline, colored text
- Danger: Red background/text
- Ghost: Transparent with hover effects

**States**:
- Default: Normal appearance
- Hover: Slight color variation
- Active: Pressed appearance
- Disabled: Muted appearance

---

## Styling Guidelines

### Color Palette
- Primary: indigo-600 (buttons, links, highlights)
- Secondary: gray-700 (text, borders)
- Success: green-500 (completed tasks, success messages)
- Warning: yellow-500 (in-progress tasks)
- Danger: red-500 (delete buttons, errors)
- Background: gray-50 (page background)

### Typography
- Headings: font-bold with appropriate sizing
- Body: font-normal with good readability
- Monospace: For code snippets and technical data
- Line height: 1.5 for readability

### Spacing
- Consistent padding using Tailwind scale (px-4, py-2)
- Vertical rhythm with margin utilities
- Responsive gutters that adapt to screen size

### Responsive Breakpoints
- Mobile: up to 768px (stacked layouts)
- Tablet: 768px - 1024px (moderate columns)
- Desktop: 1024px+ (full column layouts)

---

## Component Hierarchy

```
App Layout
├── Header
├── Main Content Area
│   ├── AuthForm (when not authenticated)
│   └── TaskList (when authenticated)
│       ├── TaskForm (for adding/editing)
│       ├── Filter Controls
│       └── TaskCard x N
└── Footer
```

---

## Implementation Checklist

### Reusability
- [ ] All props typed with TypeScript interfaces
- [ ] Default props provided where appropriate
- [ ] Component composition over duplication
- [ ] Shared utility functions extracted

### Accessibility
- [ ] Semantic HTML elements used appropriately
- [ ] Proper ARIA labels for interactive elements
- [ ] Keyboard navigation support
- [ ] Screen reader compatibility
- [ ] Sufficient color contrast ratios

### Performance
- [ ] Server components by default
- [ ] Client components only for interactivity
- [ ] Lazy loading for heavy components
- [ ] Memoization for expensive renders
- [ ] Efficient prop drilling avoided

### Responsive Design
- [ ] Mobile-first approach
- [ ] Touch-friendly targets (min 44px)
- [ ] Adaptable layouts for all screen sizes
- [ ] Appropriate font sizing
- [ ] Gesture support where needed

### Error Handling
- [ ] Loading states implemented
- [ ] Error boundaries for crashes
- [ ] Graceful degradation for network failures
- [ ] User-friendly error messages
- [ ] Retry mechanisms where appropriate