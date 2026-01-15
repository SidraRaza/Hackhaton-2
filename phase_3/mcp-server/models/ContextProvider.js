// mcp-server/models/ContextProvider.js
// Aggregate user data for AI models

const { db } = require('../../src/config/database');
const TodoAdapter = require('./TodoAdapter');

class ContextProvider {
  static async getUserContext(userId) {
    try {
      // Get user profile info
      const userSql = 'SELECT id, email, name, created_at FROM users WHERE id = ?';
      const user = await new Promise((resolve, reject) => {
        db.get(userSql, [userId], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });

      if (!user) {
        throw new Error('User not found');
      }

      // Get user's todos count and stats
      const todos = await TodoAdapter.getAllTodos(userId);
      const todoStats = {
        total: todos.length,
        completed: todos.filter(todo => todo.completed).length,
        pending: todos.filter(todo => !todo.completed).length
      };

      // Get recent activity
      const recentActivitySql = `
        SELECT timestamp, content, role
        FROM chat_messages cm
        JOIN chat_sessions cs ON cm.session_id = cs.id
        WHERE cs.user_id = ?
        ORDER BY cm.timestamp DESC
        LIMIT 5
      `;

      const recentActivity = await new Promise((resolve, reject) => {
        db.all(recentActivitySql, [userId], (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      return {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          joinedDate: user.created_at
        },
        todoStats,
        recentActivity,
        lastActive: recentActivity.length > 0 ? recentActivity[0].timestamp : null
      };
    } catch (error) {
      throw error;
    }
  }

  static async getUserTodos(userId) {
    try {
      return await TodoAdapter.getAllTodos(userId);
    } catch (error) {
      throw error;
    }
  }

  static async getUserChatHistory(userId, limit = 10) {
    try {
      const sql = `
        SELECT cm.id, cm.session_id, cm.role, cm.content, cm.timestamp, cs.title as session_title
        FROM chat_messages cm
        JOIN chat_sessions cs ON cm.session_id = cs.id
        WHERE cs.user_id = ?
        ORDER BY cm.timestamp DESC
        LIMIT ?
      `;

      const chatHistory = await new Promise((resolve, reject) => {
        db.all(sql, [userId, limit], (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      return chatHistory;
    } catch (error) {
      throw error;
    }
  }

  static formatForAIModel(data) {
    try {
      const formatted = {
        userInfo: {
          id: data.user?.id,
          name: data.user?.name,
          email: data.user?.email
        },
        todos: data.todoStats ? {
          total: data.todoStats.total,
          completed: data.todoStats.completed,
          pending: data.todoStats.pending,
          items: data.todos || []
        } : null,
        recentActivity: data.recentActivity || [],
        lastActive: data.lastActive
      };

      return formatted;
    } catch (error) {
      throw error;
    }
  }
}

module.exports = ContextProvider;