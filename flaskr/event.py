import time
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import sqlite3
from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime, timedelta
from flaskr.helpers.database import Database


bp = Blueprint('event', __name__)

def get_count_of_active_tasks_for_user(db, userid: int) -> int:
    return db.execute("SELECT COUNT(*) FROM task WHERE author_id = ? AND finished = 0", (userid,)).fetchone()[0]

def create_new_task(db, userid: int):
    db.execute(
        'INSERT INTO task (author_id)'
        'VALUES (?)',
        (userid,)
    )

def create_new_event(db, userid: int, event_category: str):
    db.execute(
        'INSERT INTO event (task_id, event_category)'
        ' VALUES (?, ?)',
        (get_last_active_task_id_for_user(db, userid), event_category)
    )


def get_last_active_task_id_for_user(db, userid: int) -> int:
    return db.execute("SELECT id FROM task WHERE author_id = ? AND finished = 0", (userid,)).fetchone()[0]

def get_last_active_task_duration_for_user(db, userid: int) -> int:
    return db.execute("SELECT duration FROM task WHERE author_id = ? AND finished = 0", (userid,)).fetchone()[0]

def get_last_active_event_category_for_user(db, userid: int) -> str:
    return db.execute("SELECT event_category FROM event WHERE task_id = ? ORDER BY id DESC LIMIT 1", (get_last_active_task_id_for_user(db, userid),)).fetchone()[0]

def get_last_active_event_created_for_user(db, userid: int) -> datetime:
    return db.execute("SELECT created FROM event WHERE task_id = ? ORDER BY id DESC LIMIT 1", (get_last_active_task_id_for_user(db, userid),)).fetchone()[0]

def update_last_active_task_duration_for_user(db, userid: int, duration: int):
    db.execute("UPDATE task SET duration = ? WHERE id = ?", (duration, get_last_active_task_id_for_user(db, userid)))

def end_last_active_task_for_user(db, userid: int, category: str, comment: str):
    db.execute("UPDATE task SET category = ?, comment = ?, finished = 1 WHERE id = ?", (category, comment, get_last_active_task_id_for_user(db, userid)))

def edit_task(db, id: int, category: str, comment: str):
    db.execute("UPDATE task SET category = ?, comment = ? WHERE id = ?", (category, comment, id))

def to_time(db, user_id):
    duration = get_last_active_task_duration_for_user(db, user_id)
    time1 : time=  datetime.now() - get_last_active_event_created_for_user(db, user_id) 
    hours = (time1.seconds + duration) // 3600 
    minutes = ((time1.seconds + duration) // 60) % 60
    seconds = (time1.seconds + duration) % 60
    total_seconds = hours*3600 + minutes*60 + seconds
    string_format = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    return total_seconds,string_format

def get_user_id():
    if g.user is None:
        return 1
    return g.user['id']

@bp.route('/start')
#@login_required
def start():
    user_id = get_user_id()
    db = get_db()
    text = "timer resumed"
    count_of_active_tasks_for_user: int = get_count_of_active_tasks_for_user(db, user_id)
    if count_of_active_tasks_for_user == 0:
        create_new_task(db, user_id)
        text = "timer started"
    elif count_of_active_tasks_for_user != 1:
        abort(500)
    elif get_last_active_event_category_for_user(db,user_id) == "start":
        return "already started"

    create_new_event(db, user_id, "start")
    _, string_format = to_time(db, user_id)

    db.commit()
    return text + " at: " + string_format


def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

@bp.route('/pause')
#@login_required
def pause():
    db = get_db()
    user_id = get_user_id()

    if  get_count_of_active_tasks_for_user(db, user_id) != 1:
        return "nothinkg to pause or error"
    if get_last_active_event_category_for_user(db, user_id) == "pause":
        return "already paused"
    
    total_seconds, string_format = to_time(db, user_id)
    update_last_active_task_duration_for_user(db, user_id, total_seconds)
    create_new_event(db, user_id, "pause")
    db.commit()

    return "timer paused at: " + string_format


@bp.route('/log')
#@login_required
def log():
    db = get_db()
    user_id = get_user_id()
    if get_count_of_active_tasks_for_user(db, user_id) != 1:
        return "nothinkg to show or error"
    _, string_format = to_time(db, user_id)
    return "timer " + get_last_active_event_category_for_user(db, user_id) + ", actual time: " + string_format


@bp.route('/end', methods=('GET', 'POST'))
#@login_required
def end(red = False):
    db = get_db()
    user_id = get_user_id()
    if get_count_of_active_tasks_for_user(db, user_id) != 1:
        return "nothinkg to end or error"
    duration, string_format = to_time(db, user_id)

    if request.method == 'POST':
        category = request.form['category']
        comment = request.form['comment']
        error = None

        if not category:
            #error = 'Title is required.'
            category = "no category"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            total_seconds, string_format = to_time(db, user_id)
            update_last_active_task_duration_for_user(db, user_id, total_seconds)
            create_new_event(db, user_id, "end")
            end_last_active_task_for_user(db, user_id, category, comment)
            db.commit()
            if red:
                return redirect(url_for('event.index'))
            return "timer ended: " + string_format
    return render_template('event/end.html')


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute("SELECT id, duration, category, comment, finished, author_id FROM task WHERE author_id = ? ORDER by id DESC", (1,)).fetchall()
    new_posts = []
    for post in posts:
        new_posts.append(dict(post))
        new_posts[len(new_posts)-1]['duration'] = str(timedelta(seconds=post['duration']))
        new_posts[len(new_posts)-1]['finished'] =  "yes" if post['finished'] == 1 else "no"
    return render_template('event/index.html', posts=new_posts)


@bp.route('/started', methods=('GET', 'POST'))
@login_required
def started():
    flash(start())
    return redirect(url_for('event.index'))

@bp.route('/paused', methods=('GET', 'POST'))
@login_required
def paused():
    flash(pause())
    return redirect(url_for('event.index'))


@bp.route('/logged', methods=('GET', 'POST'))
def logged():
    flash(log())
    return redirect(url_for('event.index'))

@bp.route('/ended', methods=('GET', 'POST'))
@login_required
def ended():
    db = get_db()
    user_id = get_user_id()
    if get_count_of_active_tasks_for_user(db, user_id) != 1:
        flash("nothinkg to end or error")
        return redirect(url_for('event.index'))
    end()
    if request.method == 'POST':
        return redirect(url_for('event.index'))
    return render_template('event/end.html')

def get_task(id):
    post = get_db().execute("SELECT category, comment, id FROM task WHERE id = ?",(id,)).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_task(id)
    user_id = get_user_id()

    if request.method == 'POST':
        category = request.form['category']
        comment = request.form['comment']
        error = None

        if not category:
            #error = 'Title is required.'
            category = "no category"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            edit_task(db, user_id, category, comment)
            db.commit()
            return redirect(url_for('event.index'))

    return render_template('event/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))