"""Tests for Living Room Camera Away Mode Control automation."""

import pytest
from tests.helpers.automation_helpers import assert_service_called


@pytest.mark.asyncio
async def test_camera_turns_on_when_away_mode_activated(automation_test):
    """Test camera turns on when away mode is activated."""
    await automation_test.setup(
        automation=("living_room", "camera_away_mode.yaml"),
        entities={
            "input_boolean.house_mode_away": "off",
            "input_boolean.living_room_camera_state": "off",
        },
        mock_service=("input_boolean", "turn_on"),
    )

    # Trigger: Turn on away mode
    await automation_test.state_change(
        entity_id="input_boolean.house_mode_away",
        new_state="on",
        old_state="off",
    )

    # Assert: Camera should be turned on
    assert_service_called(
        automation_test.service_calls,
        expected_domain="input_boolean",
        expected_service="turn_on",
        expected_data={"entity_id": "input_boolean.living_room_camera_state"},
    )


@pytest.mark.asyncio
async def test_camera_turns_off_when_away_mode_deactivated(automation_test):
    """Test camera turns off when returning from away mode."""
    await automation_test.setup(
        automation=("living_room", "camera_away_mode.yaml"),
        entities={
            "input_boolean.house_mode_away": "on",
            "input_boolean.living_room_camera_state": "on",
        },
        mock_service=("input_boolean", "turn_off"),
    )

    # Trigger: Turn off away mode (returning home)
    await automation_test.state_change(
        entity_id="input_boolean.house_mode_away",
        new_state="off",
        old_state="on",
    )

    # Assert: Camera should be turned off
    assert_service_called(
        automation_test.service_calls,
        expected_domain="input_boolean",
        expected_service="turn_off",
        expected_data={"entity_id": "input_boolean.living_room_camera_state"},
    )


@pytest.mark.asyncio
async def test_no_camera_control_when_away_mode_unchanged(automation_test):
    """Test camera is not controlled when away mode doesn't change."""
    await automation_test.setup(
        automation=("living_room", "camera_away_mode.yaml"),
        entities={
            "input_boolean.house_mode_away": "on",
            "input_boolean.living_room_camera_state": "on",
        },
        mock_service=("input_boolean", "turn_on"),
    )

    # Trigger: Some other entity changes, not away mode
    await automation_test.state_change(
        entity_id="light.living_room_lights",
        new_state="on",
        old_state="off",
    )

    # Assert: No camera control should occur
    automation_test.assert_no_service_calls()
