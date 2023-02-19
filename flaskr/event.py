from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
import flaskr.helpers.database
import flaskr.helpers.convertors

bp = Blueprint('event', __name__)
dat = flaskr.helpers.database.Database()
conv = flaskr.helpers.convertors.Convertor()

def get_user_id() -> int:
    if g.user is None:
        return 1
    return g.user['id']

def get_task(id: int):
    post = dat.get_task(get_db(), id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    return post

@bp.route('/start')
#@login_required
def start():
    user_id = get_user_id()
    db = get_db()
    text = "timer resumed"
    count_of_active_tasks_for_user: int = dat.get_count_of_active_tasks_for_user(db, user_id)
    if count_of_active_tasks_for_user == 0:
        dat.create_new_task(db, user_id)
        text = "timer started"
    elif count_of_active_tasks_for_user != 1:
        abort(500)
    elif dat.get_last_active_event_category_for_user(db,user_id) == "start":
        return "already started"

    dat.create_new_event(db, user_id, "start")
    duration = conv.return_duration(db, user_id, dat)

    db.commit()
    return text + " at: " + duration.__str__()


@bp.route('/pause')
#@login_required
def pause():
    db = get_db()
    user_id = get_user_id()

    if dat.get_count_of_active_tasks_for_user(db, user_id) != 1:
        return "nothinkg to pause or error"
    if dat.get_last_active_event_category_for_user(db, user_id) == "pause":
        return "already paused"
    
    duration = conv.return_duration(db, user_id, dat)
    dat.update_last_active_task_duration_for_user(db, user_id, duration.total_seconds())
    dat.create_new_event(db, user_id, "pause")
    db.commit()

    return "timer paused at: " + duration.__str__()

@bp.route('/log')
#@login_required
def log():
    db = get_db()
    user_id = get_user_id()
    if dat.get_count_of_active_tasks_for_user(db, user_id) != 1:
        return "nothinkg to show or error"
    
    a =  dat.get_last_active_event_category_for_user(db, user_id)
    if a == "pause":
        duration = conv.return_duration(db, user_id, dat, True)
    else:
        duration = conv.return_duration(db, user_id, dat, False)

    return "timer " + a + ", actual time: " + duration.__str__()


@bp.route('/end', methods=('GET', 'POST'))
#@login_required
def end(red = False):
    db = get_db()
    user_id = get_user_id()
    if dat.get_count_of_active_tasks_for_user(db, user_id) != 1:
        return "nothinkg to end or error"
    duration = conv.return_duration(db, user_id, dat)

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
            duration = conv.return_duration(db, user_id, dat)
            dat.update_last_active_task_duration_for_user(db, user_id, duration.total_seconds())
            dat.create_new_event(db, user_id, "end")
            dat.end_last_active_task_for_user(db, user_id, category, comment)
            db.commit()
            if red:
                return redirect(url_for('event.index'))
            return "timer ended: " + duration.__str__()
    return render_template('event/end.html')


@bp.route('/')
def index():
    new_posts=conv.returm_formated_tasks(get_db(), dat, get_user_id())
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
    if dat.get_count_of_active_tasks_for_user(db, user_id) != 1:
        flash("nothinkg to end or error")
        return redirect(url_for('event.index'))
    end()
    if request.method == 'POST':
        return redirect(url_for('event.index'))
    return render_template('event/end.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_task(id)

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
            dat.edit_task(db, get_user_id(), category, comment)
            db.commit()

            print("\n\n\n\n\ red \n\n")
            return redirect(url_for('event.index'))

    return render_template('event/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    dat.delete_task(db, id)
    db.commit()
    return redirect(url_for('event.index'))