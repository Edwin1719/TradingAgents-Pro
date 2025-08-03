
import os
from celery import Celery

# Get Redis URL from environment variable, with a default for local non-Docker setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery
celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.tasks']  # Explicitly include the tasks module
)

# Optional: Configure Celery
celery_app.conf.update(
    task_track_started=True,
)
