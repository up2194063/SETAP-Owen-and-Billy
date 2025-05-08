from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .groups import get_group

bp = Blueprint("tasks", __name__, url_prefix='/<int:group_id>/tasks')

# show all the tasks within the group
@bp.route("/", methods=(['GET']))
@login_required
def index(group_id):

    db = get_db()
    tasks = db.execute(
        "SELECT t.task_id, t.task_name, t.task_description, t.task_deadline, t.group_id, tu.user_id, tu.task_creator, u.username"
        " FROM tasks t JOIN tasks_users tu ON t.task_id = tu.task_id"
        " JOIN users u ON u.user_id = tu.user_id"
        " WHERE t.group_id = ?",
        (group_id,)
    ).fetchall()
    return render_template("tasks/index.html", tasks=tasks, group_id=group_id)

# get a task and its creator by task_id
# checks that the id exists and optionally that the current user is the creator
# returns the task with creator information
def get_task(task_id, check_creator=True):
    task = (
        get_db()
        .execute(
            "SELECT t.task_id, t.task_name, t.task_description, t.task_deadline, t.group_id, tu.user_id, tu.task_creator, u.username"
            " FROM tasks t JOIN tasks_users tu ON t.task_id = tu.task_id"
            " JOIN users u ON u.user_id = tu.user_id"
            " WHERE t.task_id = ?",
            (task_id,),
        )
        .fetchone()
    )

    if task is None:
        abort(404, f"Task id {task_id} doesn't exist.")

    if check_creator and task["user_id"] != g.user["user_id"]:
        abort(403)

    return task

# create a new task for the current user
@bp.route("/create", methods=("GET", "POST"))
@login_required
def create(group_id):
    
    if request.method == "POST":
        task_name = request.form["task_name"]
        task_description = request.form["task_description"]
        task_deadline = request.form["task_deadline"]
        error = None

        if not task_name:
            error = "Task name is required."

        if not task_deadline:
            error = "Task deadline is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (task_name, task_description, task_deadline, group_id) VALUES (?, ?, ?, ?)",
                (task_name, task_description, task_deadline, group_id),
            )
            db.commit()
            task_id = (db.execute(
                "SELECT last_insert_rowid()"
            ).fetchone()[0])
            db.execute(
                "INSERT INTO tasks_users (user_id, task_id, task_creator) VALUES (?, ?, ?)",
                (g.user['user_id'], task_id, 'Y')
            )
            db.commit()
            return redirect(url_for("tasks.index", group_id=group_id))  # Redirect to task list (or your task index route)

    return render_template("tasks/create.html")

# update a task if the current user is the creator
@bp.route("/<int:task_id>/update", methods=("GET", "POST"))
@login_required
def update(group_id, task_id):
    
    task = get_task(task_id)

    if request.method == "POST":
        task_name = request.form["task_name"]
        task_description = request.form["task_description"]
        task_deadline = request.form["task_deadline"]
        error = None

        if not task_name:
            error = "Task Name is required."

        if not task_deadline:
            error = "Deadline is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE tasks SET task_name = ?, task_description = ?, task_deadline = ? WHERE task_id = ?", (task_name, task_description, task_deadline, task_id)
            )
            db.commit()
            return redirect(url_for("tasks.index", group_id=task['group_id']))

    return render_template("tasks/update.html", task=task, group_id=task['group_id'])

# delete a task
# ensures that the task exists and that the logged in user is the creator of the task
@bp.route("/<int:task_id>/delete", methods=("POST",))
@login_required
def delete(group_id, task_id):

    task = get_task(task_id)
    db = get_db()
    db.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    db.commit()
    return redirect(url_for("tasks.index", group_id=task['group_id']))