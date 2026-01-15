// mcp-server/server.js
// Complete server initialization

const config = require('./config');
const todoRoutes = require('./routes/todos');
const contextRoutes = require('./routes/context');
const healthRoutes = require('./health');
const { authenticateApiKey } = require('./middleware/socketAuth');
const { db } = require('../src/config/database'); // Connect to main app's database

// Setup all necessary routes
const setupServer = (app) => {
  // Health check routes (public)
  app.use('/health', healthRoutes);

  // MCP routes (require API key)
  app.use('/mcp/todos', authenticateApiKey, todoRoutes);
  app.use('/mcp/context', authenticateApiKey, contextRoutes);

  // Error handling middleware
  app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong in MCP server!' });
  });

  // Start server on configured port
  const server = app.listen(config.port, () => {
    console.log(`MCP Server is running on port ${config.port}`);
  });

  // Setup graceful shutdown
  process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
      console.log('Process terminated');
    });
  });

  process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    server.close(() => {
      console.log('Process terminated');
    });
  });
};

module.exports = { setupServer };