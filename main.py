import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

app = FastAPI(
    title="Task API (SQLite Backed)",
    description="CRUD API backed by a SQLite database",
    version="2.0"
)

DB_NAME = "tasks.db"

def get_db_connection():
    """Returns a SQLite connection that returns rows as dictionary-like objects."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the tasks table if missing and seeds 3 initial tasks if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_tasks = [
            ("Learn FastAPI fundamentals", 1),
            ("Build CRUD API for FlyRank", 0),
            ("Deploy code and push to GitHub", 0)
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", 
            initial_tasks
        )
        conn.commit()
        
    conn.close()

init_db()
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class Task(BaseModel):
    id: int
    title: str
    done: bool

@app.get("/", summary="Root Endpoint")
def read_root():
    """Returns basic API metadata."""
    return {
        "name": "Task API",
        "version": "2.0 (SQLite)",
        "endpoints": ["/tasks", "/health"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    """Returns server operational status."""
    return {"status": "ok"}

@app.get("/tasks", response_model=List[Task], summary="List All Tasks")
def get_all_tasks():
    """Fetches all tasks directly from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]

@app.get("/tasks/{task_id}", response_model=Task, summary="Get Single Task")
def get_single_task(task_id: int):
    """Fetches one task by ID using parameterized queries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_task(task_input: TaskCreate):
    """Inserts a new task into SQLite."""
    clean_title = task_input.title.strip()
    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or blank"
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (clean_title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return {"id": new_id, "title": clean_title, "done": False}

@app.put("/tasks/{task_id}", response_model=Task, summary="Update Task")
def update_task(task_id: int, task_input: TaskUpdate):
    """Updates task title and/or done status in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()
    
    if existing_task is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    current_title = existing_task["title"]
    current_done = existing_task["done"]
    
    if task_input.title is not None:
        clean_title = task_input.title.strip()
        if not clean_title:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty or blank"
            )
        current_title = clean_title
        
    if task_input.done is not None:
        current_done = 1 if task_input.done else 0
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?", 
        (current_title, current_done, task_id)
    )
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": current_title, "done": bool(current_done)}

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(task_id: int):
    """Deletes a task from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()
    
    if affected_rows == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return None

