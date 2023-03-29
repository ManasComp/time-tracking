from datetime import datetime, timedelta

from flaskr.db import backup_db, initilized, init_db

class Database:
    def get_count_of_active_tasks_for_user(self, db, userid: int) -> int:
        if initilized:
            backup_db()
        else:
            init_db()
        return db.execute("SELECT COUNT(*) FROM task WHERE author_id = ? AND finished = 0", (userid,)).fetchone()[0]

    def create_new_task(self, db, userid: int):
        db.execute('INSERT INTO task (author_id)' 'VALUES (?)', (userid,))

    def create_new_event(self, db, userid: int, event_category: str):
        db.execute('INSERT INTO event (task_id, event_category)' 'VALUES (?, ?)',
                (self.get_last_active_task_id_for_user(db, userid), event_category))

    def get_last_active_task_id_for_user(self, db, userid: int) -> int:
        return db.execute("SELECT id FROM task WHERE author_id = ? AND finished = 0", (userid,)).fetchone()[0]

    def get_last_active_task_duration_for_user(self, db, userid: int) -> int:
        return db.execute("SELECT duration FROM task WHERE author_id = ? AND finished = 0", (userid,)).fetchone()[0]

    def get_task_duration(self, db, task_id: int) -> int:
        return db.execute("SELECT duration FROM task WHERE id = ?", (task_id,)).fetchone()[0]

    def get_last_active_event_category_for_user(self, db, userid: int) -> str:
        return db.execute("SELECT event_category FROM event WHERE task_id = ? ORDER BY id DESC LIMIT 1", (self.get_last_active_task_id_for_user(db, userid),)).fetchone()[0]

    def get_last_active_event_created_for_user(self, db, userid: int) -> datetime:
        return db.execute("SELECT created FROM event WHERE task_id = ? ORDER BY id DESC LIMIT 1", (self.get_last_active_task_id_for_user(db, userid),)).fetchone()[0]

    def update_last_active_task_duration_for_user(self, db, userid: int, duration: int):
        db.execute("UPDATE task SET duration = ? WHERE id = ?", (duration, self.get_last_active_task_id_for_user(db, userid)))

    def end_last_active_task_for_user(self, db, userid: int, category: str, comment: str):
        db.execute("UPDATE task SET category = ?, comment = ?, finished = 1 WHERE id = ?", (category, comment, self.get_last_active_task_id_for_user(db, userid)))

    def edit_task(self, db, userid: int, category: str, comment: str) -> None:
        db.execute("UPDATE task SET category = ?, comment = ? WHERE id = ?", (category, comment, userid))

    def get_task(self, db, id: int):
        return db.execute("SELECT category, comment, id FROM task WHERE id = ?",(id,)).fetchone()

    def get_all_tasks(self, db, userid: int):
        return db.execute("SELECT id, duration, category, comment, finished, author_id FROM task WHERE author_id = ? ORDER by id DESC", (userid,)).fetchall()

    def delete_task(self, db, id: int):
        db.execute("DELETE FROM task WHERE id = ?", (id,))

    def get_events_for_task(self, db, task_id: int):
        return db.execute("SELECT id, created, event_category FROM event WHERE task_id = ? ORDER BY created DESC", (task_id,))
    
    def get_admin_role_id(self, db):
        return db.execute("SELECT id FROM user_role WHERE role = 'Admin'").fetchone()[0]

    def is_admin(self, db, user_id) -> bool:
        return db.execute("SELECT role_id FROM user WHERE id = ?", (user_id,)).fetchone()[0] == self.get_admin_role_id(db)
    
    def get_users(self, db) -> bool:
        return db.execute("SELECT user.id, username, role FROM user inner join user_role ur on ur.id = user.role_id").fetchall()
    
    def get_user(self, db, id) -> bool:
        return db.execute("SELECT user.id as id, username, role FROM user inner join user_role ur on ur.id = user.role_id WHERE user.id = ?", (id,)).fetchone()
    
    def edit_user(self, db, id, username, role) -> None:
        db.execute("UPDATE user SET username = ?, role_id = ? WHERE id = ?", (username, role, id))

    def edit_user_with_password(self, db, id, username, role, password) -> None:
        db.execute("UPDATE user SET username = ?, role_id = ?, password = ? WHERE id = ?", (username, role, password, id))
    
    def delete_user(self, db, id) -> None:
        db.execute("DELETE FROM user WHERE id = ?", (id,))

    def get_user_by_task_id(self, db, task_id) -> int:
        return db.execute("SELECT author_id FROM task WHERE id = ?", (task_id,)).fetchone()[0]