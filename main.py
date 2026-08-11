from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3

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
# Database initialization
# ============================================================

def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Go Gym", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy Groceries", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Walk the Dog", 0))

    conn.commit()
    conn.close()

# ============================================================
# Stage 1 root and health endpoints
# ============================================================

app = FastAPI()

init_db() # Initialize the database and create the tasks table if it doesn't exist

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

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    tasks = []
    for row in rows:
        tasks.append({"id": row[0], "title": row[1], "done": bool(row[2])})

    conn.close()
    return tasks


@app.get("/tasks/{id}", response_model=Task, summary="Get a task by ID", description="Returns a single task by its ID")
def get_task(id: int):

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    return {"id": row[0], "title": row[1], "done": bool(row[2])}

# ============================================================
# Stage 3 create endpoint with validation
# ============================================================

@app.post("/tasks", status_code=201, summary="Create a new task", description="Creates a new task with the provided title")
def create_task(task: TaskCreate):

    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing")
    
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": task.title, "done": False}

# ============================================================
# Stage 4 update and delete endpoints
# ============================================================

@app.put("/tasks/{id}", status_code=200, summary="Update a task", description="Updates a task with the provided ID")
def update_task(id: int, task: TaskUpdate):

    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="At least one of title or done must be provided")

    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is missing")
    
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    new_title = task.title if task.title is not None else row[1]
    new_done = task.done if task.done is not None else bool(row[2])

    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, int(new_done), id))

    conn.commit()
    conn.close()

    return {"id": id, "title": new_title, "done": new_done}


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task", description="Deletes a task with the provided ID")
def delete_task(id: int):

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))

    conn.commit()
    deleted_count = cursor.rowcount
    conn.close()

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")