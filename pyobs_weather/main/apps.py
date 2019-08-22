from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'pyobs_weather.main'

    def ready(self):
        from django_celery_beat.models import CrontabSchedule, PeriodicTask

        # add schedule every 5 minutes
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='*',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        # add period task for averages
        try:
            task = PeriodicTask.objects.get(name='averages')
        except PeriodicTask.DoesNotExist:
            task = PeriodicTask()
        task.crontab = schedule
        task.name = 'averages'
        task.task = 'pyobs_weather.main.tasks.update_averages'
        task.save()
