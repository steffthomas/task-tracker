from flask import Flask, render_template, request, redirect
import requests
import sqlite3
import os
import time


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

_cached_quotes = []
_last_fetch_time = 0

def get_random_quotes(n=3):
    global _cached_quotes, _last_fetch_time
    now = time.time()

    # Refresh only every 5 minutes
    if not _cached_quotes or now - _last_fetch_time > 300:
        _cached_quotes = []
        seen = set()

        while len(_cached_quotes) < n:
            try:
                res = requests.get("https://zenquotes.io/api/random", timeout=3)
                if res.status_code == 200:
                    data = res.json()[0]
                    quote = f'"{data["q"]}" — {data["a"]}'
                    if quote not in seen:
                        _cached_quotes.append(quote)
                        seen.add(quote)
                else:
                    print("ZenQuotes API error:", res.status_code)
                    break
            except:
                print("ZenQuotes failed.")
                break

        _last_fetch_time = now

    # Fallback or pad if API failed
    return _cached_quotes[:n] if _cached_quotes else [
        "Believe in yourself.",
        "You’ve got this.",
        "Keep going. You're doing great!"
    ]

@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    random_quotes = get_random_quotes()
    return render_template('index.html', tasks=tasks, quotes=random_quotes)


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
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
