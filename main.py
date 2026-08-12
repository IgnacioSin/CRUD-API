from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import db

# ============================================================
# Base models
# ============================================================

class TaskCreate(BaseModel):
    title: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

class Task(BaseModel):
    id: int
    title: str
    done: bool

# ============================================================
# Application initialization
# ============================================================

app = FastAPI()

db.init_db() # Initialize the database and create the tasks table if it doesn't exist

# ============================================================

@app.get("/", summary="Root endpoint", description="Returns basic information about the API")
def root():

    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

# ============================================================

@app.get("/health", summary="Health check endpoint", description="Returns the health status of the API")
def health():

    return { "status": "ok" }

# ============================================================
# Error handling
# ============================================================

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):

    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail},)

# ============================================================ #READY

@app.get("/tasks", response_model = list[Task], summary="Get all tasks", description="Returns a list of all tasks")
def get_tasks():

    tasks = db.get_tasks()
    return tasks

# ============================================================ #READY

@app.get("/tasks/{id}", response_model=Task, summary="Get a task by ID", description="Returns a single task by its ID")
def get_task(id: int):
    task = db.get_task_by_id(id)

    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    return task

# ============================================================ READY

@app.post("/tasks", response_model=Task, status_code=201, summary="Create a new task", description="Creates a new task with the provided title")
def create_task(task: TaskCreate):

    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing")
    
    return db.create_task(task.title)

# ============================================================ ¿READY?

@app.put("/tasks/{id}", response_model=Task, status_code=200, summary="Update a task", description="Updates a task with the provided ID")
def update_task(id: int, task: TaskUpdate):

    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="At least one of title or done must be provided")

    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing")

    updated = db.update_task(id, task.title, task.done)

    if updated is None:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    return updated

# ============================================================ READY

@app.delete("/tasks/{id}", status_code=204, summary="Delete a task", description="Deletes a task with the provided ID")
def delete_task(id: int):

    deleted_count = db.delete_task(id)

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")