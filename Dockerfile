FROM python:3.14.6-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only-main --no-interaction --no-root

COPY src ./src

CMD ["python", "src/processing.py"]