from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_celery_project.settings')

app = Celery('django_celery_project')
app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

# Celery Beat Settings
app.conf.beat_schedule = {
    'delete-expired-tokens': {
        'task': 'authentication.tasks.delete_expired_tokens',
        # 'schedule': crontab(hour=0, minute=46, day_of_month=19, month_of_year = 6),
        'schedule': 12 * 60 * 60
        #'args': (2,)
        # "options": {"queue": "starkex_queue"},
    }
}

# Celery Schedules - https://docs.celeryproject.org/en/stable/reference/celery.schedules.html

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')