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
CMD gunicorn --bind 0.0.0.0:8002 --workers=6 --threads=3 --worker-class=gthread pyobs_weather.wsgi
