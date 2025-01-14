from django.core.management.base import BaseCommand
from pyobs_weather.weather.tasks import evaluate


class Command(BaseCommand):
    help = "Evaluate weather"

    def handle(self, *args, **options):
        evaluate()
