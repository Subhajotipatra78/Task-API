from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="Task API",
    description="In-memory CRUD API for managing to-do items.",
    version="1.0"
)

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class Task(BaseModel):
    id: int
    title: str
    done: bool = False

tasks_db: List[dict] = [
    {"id": 1, "title": "Learn FastAPI fundamentals", "done": True},
    {"id": 2, "title": "Build CRUD API for FlyRank", "done": False},
    {"id": 3, "title": "Deploy code and push to GitHub", "done": False},
]

@app.get("/", summary="Root Endpoint")
def read_root():
    """Returns basic API metadata."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    """Returns server operational status."""
    return {"status": "ok"}


@app.get("/tasks", response_model=List[Task], summary="List All Tasks")
def get_all_tasks():
    """Returns the complete list of tasks."""
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task, summary="Get Single Task")
def get_single_task(task_id: int):
    """Returns a specific task by ID. Returns 404 if not found."""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_task(task_input: TaskCreate):
    clean_title = task_input.title.strip()
    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or blank"
        )
    
    # Generating next free ID
    next_id = max([t["id"] for t in tasks_db], default=0) + 1
    
    new_task = {
        "id": next_id,
        "title": clean_title,
        "done": False
    }
    tasks_db.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task, summary="Update Task")
def update_task(task_id: int, task_input: TaskUpdate):
    """Updates task title and/or done status."""
    for task in tasks_db:
        if task["id"] == task_id:
            # Validate title if provided
            if task_input.title is not None:
                clean_title = task_input.title.strip()
                if not clean_title:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Task title cannot be empty or blank"
                    )
                task["title"] = clean_title
                
            if task_input.done is not None:
                task["done"] = task_input.done
                
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(task_id: int):
    """Deletes a task by ID. Returns status 204 with no content body."""
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(index)
            return None
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )
