from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'pyobs_weather.main'

    def ready(self):
        print("test")
        from django_celery_beat.models import CrontabSchedule, PeriodicTask

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='*',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Update weather',
            task='mcd_locke.tasks.update_weather',
        )
