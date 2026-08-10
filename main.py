from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from pydantic import BaseModel

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
# IN-MEMORY data store
# ============================================================

list_of_tasks = [
    { "id": 1, "title": "Go Gym", "done": False },
    { "id": 2, "title": "Buy Groceries", "done": False },
    { "id": 3, "title": "Walk the Dog", "done": False }
]

next_id = 4

# ============================================================
# Stage 1 root and health endpoints
# ============================================================

app = FastAPI()

@app.get("/", summary="Root endpoint", description="Returns basic information about the API")
def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health", summary="Health check endpoint", description="Returns the health status of the API")
def health():
    return { "status": "ok" }

# ============================================================
# Stage 2 read endpoints with error handling
# ============================================================

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.get("/tasks", response_model = list[Task], summary="Get all tasks", description="Returns a list of all tasks")
def get_tasks():
    return list_of_tasks


@app.get("/tasks/{id}", response_model=Task, summary="Get a task by ID", description="Returns a single task by its ID")
def get_task(id: int):
    for task_stored in list_of_tasks:
        if task_stored["id"] == id:
            return task_stored
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

# ============================================================
# Stage 3 create endpoint with validation
# ============================================================

@app.post("/tasks", status_code=201, summary="Create a new task", description="Creates a new task with the provided title")
def create_task(task: TaskCreate):

    if not task.title or not task.title.strip():
            raise HTTPException(status_code=400, detail="Title is missing")

    global next_id
    new_task = {
        "id": next_id,
        "title": task.title,
        "done": False
    }
    next_id += 1

    list_of_tasks.append(new_task)
    return new_task

# ============================================================
# Stage 4 update and delete endpoints
# ============================================================

@app.put("/tasks/{id}", status_code=200, summary="Update a task", description="Updates a task with the provided ID")
def update_task(id: int, task: TaskUpdate):

    if task.title is None and task.done is None: 
        raise HTTPException(status_code=400, detail="Done status is missing")
    
    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing")
    
    for task_stored in list_of_tasks:
        
        if task_stored["id"] == id:

            if task.title is not None:
                task_stored["title"] = task.title

            if task.done is not None:
                task_stored["done"] = task.done
            
            return task_stored
    
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task", description="Deletes a task with the provided ID")
def delete_task(id: int):
    for task_stored in list_of_tasks:
        if task_stored["id"] == id:
            list_of_tasks.remove(task_stored)
            return
    raise HTTPException(status_code=404, detail=f"Task {id} not found")