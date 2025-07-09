import os
from celery import Celery

# Use Redis as broker and result backend
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "agency",
    broker=broker_url,
    backend=backend_url,
)

# Optional: direct routing
celery_app.conf.task_routes = {"service.api.process_task": {"queue": "agency"}}
# Schedule MetaAgent runs every minute via Celery Beat
from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    'run-meta-check-every-minute': {
        'task': 'service.meta_tasks.run_meta_check',
        'schedule': 60.0,
    }
}
