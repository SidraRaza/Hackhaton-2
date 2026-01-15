// mcp-server/models/TodoAdapter.js
// Connect to main application's database

const { db } = require('../../src/config/database');

class TodoAdapter {
  static getAllTodos(userId) {
    return new Promise((resolve, reject) => {
      const sql = `
        SELECT id, title, description, completed, created_at
        FROM todos
        WHERE user_id = ?
        ORDER BY created_at DESC
      `;

      db.all(sql, [userId], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  static createTodo(userId, title, description) {
    return new Promise((resolve, reject) => {
      const sql = `
        INSERT INTO todos (user_id, title, description, completed)
        VALUES (?, ?, ?, ?)
      `;

      db.run(sql, [userId, title, description || null, false], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({
            id: this.lastID,
            user_id: userId,
            title,
            description: description || null,
            completed: false,
            created_at: new Date().toISOString()
          });
        }
      });
    });
  }

  static updateTodo(id, updates) {
    return new Promise((resolve, reject) => {
      // Prepare the SET clause dynamically based on provided updates
      const updateFields = [];
      const params = [];

      if (updates.title !== undefined) {
        updateFields.push('title = ?');
        params.push(updates.title);
      }

      if (updates.description !== undefined) {
        updateFields.push('description = ?');
        params.push(updates.description);
      }

      if (updates.completed !== undefined) {
        updateFields.push('completed = ?');
        params.push(updates.completed);
      }

      if (updateFields.length === 0) {
        reject(new Error('No fields to update'));
        return;
      }

      params.push(id); // Add ID for WHERE clause

      const sql = `UPDATE todos SET ${updateFields.join(', ')} WHERE id = ?`;

      db.run(sql, params, function(err) {
        if (err) {
          reject(err);
        } else if (this.changes === 0) {
          reject(new Error('Todo not found'));
        } else {
          // Get the updated todo
          const getSql = 'SELECT * FROM todos WHERE id = ?';
          db.get(getSql, [id], (err, row) => {
            if (err) {
              reject(err);
            } else {
              resolve(row);
            }
          });
        }
      });
    });
  }

  static deleteTodo(id) {
    return new Promise((resolve, reject) => {
      const sql = 'DELETE FROM todos WHERE id = ?';

      db.run(sql, [id], function(err) {
        if (err) {
          reject(err);
        } else if (this.changes === 0) {
          reject(new Error('Todo not found'));
        } else {
          resolve({ id, status: 'deleted' });
        }
      });
    });
  }

  static toggleTodoCompletion(id) {
    return new Promise((resolve, reject) => {
      const toggleSql = 'UPDATE todos SET completed = NOT completed WHERE id = ?';

      db.run(toggleSql, [id], function(err) {
        if (err) {
          reject(err);
        } else if (this.changes === 0) {
          reject(new Error('Todo not found'));
        } else {
          // Get the updated todo
          const getSql = 'SELECT * FROM todos WHERE id = ?';
          db.get(getSql, [id], (err, row) => {
            if (err) {
              reject(err);
            } else {
              resolve(row);
            }
          });
        }
      });
    });
  }
}

module.exports = TodoAdapter;