import sqlite3

# ============================================================
# Database initialization
# ============================================================

def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(""" CREATE TABLE IF NOT EXISTS tasks 
        (
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
# Database connection
# ============================================================

def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    return conn

# ============================================================
# Get task by ID
# ============================================================

def get_task_by_id(task_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))

    task = cursor.fetchone()
    conn.close()

    if task:
        return {"id": task[0], "title": task[1], "done": bool(task[2])}
    return None

# ============================================================
# Get all tasks
# ============================================================

def get_tasks():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()

    tasks = []
    for row in rows:
        tasks.append({"id": row[0], "title": row[1], "done": bool(row[2])})

    conn.close()
    return tasks 

# ============================================================
# Create a new task
# ============================================================

def create_task(title):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?) RETURNING id, title, done", (title, 0))

    row = cursor.fetchone()

    conn.commit()
    conn.close()

    return {"id": row[0], "title": row[1], "done": bool(row[2])}

# ============================================================
# Update a task
# ============================================================

def update_task(task_id, new_title=None, new_done=None):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    updated_title = new_title if new_title is not None else row[1]
    updated_done = new_done if new_done is not None else bool(row[2])

    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ? RETURNING id, title, done", (updated_title, int(updated_done), task_id))

    row = cursor.fetchone()

    conn.commit()
    conn.close()

    return {"id": row[0], "title": row[1], "done": bool(row[2])}

# ============================================================
# Delete a task
# ============================================================

def delete_task(task_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    deleted_count = cursor.rowcount
    conn.close()

    return deleted_count