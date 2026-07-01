# To-Do List Application

A feature-rich to-do list application with local storage, task prioritization, and comprehensive task management.

## Features

✅ **Task Management**
- Create, read, update, delete tasks
- Mark tasks as completed, in progress, pending, or archived
- Set task priorities (Low, Medium, High, Urgent)
- Add due dates and tags

✅ **Filtering & Search**
- Filter by status, priority, or tags
- Search tasks by title or description
- View overdue tasks
- Custom date-based filtering

✅ **Local Storage**
- Automatic JSON file storage
- Load/save tasks on startup/shutdown
- Export tasks to JSON
- Import tasks from JSON files

✅ **Statistics**
- Task completion rate
- Count by priority and status
- Overdue task tracking

## Installation

```bash
pip install pytest
```

## Usage

### Add a Task
```bash
python todo_app.py add "Buy groceries" --desc "Milk, eggs, bread" --priority high --due 2024-01-15 --tags shopping

python todo_app.py add "Finish project" --priority urgent --tags work
```

### List Tasks
```bash
# List all tasks
python todo_app.py list

# Filter by status
python todo_app.py list --status pending

# Filter by priority
python todo_app.py list --priority high

# Show overdue tasks
python todo_app.py list --overdue
```

### Complete a Task
```bash
python todo_app.py complete <task_id>
```

### Delete a Task
```bash
python todo_app.py delete <task_id>
```

### Search Tasks
```bash
python todo_app.py search "groceries"
```

### View Statistics
```bash
python todo_app.py stats
```

### Export Tasks
```bash
python todo_app.py export tasks_backup.json
```

## Data Persistence

Tasks are automatically saved to `~/.todo_app/tasks.json`

## Running Tests

```bash
pytest test_todo_app.py -v
```

## License

MIT License
