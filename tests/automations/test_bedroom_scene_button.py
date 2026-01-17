"""Tests for Bedroom Scene Button automation."""

from datetime import datetime
from homeassistant.util import dt as dt_util


async def test_button_on_activates_scene_based_on_house_mode(automation_test):
    """Test that pressing button on activates scene based on current house mode."""
    await automation_test.setup(
        automation=("bedroom", "scene_button.yaml"),
        entities={
            "input_select.house_mode": "relaxation",
        },
        mock_service=("scene", "turn_on"),
    )

    # Simulate the ZHA event for button on
    await automation_test.fire_event(
        "zha_event",
        {
            "device_id": "91cf3416653ada66678a711fa944bab6",
            "command": "on",
        },
    )

    # Verify the relaxation scene was activated
    assert len(automation_test.service_calls) == 1
    call = automation_test.service_calls[0]
    entity_id = call.data.get("entity_id")
    # entity_id could be a string or list depending on how it's passed
    if isinstance(entity_id, list):
        assert entity_id[0] == "scene.bedroom_relaxation"
    else:
        assert entity_id == "scene.bedroom_relaxation"


async def test_button_off_changes_mode_to_sleep(automation_test):
    """Test that pressing button off changes house mode to sleep.

    The scene activation is handled by apply_mode_scenes.yaml automation.
    """
    await automation_test.setup(
        automation=("bedroom", "scene_button.yaml"),
        entities={
            "input_select.house_mode": "bedtime",
        },
        mock_service=("input_select", "select_option"),
    )

    # Simulate the ZHA event for button off
    await automation_test.fire_event(
        "zha_event",
        {
            "device_id": "91cf3416653ada66678a711fa944bab6",
            "command": "off",
        },
    )

    # Verify house mode was changed to sleep
    automation_test.assert_option_selected("sleep")
