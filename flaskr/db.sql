-- ENABLE THE USE OF FOREIGN KEYS
PRAGMA foreign_keys = ON;

-- DROP TABLES IF PRE-EXISTING
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS payments_users;
DROP TABLE IF EXISTS tasks_users;
DROP TABLE IF EXISTS users_groups;



-- CREATE TABLE FOR USERS
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- CREATE TABLE FOR GROUPS
CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL,
    group_description TEXT
);

-- CREATE TABLE FOR PAYMENTS
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    payment_name TEXT NOT NULL,
    payment_description TEXT,
    payment_deadline TEXT NOT NULL,
    payment_amount REAL NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups (group_id)
);

-- CREATE TABLE FOR TASKS
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    task_description TEXT,
    task_deadline TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups (group_id)
);

-- CREATE INTERSECTION TABLE FOR PAYMENTS AND USERS
CREATE TABLE payments_users (
    payment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payments (payment_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- CREATE INTERSECTION TABLE FOR TASKS AND USERS
CREATE TABLE tasks_users (
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (task_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- CREATE INTERSECTION TABLE FOR USERS AND GROUPS
CREATE TABLE users_groups (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (group_id) REFERENCES groups (group_id)
);



-- CREATE TASK USING THE NEW DB AND THE STRUCTURE OF THE POST CREATION --
@bp.route("/create_task", methods=("GET", "POST"))
@login_required
def create_task():
    """Create a new task for the current user."""
    if request.method == "POST":
        task_name = request.form["task_name"]
        task_description = request.form["task_description"]
        task_deadline = request.form["task_deadline"]
        group_id = request.form["group_id"]  # Assuming the group ID is passed from the form
        error = None

        if not task_name:
            error = "Task name is required."

        if not task_deadline:
            error = "Task deadline is required."

        if not group_id:
            error = "Group ID is required."  # Ensure that a valid group is selected

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (task_name, task_description, task_deadline, group_id) VALUES (?, ?, ?, ?)",
                (task_name, task_description, task_deadline, group_id),
            )
            db.commit()
            return redirect(url_for("tasks.index"))  # Redirect to task list (or your task index route)

    return render_template("tasks/create_task.html")

-- CREATE PAYMENT USING THE NEW DB AND THE STRUCTURE OF THE POST CREATION --

@bp.route("/create_payment", methods=("GET", "POST"))
@login_required
def create_payment():
    """Create a new payment for a group."""
    if request.method == "POST":
        payment_name = request.form["payment_name"]
        payment_description = request.form["payment_description"]
        payment_deadline = request.form["payment_deadline"]
        payment_amount = request.form["payment_amount"]
        group_id = request.form["group_id"]  # Assuming the group ID is passed from the form
        error = None

        if not payment_name:
            error = "Payment name is required."

        if not payment_deadline:
            error = "Payment deadline is required."

        if not payment_amount:
            error = "Payment amount is required."

        if not group_id:
            error = "Group ID is required."  # Ensure that a valid group is selected

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO payments (payment_name, payment_description, payment_deadline, payment_amount, group_id) VALUES (?, ?, ?, ?, ?)",
                (payment_name, payment_description, payment_deadline, payment_amount, group_id),
            )
            db.commit()
            return redirect(url_for("payments.index"))  -- Redirect to payment list (or your payment index route)

    return render_template("payments/create_payment.html")


-- CREATE TASK USING THE NEW DB AND THE STRUCTURE OF THE POST CREATION --
--
--
--
--
--
--
--
@bp.route("/create_task", methods=("GET", "POST"))
@login_required
def create_task():
    """Create a new task for a group."""
    if request.method == "POST":
        task_name = request.form["task_name"]
        task_description = request.form["task_description"]
        task_deadline = request.form["task_deadline"]
        group_id = request.form["group_id"]  # Assuming the group ID is passed from the form
        error = None

        if not payment_name:
            error = "Task name is required."

        if not payment_deadline:
            error = "Task deadline is required."

        if not group_id:
            error = "Group ID is required."  # Ensure that a valid group is selected

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (task_name, task_description, task_deadline, group_id) VALUES (?, ?, ?, ?)",
                (task_name, task_description, task_deadline, group_id),
            )
            db.commit()
            return redirect(url_for("tasks.index"))  -- Redirect to payment list (or your payment index route)

    return render_template("tasks/create_task.html")

-- DELETE TASK USING THE NEW DB AND THE STRUCTURE OF THE POST CREATION --
--
--
--
--
--
--
--
@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a task.

    Ensures that the task exists and that the logged in user is the
    author of the task.
    """
    get_task(task_id)
    db = get_db()
    db.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    db.commit()
    return redirect(url_for("blog.index"))

-- DELETE PAYMENT USING THE NEW DB AND THE STRUCTURE OF THE POST CREATION --
--
--
--
--
--
--
--
@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(payment_id):
    """Delete a payment.

    Ensures that the payment exists and that the logged in user is the
    author of the payment.
    """
    get_payment(payment_id)
    db = get_db()
    db.execute("DELETE FROM payments WHERE payment_id = ?", (payment_id,))
    db.commit()
    return redirect(url_for("blog.index"))

-- UPDATE TASK USING THE NEW DB AND THE STRUCTURE OF THE POST CREATION --
--
--
--
--
--
--
--
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(task_id):
    """Update a task if the current user is the author."""
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
                "UPDATE task SET task_name = ?, task_description, task_deadline = ? WHERE task_id = ?", (task_name, task_description, task_deadline, task_id)
            )
            db.commit()
            return redirect(url_for("tasks.index"))

    return render_template("tasks/update.html", tasks=tasks)

-- UPDATE PAYMENT USING THE NEW DB AND THE STRUCTURE OF THE POST CREATION --
--
--
--
--
--
--
--
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(payment_id):
    """Update a payment if the current user is the author."""
    payment = get_payment(payment_id)

    if request.method == "POST":
        payment_name = request.form["payment_name"]
        payment_description = request.form["payment_description"]
        payment_deadline = request.form["payment_deadline"]
        payment_amount = request.form["payment_amount"]
        error = None

        if not payment_name:
            error = "Payment Name is required."

        if not payment_deadline:
            error = "Deadline is required"

        if not payment_amount:
            error = "Payment Amount is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE payment SET payment_name = ?, payment_description, payment_deadline = ?, payment_amount = ? WHERE payment_id = ?", (payment_name, payment_description, payment_deadline, payment_amount, payment_id)
            )
            db.commit()
            return redirect(url_for("payments.index"))

    return render_template("payments/update.html", payments=payments)