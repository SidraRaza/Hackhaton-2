// mcp-server/config.js
// MCP protocol configuration

const config = {
  port: process.env.MCP_PORT || 3001,
  cors: {
    origin: '*', // In production, specify your frontend domain
    credentials: true
  },
  apiKey: process.env.MCP_API_KEY || 'your_mcp_api_key_here',
  serverName: process.env.MCP_SERVER_NAME || 'todo-chatbot-mcp',
  connectionPooling: {
    maxConnections: 100,
    idleTimeout: 30000
  }
};

module.exports = config;