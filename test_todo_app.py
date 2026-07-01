"""Tests for To-Do List Application."""

import pytest
import os
import tempfile
import json
from datetime import datetime, timedelta
from todo_app import TodoList, Task, TaskStatus, TaskPriority


class TestTask:
    """Test Task class."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH
        )
        
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
    
    def test_task_completion(self):
        """Test marking task as completed."""
        task = Task(title="Test")
        assert task.status == TaskStatus.PENDING
        
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
    
    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(title="Test", tags=["important"])
        data = task.to_dict()
        
        assert data['title'] == "Test"
        assert data['tags'] == ["important"]
        assert 'id' in data


class TestTodoList:
    """Test TodoList class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def todo_list(self, temp_storage):
        """Create todo list with temporary storage."""
        return TodoList(storage_path=temp_storage)
    
    def test_add_task(self, todo_list):
        """Test adding a task."""
        task = todo_list.add_task(
            title="Test Task",
            description="Test Description"
        )
        
        assert task.title == "Test Task"
        assert len(todo_list.tasks) == 1
    
    def test_delete_task(self, todo_list):
        """Test deleting a task."""
        task = todo_list.add_task(title="Delete Me")
        assert len(todo_list.tasks) == 1
        
        deleted = todo_list.delete_task(task.id)
        assert deleted is True
        assert len(todo_list.tasks) == 0
    
    def test_search_tasks(self, todo_list):
        """Test searching tasks."""
        todo_list.add_task(title="Python Project", description="Learn Python")
        todo_list.add_task(title="JavaScript Task", description="Learn JS")
        
        results = todo_list.search_tasks("Python")
        assert len(results) == 1
        assert results[0].title == "Python Project"
    
    def test_save_and_load(self, temp_storage):
        """Test saving and loading tasks."""
        todo1 = TodoList(storage_path=temp_storage)
        todo1.add_task(title="Task 1")
        todo1.add_task(title="Task 2")
        
        todo2 = TodoList(storage_path=temp_storage)
        assert len(todo2.tasks) == 2
        assert todo2.tasks[0].title == "Task 1"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
