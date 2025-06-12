from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Temporary list to store tasks
tasks = []

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        tasks.append({'id': len(tasks), 'title': title})
        return redirect('/')
    return render_template('add.html')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return "Task not found", 404

    if request.method == 'POST':
        new_title = request.form['title']
        task['title'] = new_title
        return redirect('/')

    return render_template('edit.html', task=task)


if __name__ == '__main__':
    app.run(debug=True)
