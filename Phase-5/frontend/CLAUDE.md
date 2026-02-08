# CLAUDE.md
## Frontend Service: Advanced Cloud Deployment

### Service Context
Frontend application for Phase V: Advanced Cloud Deployment featuring enhanced UI with priority indicators, tag management, search/filter capabilities, recurrence patterns, and due date handling with event-driven synchronization.

### Technology Stack
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React hooks, Zustand (optional), React Query/SWR
- **Forms**: React Hook Form with Zod validation
- **Icons**: Lucide React
- **Testing**: Jest, React Testing Library, Playwright (e2e)
- **Build Tool**: Webpack/Vite with Next.js defaults

### Key Components
- `/src/app`: Next.js 14 App Router pages and layouts
- `/src/components`: Reusable UI components including task features
- `/src/components/task`: Task-specific components with advanced features
- `/src/components/search`: Advanced search and filter components
- `/src/components/chat`: Enhanced chatbot interface with advanced understanding
- `/src/lib`: Utility functions and API clients
- `/src/hooks`: Custom React hooks for advanced features
- `/src/services`: Service layers for data management
- `/src/types`: TypeScript type definitions for advanced features

### Advanced Features Implemented
- **Priority System**: Visual indicators (color-coded), priority selection UI, filtering/sorting
- **Tag Management**: Tag input with autocomplete, tag creation, tag filtering
- **Search & Filter**: Full-text search, multi-criteria filtering, saved filters
- **Sorting**: Multi-column sorting with primary/secondary criteria, sort persistence
- **Recurring Tasks**: Recurrence pattern selector, series management UI
- **Due Dates & Reminders**: Date/time picker with timezone handling, reminder configuration
- **Real-time Sync**: Event-driven updates from backend services
- **Responsive Design**: Mobile-first with desktop enhancements

### UI Components
- `PrioritySelector.tsx`: Interactive priority selection with visual indicators
- `TagInput.tsx`: Tag management with autocomplete and creation
- `AdvancedFilterPanel.tsx`: Multi-criteria filtering interface
- `RecurrencePatternSelector.tsx`: UI for selecting recurrence patterns
- `DateTimePicker.tsx`: Date and time selection with timezone support
- `TaskList.tsx`: Enhanced with priority indicators, tags, filtering controls
- `TaskForm.tsx`: Extended with all advanced feature inputs
- `SearchBar.tsx`: Advanced search with filters and suggestions
- `SortControls.tsx`: Sorting interface with multi-column support

### API Integration
- Enhanced API client with support for priority, tags, search, sort parameters
- Real-time updates via Server-Sent Events or WebSocket
- Error handling and retry logic for event-driven operations
- Optimistic updates for better UX with eventual consistency

### Chatbot Enhancement
- Natural language understanding for priorities ("high priority task")
- Tag recognition and assignment ("add work tag")
- Date/time parsing ("due tomorrow at 3pm")
- Recurrence pattern recognition ("weekly meeting every Monday")
- Search query understanding ("find tasks about meetings")
- Sort command recognition ("show by due date")

### Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend API base URL
- `NEXT_PUBLIC_DAPR_SIDECAR_HOST`: Dapr sidecar host for service invocation
- `NEXT_PUBLIC_TODO_WEBSOCKET_URL`: WebSocket endpoint for real-time updates
- `NEXT_PUBLIC_DEFAULT_PRIORITY`: Default priority level for new tasks
- `NEXT_PUBLIC_TIMEZONE`: Default timezone for date operations

### Development Commands
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run test`: Run unit tests
- `npm run test:e2e`: Run end-to-end tests
- `npm run lint`: Run linting
- `npm run type-check`: Run TypeScript type checking

### Performance Optimizations
- Client-side caching for task data
- Virtual scrolling for large task lists
- Lazy loading of components
- Code splitting for improved initial load
- Memoization for expensive computations
- Debounced search for better responsiveness