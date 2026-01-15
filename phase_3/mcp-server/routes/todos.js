// mcp-server/routes/todos.js
// MCP todo management endpoints

const express = require('express');
const router = express.Router();
const TodoAdapter = require('../models/TodoAdapter');

// GET /mcp/todos - Return user's todos in MCP-compatible format
router.get('/', async (req, res) => {
  try {
    const { userId } = req.query;

    if (!userId) {
      return res.status(400).json({ error: 'userId parameter is required' });
    }

    const todos = await TodoAdapter.getAllTodos(userId);

    res.json({
      success: true,
      data: todos,
      message: `Retrieved ${todos.length} todos for user ${userId}`
    });
  } catch (error) {
    console.error('Error getting todos:', error);
    res.status(500).json({ error: 'Failed to retrieve todos' });
  }
});

// POST /mcp/todos - Create new todo via TodoAdapter
router.post('/', async (req, res) => {
  try {
    const { userId, title, description } = req.body;

    if (!userId || !title) {
      return res.status(400).json({
        error: 'userId and title are required'
      });
    }

    const newTodo = await TodoAdapter.createTodo(userId, title, description);

    res.status(201).json({
      success: true,
      data: newTodo,
      message: 'Todo created successfully'
    });
  } catch (error) {
    console.error('Error creating todo:', error);
    res.status(500).json({ error: 'Failed to create todo' });
  }
});

// PUT /mcp/todos/:id - Update todo via TodoAdapter
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;

    // Only allow specific fields to be updated
    const allowedUpdates = {};
    if (updates.title !== undefined) allowedUpdates.title = updates.title;
    if (updates.description !== undefined) allowedUpdates.description = updates.description;
    if (updates.completed !== undefined) allowedUpdates.completed = updates.completed;

    const updatedTodo = await TodoAdapter.updateTodo(parseInt(id), allowedUpdates);

    res.json({
      success: true,
      data: updatedTodo,
      message: 'Todo updated successfully'
    });
  } catch (error) {
    console.error('Error updating todo:', error);
    if (error.message === 'Todo not found') {
      res.status(404).json({ error: 'Todo not found' });
    } else {
      res.status(500).json({ error: 'Failed to update todo' });
    }
  }
});

// DELETE /mcp/todos/:id - Delete todo via TodoAdapter
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await TodoAdapter.deleteTodo(parseInt(id));

    res.json({
      success: true,
      data: result,
      message: 'Todo deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting todo:', error);
    if (error.message === 'Todo not found') {
      res.status(404).json({ error: 'Todo not found' });
    } else {
      res.status(500).json({ error: 'Failed to delete todo' });
    }
  }
});

module.exports = router;