FROM python:3.8-slim

RUN apt-get update; \
    apt-get install -y build-essential curl;

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --upgrade pip==20.2.2
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

WORKDIR /app

COPY ./etc/app/poetry.lock ./etc/app/pyproject.toml ./
RUN ~/.poetry/bin/poetry install --no-ansi --no-interaction

WORKDIR /app/remindme_app

COPY ./src/remindme_app ./

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]