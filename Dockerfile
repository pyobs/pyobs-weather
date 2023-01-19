FROM python:3.7-slim AS compile-image
RUN apt-get update \
  && apt-get install -y build-essential libmariadbclient-dev-compat \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.7-slim
RUN apt-get update \
  && apt-get install -y mariadb-client \
  && rm -rf /var/lib/apt/lists/*
COPY --from=compile-image /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
WORKDIR /weather
COPY . /weather/
CMD gunicorn --bind 0.0.0.0:8002 --workers=6 --threads=3 --worker-class=gthread pyobs_weather.wsgi
