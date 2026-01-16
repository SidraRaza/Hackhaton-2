# Quickstart Guide: UI Enhancements for Next.js Frontend

## Prerequisites

- Node.js 18+ for frontend development
- Git for version control

## Setup Instructions

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 3. Environment Configuration

The UI enhancements don't require additional environment variables beyond the existing ones, but ensure these are set:

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SERVER_URL=http://localhost:8000
```

### 4. Running the Application

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Visit http://localhost:3000 to see the enhanced UI.

## UI Enhancement Features

### Dark/Light Mode
- Toggle between themes using the moon/sun icon in the header
- System preference detection
- Persistent theme selection

### Responsive Design
- Mobile-first approach
- Adapts to different screen sizes
- Touch-friendly interface elements

### Enhanced Components
- Modern card designs with subtle shadows
- Smooth transitions and animations
- Improved form validation with visual feedback
- Loading states and skeleton screens

### Navigation
- Sticky header with user controls
- Collapsible sidebar for desktop
- Mobile hamburger menu

## Development

### Running Tests

```bash
npm test
# or
yarn test
# or
pnpm test
```

### Building for Production

```bash
npm run build
# or
yarn build
# or
pnpm build
```

### Component Development

Components are organized by functionality:
- `components/ui/` - Reusable UI primitives
- `components/layout/` - Structural components (Header, Sidebar)
- `components/auth/` - Authentication components
- `components/tasks/` - Task management components

## Troubleshooting

### Common Issues

1. **Dark Mode Not Working**
   - Verify Tailwind CSS is configured for dark mode
   - Check that `darkMode: 'class'` is set in `tailwind.config.js`

2. **Responsive Design Issues**
   - Verify Tailwind CSS is properly installed
   - Check that responsive prefixes (sm:, md:, lg:) are being applied correctly

3. **Icons Not Showing**
   - Verify `@heroicons/react` is installed
   - Check that icon components are imported correctly

4. **Component Import Issues**
   - Verify component paths are correct
   - Check that TypeScript interfaces are properly defined