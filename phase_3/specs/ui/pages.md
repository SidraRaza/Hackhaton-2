# UI Pages Specification

> **Feature**: Page Structure and Layout
> **Phase**: II
> **Status**: Ready for Implementation

## Overview

Define the page structure and layout for the Hackathon II Todo App using Next.js App Router. Each page follows responsive design principles with appropriate data fetching and error handling patterns.

## Related Specs

- `@specs/features/task-crud.md` - Task page requirements
- `@specs/features/authentication.md` - Auth page requirements
- `@specs/ui/components.md` - Component composition
- `@specs/ui/enhancements.md` - UI improvements and enhancements
- `@specs/api/rest-endpoints.md` - Data fetching requirements

---

## Page Definitions

### 1. Home Page (`/`)

**Purpose**: Landing page for unauthenticated users

**Components Used**:
- Header (guest mode)
- Hero section with app description
- AuthForm (login mode by default)

**Server-Side Logic**:
- Redirect authenticated users to dashboard
- Fetch public content (if any)

**Client-Side Interactions**:
- Switch between login/register modes
- Form submission handlers

**Responsive Behavior**:
- Mobile: Single column, centered content
- Desktop: Wider content area with balanced spacing

**Error Handling**:
- Display authentication errors
- Network error fallback

### 2. Login Page (`/auth/login`)

**Purpose**: User authentication entry point

**Components Used**:
- Header (guest mode)
- AuthForm (login mode)
- Link to register page

**Server-Side Logic**:
- Redirect authenticated users to dashboard
- Handle JWT token storage

**Client-Side Interactions**:
- Login form submission
- Mode switching to registration
- Input validation

**Responsive Behavior**:
- Mobile: Full-width form
- Desktop: Constrained width for better focus

**Error Handling**:
- Invalid credentials error
- Network connectivity errors
- Redirect to dashboard on success

### 3. Register Page (`/auth/register`)

**Purpose**: New user account creation

**Components Used**:
- Header (guest mode)
- AuthForm (register mode)
- Link to login page

**Server-Side Logic**:
- Redirect authenticated users to dashboard
- Handle JWT token storage after registration

**Client-Side Interactions**:
- Registration form submission
- Mode switching to login
- Input validation

**Responsive Behavior**:
- Mobile: Full-width form with stacked inputs
- Desktop: Optimized input spacing

**Error Handling**:
- Duplicate email/username errors
- Validation errors
- Network connectivity issues
- Redirect to dashboard on success

### 4. Dashboard Page (`/dashboard`)

**Purpose**: Main application interface for authenticated users

**Components Used**:
- Header (authenticated mode)
- TaskForm (for creating new tasks)
- TaskList (with filtering/sorting)
- Stats summary (optional)

**Server-Side Logic**:
- Redirect unauthenticated users to login
- Fetch user's tasks
- Verify JWT validity

**Client-Side Interactions**:
- Task creation, editing, deletion
- Status toggling
- Filtering and sorting controls
- Real-time updates

**Responsive Behavior**:
- Mobile: Stacked layout with collapsible filters
- Desktop: Sidebar or top-aligned controls

**Error Handling**:
- Unauthorized access (invalid JWT)
- Task loading errors
- Task operation failures

### 5. Task Detail Page (`/tasks/[id]`)

**Purpose**: View and edit individual task details

**Components Used**:
- Header (authenticated mode)
- TaskCard (expanded view)
- TaskForm (pre-filled with task data)

**Server-Side Logic**:
- Redirect unauthenticated users to login
- Fetch specific task by ID
- Verify user owns the task

**Client-Side Interactions**:
- Task editing
- Status toggling
- Deletion confirmation

**Responsive Behavior**:
- Mobile: Single column layout
- Desktop: Side-by-side edit view

**Error Handling**:
- Task not found (404)
- Unauthorized access to task
- Update/delete operation failures

### 6. Profile Page (`/profile`)

**Purpose**: User profile management

**Components Used**:
- Header (authenticated mode)
- Profile form
- Security settings
- Account management options

**Server-Side Logic**:
- Redirect unauthenticated users to login
- Fetch user profile data
- Handle profile updates

**Client-Side Interactions**:
- Profile editing
- Password change
- Account deletion confirmation

**Responsive Behavior**:
- Mobile: Vertical form layout
- Desktop: Sectioned layout with sidebar

**Error Handling**:
- Profile update failures
- Unauthorized access
- Validation errors

---

## Layout Structure

### Root Layout (`app/layout.tsx`)
```tsx
<html lang="en">
  <body className="min-h-screen bg-gray-50">
    <AuthProvider>
      <TasksProvider>
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </TasksProvider>
    </AuthProvider>
  </body>
</html>
```

### Page Layout Patterns

#### Authenticated Pages
```
AuthenticatedLayout
├── Header (with user menu)
├── Main Content
│   └── Page-specific components
└── Footer (optional)
```

#### Guest Pages
```
GuestLayout
├── Header (with auth links)
├── Main Content
│   └── Page-specific components
└── Footer (optional)
```

---

## Data Fetching Patterns

### Server-Side Data Fetching
- Use `generateMetadata` for dynamic titles
- Pre-fetch essential data in page components
- Handle loading states with skeleton screens

### Client-Side Data Fetching
- Use React Query or SWR for caching
- Implement optimistic updates
- Handle network retries

### Error Boundaries
- Per-page error boundaries
- Global error boundary for unexpected errors
- User-friendly error messages with actions

---

## Navigation Patterns

### Client-Side Navigation
- Use `next/link` for internal navigation
- Prefetch popular routes
- Handle navigation state with `next/router`

### Authentication-Based Navigation
- Automatic redirects based on auth status
- Protected route patterns
- Session timeout handling

---

## SEO and Metadata

### Page Titles
- Dynamic titles based on content
- Brand name suffix for consistency
- Unread notification counts

### Meta Tags
- Description tags for social sharing
- Open Graph tags for rich previews
- Twitter Card integration

---

## Performance Considerations

### Loading States
- Skeleton screens for content loading
- Optimistic updates for user actions
- Progressive enhancement for JS-disabled

### Bundle Optimization
- Code splitting at page level
- Dynamic imports for heavy components
- Image optimization with `next/image`

### Caching Strategies
- Static generation where possible
- Incremental static regeneration
- Client-side caching for API responses

---

## Implementation Checklist

### Page Structure
- [ ] Next.js App Router structure implemented
- [ ] Layout files created for common elements
- [ ] Page-level error boundaries
- [ ] Loading states implemented

### Navigation
- [ ] Internal linking with next/link
- [ ] Breadcrumb navigation where appropriate
- [ ] Back button handling
- [ ] Deep linking support

### Data Handling
- [ ] Server-side data fetching implemented
- [ ] Client-side data synchronization
- [ ] Error handling for data operations
- [ ] Loading state management

### Authentication Flow
- [ ] Protected route patterns implemented
- [ ] Redirects for unauthorized access
- [ ] Session management
- [ ] Logout functionality

### Responsive Design
- [ ] Mobile-first approach
- [ ] Touch-friendly navigation
- [ ] Adaptive layouts
- [ ] Accessible navigation patterns

### SEO
- [ ] Proper heading hierarchy
- [ ] Meta tags implemented
- [ ] Canonical URLs
- [ ] Structured data where appropriate