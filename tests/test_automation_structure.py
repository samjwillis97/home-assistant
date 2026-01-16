"""Tests for automation YAML structure and validity."""

import yaml
from pathlib import Path
import pytest


def get_all_automation_files():
    """Get all automation YAML files."""
    automations_dir = Path(__file__).parent.parent / "automations"
    return list(automations_dir.rglob("*.yaml"))


def get_all_scene_files():
    """Get all scene YAML files."""
    scenes_dir = Path(__file__).parent.parent / "scenes"
    return list(scenes_dir.rglob("*.yaml"))


@pytest.mark.parametrize("automation_file", get_all_automation_files())
def test_automation_yaml_valid(automation_file):
    """Test that automation YAML files are valid."""
    with open(automation_file) as f:
        data = yaml.safe_load(f)

    assert data is not None, f"{automation_file} is empty or invalid"


@pytest.mark.parametrize("automation_file", get_all_automation_files())
def test_automation_has_required_fields(automation_file):
    """Test that automations have required fields."""
    with open(automation_file) as f:
        data = yaml.safe_load(f)

    # Skip if file is empty or not a dict
    if not isinstance(data, dict):
        pytest.skip(f"{automation_file} does not contain a standard automation")
        return

    # Check for required fields
    assert "id" in data or "alias" in data, \
        f"{automation_file} must have either 'id' or 'alias'"


@pytest.mark.parametrize("automation_file", get_all_automation_files())
def test_automation_has_trigger_and_action(automation_file):
    """Test that automations have trigger and action."""
    with open(automation_file) as f:
        data = yaml.safe_load(f)

    # Skip if file is empty or not a dict
    if not isinstance(data, dict):
        pytest.skip(f"{automation_file} does not contain a standard automation")
        return

    # Blueprint-based automations use "use_blueprint" instead of trigger/action
    if "use_blueprint" in data:
        pytest.skip(f"{automation_file} uses a blueprint")
        return

    # Check for trigger(s) and action - both singular and plural forms are valid
    has_trigger = "trigger" in data or "triggers" in data
    assert has_trigger, \
        f"{automation_file} must have either 'trigger' or 'triggers' field"

    assert "action" in data, f"{automation_file} must have an 'action' field"


@pytest.mark.parametrize("scene_file", get_all_scene_files())
def test_scene_yaml_valid(scene_file):
    """Test that scene YAML files are valid."""
    with open(scene_file) as f:
        data = yaml.safe_load(f)

    assert data is not None, f"{scene_file} is empty or invalid"


def test_automation_directory_structure():
    """Test that automation directory exists and contains files."""
    automations_dir = Path(__file__).parent.parent / "automations"
    assert automations_dir.exists(), "automations/ directory must exist"

    automation_files = list(automations_dir.rglob("*.yaml"))
    assert len(automation_files) > 0, "automations/ directory must contain YAML files"


def test_scenes_directory_structure():
    """Test that scenes directory exists."""
    scenes_dir = Path(__file__).parent.parent / "scenes"
    assert scenes_dir.exists(), "scenes/ directory must exist"
