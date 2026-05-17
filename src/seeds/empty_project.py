"""Seed: creates a single empty project with no resources."""

from src.seeds.api import SemaphoreAPI
from src.config import DEFAULT_PROJECT_NAME


def run(base_url: str) -> dict:
    api = SemaphoreAPI(base_url)
    project = api.create_project(DEFAULT_PROJECT_NAME)
    return project
