"""Main entrypoint to the web application."""

from weather_app.routers.api import v1 as api_v1

from fastapi import FastAPI

app = FastAPI()
app.include_router(api_v1.router)
