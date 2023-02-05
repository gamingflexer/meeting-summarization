from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
import os

from pytz import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dp.settings')

app = Celery('sih')
app.conf.enable_utc = True

app.conf.update(timezone = 'Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

#Celery Beat Config

app.autodiscover_tasks(lambda : settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

