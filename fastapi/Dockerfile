FROM python:3.12-alpine
RUN apk add --no-cache pipx

ADD poetry.lock pyproject.toml /app/
ADD weather_app /app/weather_app/
ADD static /app/static

WORKDIR /app/
RUN pipx run poetry install
ENTRYPOINT ["pipx", "run", "poetry", "run", "fastapi", "run", "weather_app/main.py"]
