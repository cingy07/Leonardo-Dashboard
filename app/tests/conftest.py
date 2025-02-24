"""
PyTest configuration file containing shared fixtures and settings.
"""

import pytest
import asyncio
from typing import Generator
import json
from pathlib import Path

# Configure test settings
def pytest_configure(config):
    """Configure PyTest settings."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_committee_data() -> dict:
    """Provide sample committee data for testing."""
    return {
        "Committee 1": ["Test Representative"],
        "Committee 2": ["Other Representative"]
    }

@pytest.fixture
def mock_committee_file(tmp_path, sample_committee_data):
    """Create a temporary committee data file."""
    file_path = tmp_path / "committees.json"
    with open(file_path, "w") as f:
        json.dump(sample_committee_data, f)
    return file_path