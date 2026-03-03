import os
from celery import Celery

redis_url = os.getenv("REDIS_URL")

if not redis_url:
    raise RuntimeError("REDIS_URL is not set")

celery = Celery(
    "shortener_worker",
    broker=redis_url,
    backend=redis_url,
)

celery.conf.update(
    task_track_started=True,
    timezone="UTC",
)

celery.autodiscover_tasks(["app.tasks"])

celery.conf.beat_schedule = {
    "delete-every-day": {
        "task": "app.tasks.delete_rotten_links.delete_rotten_links",
        "schedule": 86400.0,
    }
}