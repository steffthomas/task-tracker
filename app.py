from flask import Flask, render_template, request, redirect
import sqlite3
import os


app = Flask(__name__)

# Temporary list to store tasks
tasks = []

DB_NAME = 'todo.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            );
        ''')
        conn.commit()
        conn.close()

# Call it at startup
init_db()


@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (title) VALUES (?)', (title,))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add.html')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()

    if request.method == 'POST':
        new_title = request.form['title']
        conn.execute('UPDATE tasks SET title = ? WHERE id = ?', (new_title, task_id))
        conn.commit()
        conn.close()
        return redirect('/')

    conn.close()
    return render_template('edit.html', task=task)


if __name__ == '__main__':
    app.run(debug=True)
