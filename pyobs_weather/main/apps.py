from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'pyobs_weather.main'

    def ready(self):
        from django_celery_beat.models import CrontabSchedule, PeriodicTask

        """
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='*',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='mcdonald_locke',
            task='pyobs_weather.mcdonald_locke.tasks.update',
        )
        """
