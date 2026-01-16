"""Pytest configuration and fixtures for Home Assistant automation testing."""

import pytest
from pathlib import Path
from typing import Any
import yaml
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy.assertion import SnapshotAssertion

# Enable pytest-homeassistant-custom-component plugin
pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion with Home Assistant extension."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture
def automation_files_path() -> Path:
    """Return path to automation files directory."""
    return Path(__file__).parent.parent / "automations"


@pytest.fixture
def scenes_path() -> Path:
    """Return path to scenes directory."""
    return Path(__file__).parent.parent / "scenes"


@pytest.fixture
def load_automation():
    """Fixture to load automation from YAML file."""

    def _load_automation(category: str, filename: str) -> dict[str, Any]:
        """
        Load an automation from YAML file.

        Args:
            category: The subdirectory (e.g., 'house', 'living_room', 'bedroom')
            filename: The YAML filename (with or without .yaml extension)

        Returns:
            Parsed automation dictionary
        """
        automation_path = (
            Path(__file__).parent.parent / "automations" / category / filename
        )
        if not automation_path.suffix:
            automation_path = automation_path.with_suffix(".yaml")

        with open(automation_path) as f:
            return yaml.safe_load(f)

    return _load_automation


@pytest.fixture
def load_scene():
    """Fixture to load scene from YAML file."""

    def _load_scene(room: str, filename: str) -> dict[str, Any]:
        """
        Load a scene from YAML file.

        Args:
            room: The room subdirectory (e.g., 'dining_room', 'study')
            filename: The YAML filename (with or without .yaml extension)

        Returns:
            Parsed scene dictionary
        """
        scene_path = Path(__file__).parent.parent / "scenes" / room / filename
        if not scene_path.suffix:
            scene_path = scene_path.with_suffix(".yaml")

        with open(scene_path) as f:
            return yaml.safe_load(f)

    return _load_scene


@pytest.fixture
async def setup_test_entities(hass: HomeAssistant):
    """Set up common test entities used across multiple automations."""

    async def _setup_entities(entities: dict[str, str]):
        """
        Set up entities with initial states.

        Args:
            entities: Dictionary mapping entity_id to initial state
        """
        for entity_id, state in entities.items():
            hass.states.async_set(entity_id, state)
        await hass.async_block_till_done()

    return _setup_entities


@pytest.fixture
def mock_time():
    """Fixture to help with time-based testing."""
    from datetime import datetime
    from unittest.mock import patch
    from homeassistant.util import dt as dt_util

    def _mock_time(target_datetime: datetime):
        """
        Create a context manager to mock the current time.

        Args:
            target_datetime: The datetime to mock as "now"

        Returns:
            Context manager that mocks dt_util.now()
        """
        return patch.object(dt_util, "now", return_value=target_datetime)

    return _mock_time


@pytest.fixture
def common_entities():
    """Return dictionary of common entity IDs and their default states."""
    return {
        "input_select.house_mode": "default",
        "input_boolean.house_mode_away": "off",
        "input_boolean.holidays": "off",
        "media_player.lounge_room": "off",
        "binary_sensor.hallway_motion": "off",
        "switch.bedroom_lights_switch": "off",
    }
