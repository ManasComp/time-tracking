from datetime import datetime, timedelta
from flaskr.helpers.database import Database

class Time:
    def __init__(self, hours, minutes, seconds):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
    def __str__(self):
        return "{:02d}:{:02d}:{:02d}".format(self.hours, self.minutes, self.seconds)
    def total_seconds(self):
        return self.hours * 3600 + self.minutes * 60 + self.seconds
    

class Convertor:
    def return_duration(self, db, user_id : int, dat : Database, pause=False):
        duration = dat.get_last_active_task_duration_for_user(db, user_id)
        if not pause:
            duration += (datetime.now() - dat.get_last_active_event_created_for_user(db, user_id)).seconds
        hours = duration // 3600 
        minutes = (duration // 60) % 60
        seconds = duration % 60
        return Time(hours, minutes, seconds)
    
    def return_duration_random_task(self, db, task_id : int, dat : Database):
        duration = dat.get_task_duration(db, task_id)
        hours = duration // 3600 
        minutes = (duration // 60) % 60
        seconds = duration % 60
        return Time(hours, minutes, seconds)
    
    def returm_formated_tasks(self, db, dat : Database, user_id : int):
        posts = dat.get_all_tasks(db, user_id)
        new_posts = []
        for post in posts:
            new_posts.append(dict(post))
            new_posts[len(new_posts)-1]['duration'] = str(timedelta(seconds=post['duration']))
            new_posts[len(new_posts)-1]['finished'] =  "yes" if post['finished'] == 1 else "no"
        return new_posts

