# Quickstart Guide: Fix Dependency Installation Error

## Prerequisites
- Node.js (LTS version)
- npm package manager
- Git

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Navigate to frontend directory
```bash
cd frontend
```

### 3. Install dependencies
```bash
npm install
```

> **Note**: This should now complete successfully without the @openai/assistant-runtime 404 error

### 4. Build the application
```bash
npm run build
```

> **Note**: The build should complete successfully without dependency resolution errors

### 5. Run the application
```bash
npm run dev
```

## Verification Steps

1. **Verify dependency installation**: Confirm that `npm install` completes without errors
2. **Verify build process**: Confirm that `npm run build` completes successfully
3. **Test AI functionality**: Access the dashboard and verify the AI Task Assistant works properly
4. **Check API communication**: Monitor network requests to confirm frontend-backend communication

## Troubleshooting

### Common Issues

- **Still getting dependency errors**: Ensure you have the latest frontend/package.json that removes the @openai/assistant-runtime dependency
- **AI Assistant not working**: Verify that the backend server is running and accessible at the configured API endpoint

### Environment Variables
- `NEXT_PUBLIC_API_URL`: Backend API URL (defaults to http://localhost:8000)