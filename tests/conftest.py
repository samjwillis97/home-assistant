"""Pytest configuration and fixtures for Home Assistant automation testing."""

import pytest
from pathlib import Path
from typing import Any
import yaml


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
