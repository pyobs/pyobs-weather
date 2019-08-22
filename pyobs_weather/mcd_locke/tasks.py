import logging
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from pyobs_weather.celery import app


@app.task
def update_weather():
    print("update weather")
    return "bla"
