import os
from celery import Celery

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "5370")

celery = Celery(
    "shortener_worker",
    broker=f"redis://{redis_host}:{redis_port}/0",
    backend=f"redis://{redis_host}:{redis_port}/0",
)

celery.conf.update(
    task_track_started=True,
    timezone="UTC",
)

celery.autodiscover_tasks(["app.tasks"])

celery.conf.beat_schedule = {
    "delete-every-minute": {
        "task": "app.tasks.delete_rotten_links.delete_rotten_links",
        "schedule": 60.0,
    }
}