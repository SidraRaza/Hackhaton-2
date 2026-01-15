// mcp-server/health.js
// Health check endpoints for monitoring

const express = require('express');
const router = express.Router();
const { db } = require('../src/config/database');

// GET /health - Return server status
router.get('/', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'MCP Server',
    uptime: process.uptime()
  });
});

// GET /health/db - Check database connectivity
router.get('/db', (req, res) => {
  // Try a simple query to check database connection
  db.get('SELECT 1 as test', [], (err, row) => {
    if (err) {
      console.error('Database connection error:', err);
      res.status(503).json({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        service: 'Database',
        error: err.message
      });
    } else {
      res.status(200).json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'Database',
        details: row
      });
    }
  });
});

// GET /health/api - Check external API availability (placeholder)
router.get('/api', (req, res) => {
  // This would check external API availability like OpenAI
  // For now, we'll just return healthy as a placeholder
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'External APIs',
    details: 'Placeholder - would check external API availability'
  });
});

module.exports = router;