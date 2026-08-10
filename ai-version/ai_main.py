# ai-main.py
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task Management API",
    description="In-memory CRUD API built with FastAPI",
    version="1.0.0",
)

# ------------------------------------------------------------------------------
# Pydantic Schemas
# ------------------------------------------------------------------------------

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed task description")
    completed: bool = Field(default=False, description="Task status")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="New title")
    description: Optional[str] = Field(None, description="New description")
    completed: Optional[bool] = Field(None, description="New status")


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False


# ------------------------------------------------------------------------------
# In-Memory Database
# ------------------------------------------------------------------------------

tasks_db: dict[int, Task] = {}
id_counter: int = 1


# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------

@app.get("/tasks", response_model=List[Task], summary="Get all tasks")
def get_all_tasks():
    """Retrieve a list of all stored tasks."""
    return list(tasks_db.values())


@app.get("/tasks/{task_id}", response_model=Task, summary="Get a task by ID")
def get_task(task_id: int):
    """Retrieve details of a specific task by its ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )
    return tasks_db[task_id]


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(task_data: TaskCreate):
    """Create a new task with an auto-incremented ID."""
    global id_counter

    new_task = Task(
        id=id_counter,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
    )
    tasks_db[id_counter] = new_task
    id_counter += 1

    return new_task


@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task")
def update_task(task_id: int, task_data: TaskUpdate):
    """Update fields of an existing task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    existing_task = tasks_db[task_id]
    
    # Extract only non-null updated values provided by the client
    update_data = task_data.model_dump(exclude_unset=True)
    updated_task = existing_task.model_copy(update=update_data)

    tasks_db[task_id] = updated_task
    return updated_task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_task(task_id: int):
    """Delete a task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    del tasks_db[task_id]
    return None