# Quickstart Guide: Fix AI Assistant Sidebar Issue

## Prerequisites
- Node.js 18+ installed
- Git

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <repository-name>
git checkout 1-fix-ai-sidebar
```

### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your backend API URL

# Start the development server
npm run dev
```

## Key Features

### AI Assistant Sidebar Integration
- Fixed AI assistant visibility in sidebar
- Proper integration with main application content
- Responsive design for different screen sizes
- Error handling for unavailable services

### Sidebar Functionality
- Collapsible sidebar implementation
- Proper z-index and positioning
- Loading states during initialization
- Preserved user chat history

## Development Commands

### Frontend
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

## Troubleshooting

### Common Issues

1. **AI Assistant Not Visible**:
   - Check that the ChatPanel component is properly rendered in the sidebar
   - Verify that the sidebar component is not hidden by CSS
   - Confirm that the component is properly mounted

2. **Responsive Design Problems**:
   - Test on different screen sizes using browser developer tools
   - Check Tailwind CSS classes for responsive behavior
   - Verify mobile-friendly layout

3. **Service Connection Issues**:
   - Verify API endpoint configurations
   - Check network connectivity to AI service
   - Confirm error handling implementation

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AI_SERVICE_URL=https://api.openai.com
```

## Testing

### Manual Tests
1. Verify AI assistant appears in sidebar on page load
2. Test interaction with AI assistant in sidebar
3. Check sidebar behavior when collapsed/expanded
4. Test responsive behavior on different screen sizes
5. Verify error handling when AI service is unavailable