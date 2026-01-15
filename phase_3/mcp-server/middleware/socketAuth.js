// mcp-server/middleware/socketAuth.js
// API key authentication for MCP server

const config = require('../config');

const authenticateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'] || req.query.api_key;

  if (!apiKey || apiKey !== config.apiKey) {
    return res.status(401).json({
      error: 'Unauthorized: Invalid API key'
    });
  }

  next();
};

module.exports = { authenticateApiKey };