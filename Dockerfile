FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1
RUN apt-get update \
  && apt-get install -y build-essential libmariadbclient-dev \
  && rm -rf /var/lib/apt/lists/*
RUN mkdir /pyobs-weather
WORKDIR /pyobs-weather
COPY requirements.txt /pyobs-weather/
RUN pip install -r requirements.txt
COPY . /pyobs-weather/
RUN ./manage.py collectstatic --noinput
CMD gunicorn pyobs_weather.wsgi
