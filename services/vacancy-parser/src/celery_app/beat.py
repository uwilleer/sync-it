from datetime import timedelta

from celery.schedules import crontab, schedule


__all__ = ["beat_schedule"]

beat_schedule = {
    "parse-vacancies-every-10-minutes": {
        "task": "parse_vacancies",
        "schedule": schedule(run_every=timedelta(minutes=10)),
    },
    "cleanup-duplicate-vacancies-daily-03-00": {
        "task": "cleanup_duplicate_vacancies",
        "schedule": crontab(hour=3, minute=0),
    },
}
