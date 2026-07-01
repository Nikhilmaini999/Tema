"""To-Do List Application with Local Storage."""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
from dataclasses import dataclass, asdict, field
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """Task class with metadata."""
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Task {self.id} marked as completed")
    
    def mark_in_progress(self) -> None:
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Task {self.id} marked as in progress")
    
    def update(self, **kwargs) -> None:
        """Update task fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'due_date': self.due_date,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())[:8]),
            title=data['title'],
            description=data.get('description', ''),
            priority=TaskPriority(data.get('priority', 2)),
            status=TaskStatus(data.get('status', 'pending')),
            due_date=data.get('due_date'),
            tags=data.get('tags', []),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            completed_at=data.get('completed_at')
        )


class TodoList:
    """Main To-Do List Manager with local storage."""
    
    def __init__(self, storage_path: str = "~/.todo_app"):
        """Initialize to-do list.
        
        Args:
            storage_path: Path to store tasks JSON file
        """
        self.storage_path = os.path.expanduser(storage_path)
        self.tasks_file = os.path.join(self.storage_path, 'tasks.json')
        self.tasks: List[Task] = []
        
        # Create storage directory
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Load existing tasks
        self.load_tasks()
        logger.info(f"TodoList initialized with {len(self.tasks)} tasks")
    
    def add_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[str] = None,
        tags: List[str] = None
    ) -> Task:
        """Add a new task.
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority
            due_date: Due date (ISO format)
            tags: List of tags
        
        Returns:
            Created Task object
        """
        if tags is None:
            tags = []
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags
        )
        
        self.tasks.append(task)
        self.save_tasks()
        logger.info(f"Task '{title}' added with ID {task.id}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task object or None
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """Update task fields.
        
        Args:
            task_id: Task ID
            **kwargs: Fields to update
        
        Returns:
            Updated Task or None
        """
        task = self.get_task(task_id)
        if task:
            task.update(**kwargs)
            self.save_tasks()
            logger.info(f"Task {task_id} updated")
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if deleted, False if not found
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self.save_tasks()
                logger.info(f"Task {task_id} deleted")
                return True
        return False
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks filtered by status.
        
        Args:
            status: Task status
        
        Returns:
            List of tasks with matching status
        """
        return [task for task in self.tasks if task.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Get tasks filtered by priority.
        
        Args:
            priority: Task priority
        
        Returns:
            List of tasks with matching priority
        """
        return [task for task in self.tasks if task.priority == priority]
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get tasks filtered by tag.
        
        Args:
            tag: Tag name
        
        Returns:
            List of tasks with matching tag
        """
        return [task for task in self.tasks if tag in task.tags]
    
    def get_tasks_by_date(self, date: str) -> List[Task]:
        """Get tasks due on specific date.
        
        Args:
            date: Date in ISO format (YYYY-MM-DD)
        
        Returns:
            List of tasks due on that date
        """
        return [task for task in self.tasks if task.due_date == date]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks.
        
        Returns:
            List of overdue tasks
        """
        today = datetime.now().date().isoformat()
        overdue = []
        
        for task in self.tasks:
            if task.due_date and task.due_date < today and task.status != TaskStatus.COMPLETED:
                overdue.append(task)
        
        return sorted(overdue, key=lambda t: t.due_date)
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description.
        
        Args:
            query: Search query
        
        Returns:
            List of matching tasks
        """
        query_lower = query.lower()
        return [
            task for task in self.tasks
            if query_lower in task.title.lower() or query_lower in task.description.lower()
        ]
    
    def get_statistics(self) -> Dict:
        """Get task statistics.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.tasks)
        completed = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        pending = len(self.get_tasks_by_status(TaskStatus.PENDING))
        in_progress = len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS))
        
        priority_counts = {
            'urgent': len(self.get_tasks_by_priority(TaskPriority.URGENT)),
            'high': len(self.get_tasks_by_priority(TaskPriority.HIGH)),
            'medium': len(self.get_tasks_by_priority(TaskPriority.MEDIUM)),
            'low': len(self.get_tasks_by_priority(TaskPriority.LOW))
        }
        
        return {
            'total_tasks': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'overdue': len(self.get_overdue_tasks()),
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'by_priority': priority_counts
        }
    
    def save_tasks(self) -> bool:
        """Save tasks to JSON file.
        
        Returns:
            True if successful
        """
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.tasks_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.tasks)} tasks to {self.tasks_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")
            return False
    
    def load_tasks(self) -> bool:
        """Load tasks from JSON file.
        
        Returns:
            True if successful
        """
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                self.tasks = [Task.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self.tasks)} tasks from {self.tasks_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
            return False
    
    def export_tasks(self, filepath: str, status_filter: Optional[TaskStatus] = None) -> bool:
        """Export tasks to JSON file.
        
        Args:
            filepath: Export file path
            status_filter: Optional status filter
        
        Returns:
            True if successful
        """
        try:
            tasks = self.tasks
            if status_filter:
                tasks = self.get_tasks_by_status(status_filter)
            
            data = [task.to_dict() for task in tasks]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Exported {len(tasks)} tasks to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export tasks: {e}")
            return False
    
    def import_tasks(self, filepath: str, merge: bool = True) -> bool:
        """Import tasks from JSON file.
        
        Args:
            filepath: Import file path
            merge: Whether to merge with existing tasks
        
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            imported_tasks = [Task.from_dict(item) for item in data]
            
            if not merge:
                self.tasks = []
            
            self.tasks.extend(imported_tasks)
            self.save_tasks()
            logger.info(f"Imported {len(imported_tasks)} tasks from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to import tasks: {e}")
            return False
    
    def print_tasks(self, tasks: Optional[List[Task]] = None) -> None:
        """Print tasks in formatted table.
        
        Args:
            tasks: List of tasks to print (uses all if None)
        """
        if tasks is None:
            tasks = self.tasks
        
        if not tasks:
            print("No tasks found.")
            return
        
        print("\n" + "="*100)
        print(f"{'ID':<8} {'Title':<25} {'Priority':<10} {'Status':<15} {'Due Date':<12} {'Tags':<20}")
        print("="*100)
        
        for task in tasks:
            priority_name = task.priority.name
            status_name = task.status.value.replace('_', ' ').title()
            tags_str = ', '.join(task.tags) if task.tags else '-'
            due_date = task.due_date or '-'
            
            print(f"{task.id:<8} {task.title:<25} {priority_name:<10} {status_name:<15} {due_date:<12} {tags_str:<20}")
        
        print("="*100 + "\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='To-Do List Application')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('--desc', default='', help='Task description')
    add_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'urgent'], default='medium')
    add_parser.add_argument('--due', help='Due date (YYYY-MM-DD)')
    add_parser.add_argument('--tags', nargs='+', default=[], help='Tags')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed', 'archived'])
    list_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'urgent'])
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--overdue', action='store_true', help='Show overdue tasks')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
    complete_parser.add_argument('task_id', help='Task ID')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete task')
    delete_parser.add_argument('task_id', help='Task ID')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search tasks')
    search_parser.add_argument('query', help='Search query')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export tasks')
    export_parser.add_argument('filepath', help='Export file path')
    
    args = parser.parse_args()
    todo = TodoList()
    
    if args.command == 'add':
        priority = TaskPriority[args.priority.upper()]
        todo.add_task(
            title=args.title,
            description=args.desc,
            priority=priority,
            due_date=args.due,
            tags=args.tags
        )
        print(f"Task added: {args.title}")
    
    elif args.command == 'list':
        tasks = todo.tasks
        
        if args.status:
            tasks = todo.get_tasks_by_status(TaskStatus(args.status))
        elif args.priority:
            tasks = todo.get_tasks_by_priority(TaskPriority[args.priority.upper()])
        elif args.tag:
            tasks = todo.get_tasks_by_tag(args.tag)
        elif args.overdue:
            tasks = todo.get_overdue_tasks()
        
        todo.print_tasks(tasks)
    
    elif args.command == 'complete':
        task = todo.get_task(args.task_id)
        if task:
            task.mark_completed()
            todo.save_tasks()
            print(f"Task {args.task_id} marked as completed")
        else:
            print(f"Task {args.task_id} not found")
    
    elif args.command == 'delete':
        if todo.delete_task(args.task_id):
            print(f"Task {args.task_id} deleted")
        else:
            print(f"Task {args.task_id} not found")
    
    elif args.command == 'search':
        results = todo.search_tasks(args.query)
        todo.print_tasks(results)
    
    elif args.command == 'stats':
        stats = todo.get_statistics()
        print("\n" + "="*50)
        print("TASK STATISTICS")
        print("="*50)
        print(f"Total Tasks: {stats['total_tasks']}")
        print(f"Completed: {stats['completed']}")
        print(f"Pending: {stats['pending']}")
        print(f"In Progress: {stats['in_progress']}")
        print(f"Overdue: {stats['overdue']}")
        print(f"Completion Rate: {stats['completion_rate']:.1f}%")
        print(f"\nBy Priority:")
        print(f"  Urgent: {stats['by_priority']['urgent']}")
        print(f"  High: {stats['by_priority']['high']}")
        print(f"  Medium: {stats['by_priority']['medium']}")
        print(f"  Low: {stats['by_priority']['low']}")
        print("="*50 + "\n")
    
    elif args.command == 'export':
        if todo.export_tasks(args.filepath):
            print(f"Tasks exported to {args.filepath}")
        else:
            print("Export failed")


if __name__ == '__main__':
    main()
