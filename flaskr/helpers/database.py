from flaskr.db import get_db

class Database:
    db = None
    def __init__(self):
        self.db = get_db()
    
    # def ActiveTasksForUser(self, userid: int) -> int:
    #     return db.execute("SELECT COUNT(*) FROM task WHERE author_id = ? AND finished = 0", (userid,)).fetchone()