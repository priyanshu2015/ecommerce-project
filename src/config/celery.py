from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
# app.conf.enable_utc = False

# app.conf.update(timezone="Asia/Kolkata")

app.config_from_object(settings, namespace='CELERY')


app.conf.beat_schedule = {
    "delete-expired-tokens": {
        "task": "authentication.tasks.delete_expired_tokens",
        # "schedule": 2
        "schedule": crontab(hour=7, minute=56),
        # "options": {"queue": "tokens"}
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')