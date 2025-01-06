from fasthtml.common import *
from datetime import datetime
import sqlite3



# Initialize the app
app, rt = fast_app()

# Database setup
todo_db = "todo.db"


def execute_query(query, params=(), fetch=False):
    """Execute a query on the SQLite database."""
    with sqlite3.connect(todo_db) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()



# Create the todos table
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



def render_todo_list():
    """Fetch and render all tasks."""
    items = execute_query(
        """
        SELECT id, title, body, creation_time, due_date, is_completed, tags
        FROM todos
        ORDER BY id DESC
        """,
        fetch=True,
    )
    if not items:
        return [Li("No tasks remaining.")]
    rendered_items = [
        Li(
            f"Task ID: {item[0]} | Title: {item[1]} | Body: {item[2] or 'N/A'} | Created: {item[3]} | "
            f"Due: {item[4] or 'N/A'} | Completed: {'✔️' if item[5] else '❌'} | Tags: {item[6] or 'None'}",
            Div(
                A(
                    "Done",
                    href="#",
                    hx_post=f"/done/{item[0]}",
                    hx_target="#todo-list",
                    hx_swap="innerHTML"
                ),
                A(
                    "Delete",
                    href="#",
                    hx_post=f"/delete/{item[0]}",
                    hx_target="#todo-list",
                    hx_swap="innerHTML"
                ),
            ),
            id=f"task-{item[0]}",
        )
        for item in items
    ]
    return rendered_items





@rt("/")
def get():
    """Render the to-do list and input form."""
    return Titled(
        "To-Do Lists",
        Form(
            Input(name="title", placeholder="Title", required=True),
            Textarea(name="body", placeholder="Body (optional)"),
            Input(name="due_date", placeholder="Due Date (YYYY-MM-DD)", type="date"),
            Input(name="tags", placeholder="Tags (comma-separated)"),
            Button("Add", type="submit"),
            hx_post="/add", hx_target="#todo-list", hx_swap="innerHTML",
        ),
        Ul(id="todo-list", children=render_todo_list()),
    )





@rt("/add", methods=["POST"])
def add(title: str, body: str = "", due_date: str = None, tags: str = ""):
    """Add a new task to the database and update the list."""
    execute_query(
        """
        INSERT INTO todos (title, body, creation_time, due_date, tags)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, body, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), due_date, tags),
    )
    return Ul(*render_todo_list(), id="todo-list")




@rt("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id: int):
    """Delete the task from the database and refresh the list."""
    execute_query("DELETE FROM todos WHERE id = ?", (task_id,))
    updated_list = render_todo_list()
    return Ul(*updated_list, id="todo-list")






@rt("/done/<int:task_id>", methods=["POST"])
def toggle_completed(task_id: int):
    """Toggle the is_completed status in the database and refresh the list."""
    current_status = execute_query(
        "SELECT is_completed FROM todos WHERE id = ?",
        (task_id,),
        fetch=True,
    )
    new_status = 0 if current_status else 1
    execute_query(
        "UPDATE todos SET is_completed = ? WHERE id = ?",
        (new_status, task_id),
    )
    updated_list = render_todo_list()
    return Ul(*updated_list, id="todo-list")


# def delete_all_entries():
#     with sqlite3.connect(todo_db) as conn:
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM todos")
#         conn.commit()
#         print("All entries have been deleted.")

# # Call the function to delete all entries
# delete_all_entries()


serve()
