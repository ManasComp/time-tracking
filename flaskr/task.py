"""Task blueprint."""

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

import flaskr.helpers.convertors
import flaskr.helpers.database
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("task", __name__)
dat = flaskr.helpers.database.Database()
conv = flaskr.helpers.convertors.Convertor()


def get_user_id() -> int:
    """Get user id from the current user."""
    if g.user is None:
        # we want to have a default user
        return 1
    return g.user["id"]


def get_task(id: int):
    """Get a task and its author by id."""
    post = dat.get_task(get_db(), id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    return post


@bp.route("/start")
def start():
    """Start timer for user."""
    user_id = get_user_id()
    database = get_db()
    text = "timer resumed"
    count_of_active_tasks_for_user: int = dat.get_count_of_active_tasks_for_user(
        database, user_id
    )
    if count_of_active_tasks_for_user == 0:
        dat.create_new_task(database, user_id)
        text = "timer started"
    elif count_of_active_tasks_for_user != 1:
        abort(500)
    elif dat.get_last_active_event_category_for_user(database, user_id) == "start":
        return "already started"

    dat.create_new_event(database, user_id, "start")
    duration = conv.return_duration(database, user_id, dat)

    database.commit()
    return text + " at: " + str(duration)


@bp.route("/pause")
def pause():
    """Pause timer for user."""
    database = get_db()
    user_id = get_user_id()

    if dat.get_count_of_active_tasks_for_user(database, user_id) != 1:
        return "nothinkg to pause or error"
    if dat.get_last_active_event_category_for_user(database, user_id) == "pause":
        return "already paused"

    duration = conv.return_duration(database, user_id, dat)
    dat.update_last_active_task_duration_for_user(
        database, user_id, duration.total_seconds()
    )
    dat.create_new_event(database, user_id, "pause")
    database.commit()

    return "timer paused at: " + str(duration)


@bp.route("/log")
def log():
    """Log timer for user."""
    database = get_db()
    user_id = get_user_id()
    if dat.get_count_of_active_tasks_for_user(database, user_id) != 1:
        return "nothinkg to show or error"

    event_category = dat.get_last_active_event_category_for_user(database, user_id)
    if event_category == "pause":
        duration = conv.return_duration(database, user_id, dat, True)
    else:
        duration = conv.return_duration(database, user_id, dat, False)

    return "timer " + event_category + ", actual time: " + str(duration)


@bp.route("/")
def index():
    """Show all the tasks, most recent first."""
    new_posts = conv.returm_formated_tasks(get_db(), dat, get_user_id())
    return render_template("task/index.html", posts=new_posts)


@bp.route("/started", methods=("GET", "POST"))
@login_required
def started():
    """Start timer for user."""
    flash(start())
    return redirect(url_for("task.index"))


@bp.route("/paused", methods=("GET", "POST"))
@login_required
def paused():
    """Pause timer for user."""
    flash(pause())
    return redirect(url_for("task.index"))


@bp.route("/logged", methods=("GET", "POST"))
def logged():
    """Log timer for user."""
    flash(log())
    return redirect(url_for("task.index"))


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a task if the current user is the author."""
    if request.method == "POST":
        category = request.form["category"]
        comment = request.form["comment"]
        error = None

        if not category:
            category = "no category"

        if error is not None:
            flash(error)
        else:
            database = get_db()
            dat.edit_task(database, id, category, comment)
            database.commit()
            return redirect(url_for("task.index"))
    post = get_task(id)
    return render_template("task/edit.html", post=post, message="Edit task")


@bp.route("/ended", methods=("GET", "POST"))
def ended():
    """End timer for user."""
    database = get_db()
    user_id = get_user_id()
    if dat.get_count_of_active_tasks_for_user(database, user_id) != 1:
        flash("nothinkg to end or error")
        return redirect(url_for("task.index"))

    if request.method == "POST":
        category = request.form["category"]
        comment = request.form["comment"]
        error = None

        if not category:
            category = "no category"

        if error is not None:
            flash(error)
        else:
            database = get_db()
            duration = conv.return_duration(database, user_id, dat)
            dat.update_last_active_task_duration_for_user(
                database, user_id, duration.total_seconds()
            )
            dat.create_new_event(database, user_id, "end")
            dat.end_last_active_task_for_user(database, user_id, category, comment)
            database.commit()
            flash("timer ended: " + str(duration))
            return redirect(url_for("task.index"))

    post = get_task(dat.get_last_active_task_id_for_user(database, user_id))
    if post["category"] == "UNDEFINED":
        new_posts = []
        new_posts.append(dict(post))
        new_posts[0]["category"] = ""
        new_posts[0]["comment"] = post["comment"]
        post = new_posts[0]
    return render_template("task/edit.html", post=post, message="End")


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a task."""
    database = get_db()
    dat.delete_task(database, id)
    database.commit()
    return redirect(url_for("task.index"))


@bp.route("/<int:id>/show", methods=("POST", "GET"))
@login_required
def show(id):
    """Show all events for task."""
    database = get_db()
    return render_template(
        ("task/event-index.html"),
        posts=dat.get_events_for_task(database, id),
        time=conv.return_duration_random_task(database, id, dat),
    )


@bp.route("/users")
@login_required
def get_users():
    """Show all users"""
    if dat.is_admin(get_db(), get_user_id()):
        return render_template(("task/users.html"), posts=dat.get_users(get_db()))
    flash("You are not admin!")
    return redirect(url_for("task.index"))


@bp.route("/users/<int:id>/show", methods=("POST", "GET"))
@login_required
def show_user(id):
    """Show user."""
    database = get_db()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_type = request.form["user_type"]
        print("\n\n\n\n\n\n")
        print(password)
        print("\n\n\n\n\n\n")
        if password == "" or password is not None:
            password = generate_password_hash(password)
            dat.edit_user_with_password(
                database, id, username, user_type, password
            )
        else:
            dat.edit_user(database, id, username, user_type)

        database.commit()
        return redirect(url_for("task.get_users"))
    return render_template(
        ("task/edit-user.html"), post=dat.get_user(database, id)
    )


@bp.route("/users/<int:id>/delete", methods=("POST",))
@login_required
def delete_user(id):
    """Delete a user."""
    database = get_db()
    dat.delete_task(database, id)
    database.commit()
    return redirect(url_for("task.index"))
