// mcp-server/index.js
// Main MCP server entry point

const express = require('express');
const cors = require('cors');
const config = require('./config');
const { setupServer } = require('./server');

const app = express();

// Middleware
app.use(cors(config.cors));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Basic health check endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'MCP Server for AI-Powered Todo Chatbot is running!',
    serverName: config.serverName,
    status: 'healthy'
  });
});

// Start the server
setupServer(app);

module.exports = app;