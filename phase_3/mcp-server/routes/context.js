// mcp-server/routes/context.js
// MCP chat context endpoints

const express = require('express');
const router = express.Router();
const ContextProvider = require('../models/ContextProvider');

// GET /mcp/context/:userId - Return comprehensive user context
router.get('/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    if (!userId) {
      return res.status(400).json({ error: 'userId parameter is required' });
    }

    const userContext = await ContextProvider.getUserContext(userId);
    const formattedContext = ContextProvider.formatForAIModel(userContext);

    res.json({
      success: true,
      data: formattedContext,
      message: `Retrieved context for user ${userId}`
    });
  } catch (error) {
    console.error('Error getting user context:', error);
    if (error.message === 'User not found') {
      res.status(404).json({ error: 'User not found' });
    } else {
      res.status(500).json({ error: 'Failed to retrieve user context' });
    }
  }
});

// GET /mcp/context/:userId/todos - Return user's todos in AI-friendly format
router.get('/:userId/todos', async (req, res) => {
  try {
    const { userId } = req.params;

    if (!userId) {
      return res.status(400).json({ error: 'userId parameter is required' });
    }

    const todos = await ContextProvider.getUserTodos(userId);

    res.json({
      success: true,
      data: {
        todos,
        count: todos.length,
        completed: todos.filter(todo => todo.completed).length,
        pending: todos.filter(todo => !todo.completed).length
      },
      message: `Retrieved ${todos.length} todos for user ${userId}`
    });
  } catch (error) {
    console.error('Error getting user todos:', error);
    res.status(500).json({ error: 'Failed to retrieve user todos' });
  }
});

// GET /mcp/context/:userId/chat-history - Return recent chat messages
router.get('/:userId/chat-history', async (req, res) => {
  try {
    const { userId } = req.params;
    const { limit = 10 } = req.query;

    if (!userId) {
      return res.status(400).json({ error: 'userId parameter is required' });
    }

    const chatHistory = await ContextProvider.getUserChatHistory(userId, parseInt(limit));

    res.json({
      success: true,
      data: {
        chatHistory,
        count: chatHistory.length,
        limit: parseInt(limit)
      },
      message: `Retrieved ${chatHistory.length} recent messages for user ${userId}`
    });
  } catch (error) {
    console.error('Error getting chat history:', error);
    res.status(500).json({ error: 'Failed to retrieve chat history' });
  }
});

module.exports = router;