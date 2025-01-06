from fasthtml.common import *
from datetime import datetime
import sqlite3

# Initialize the app
app, rt = fast_app()

# Database setup
todo_db = "todo.db"

def execute_query(query, params=(), fetch=False):
    with sqlite3.connect(todo_db) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()

# Create the todos table with the required fields
execute_query(
    """
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        body TEXT,
        creation_time TEXT NOT NULL,
        due_date TEXT,
        is_completed BOOLEAN NOT NULL DEFAULT 0,
        tags TEXT
    )
    """
)

@rt("/")
def get():
    # Render the to-do list and input form
    return Titled(
        "To-Do Lists",
        Form(
            Input(name="title", placeholder="Title"),
            Input(name="body", placeholder="Body (OPTIONAL)"),
            Input(name="due_date", placeholder="Due Date)", type="date"),
            Input(name="tags", placeholder="Tags separated by comma"),
            Button("Add", type="submit"),
            hx_post="/add", hx_target="#todo-list", hx_swap="beforeend",
        ),
        Ul(id="todo-list", children=render_todo_list()),
    )

@rt("/add", methods=["POST"])
def add(title: str, body: str = "", due_date: str = None, tags: str = ""):
    # Add a new task to the database
    execute_query(
        """
        INSERT INTO todos (title, body, creation_time, due_date, tags)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, body, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), due_date, tags),
    )
    return Ul(*render_todo_list(), id="todo-list")

def render_todo_list():
    # Fetch and render tasks
    items = execute_query(
        """
        SELECT title, body, creation_time, due_date, is_completed, tags
        FROM todos
        ORDER BY id DESC
        """,
        fetch=True,
    )
    if not items:
        return [Li("No to-do items yet!")]
    return [
        Li(
            f"Title: {title} | Body: {body or 'N/A'} | Created: {creation_time} | "
            f"Due: {due_date or 'N/A'} | Completed: {'Yes' if is_completed else 'No'} | "
            f"Tags: {tags or 'None'}"
        )
        for title, body, creation_time, due_date, is_completed, tags in items
    ]

serve()
