FROM python:3.12-slim-bookworm

ENV \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  OPENBLAS_NUM_THREADS=1

# install package
RUN apt-get update \
  && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/*

# poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
WORKDIR /weather
COPY poetry.lock pyproject.toml /weather/

# Project initialization:
RUN poetry install --no-root --no-interaction --no-ansi

# copy all
COPY . /weather

CMD gunicorn --bind 0.0.0.0:8002 --workers=6 --threads=3 --worker-class=gthread pyobs_weather.wsgi
