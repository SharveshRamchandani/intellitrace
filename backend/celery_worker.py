"""
celery_worker.py – Celery worker entry point.
Run with: celery -A celery_worker.celery_app worker --loglevel=info
"""
from app.tasks import celery_app  # re-export so Celery CLI can find it

__all__ = ["celery_app"]
