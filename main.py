from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request

list_of_tasks = [
    { "id": 1, "title": "Go Gym", "done": False },
    { "id": 2, "title": "Buy Groceries", "done": False },
    { "id": 3, "title": "Walk the Dog", "done": False }
]

app = FastAPI()

@app.get("/")
def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }


@app.get("/health")
def health():
    return { "status": "ok" }


@app.get("/tasks")
def get_tasks():
    return list_of_tasks


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.get("/tasks/{id}")
def get_task(id: int):
    for task in list_of_tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")