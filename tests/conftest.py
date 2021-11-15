import os

import pytest


@pytest.fixture
def resources_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "resources")
