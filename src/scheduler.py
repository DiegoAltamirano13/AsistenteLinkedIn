from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class PostScheduler:
    def __init__(self, post_callback, interval_hours=1):
        self.scheduler = BackgroundScheduler()
        self.post_callback = post_callback
        self.interval_hours = interval_hours
        self.running = False

    def start(self):
        if not self.running:
            self.scheduler.add_job(
                self.post_callback,
                trigger=IntervalTrigger(hours=self.interval_hours),
                id='auto_post',
                replace_existing=True
            )
            self.scheduler.start()
            self.running = True

    def stop(self):
        if self.running:
            self.scheduler.shutdown()
            self.running = False

    def change_interval(self, hours):
        self.interval_hours = hours
        if self.running:
            self.scheduler.reschedule_job('auto_post', trigger=IntervalTrigger(hours=hours))