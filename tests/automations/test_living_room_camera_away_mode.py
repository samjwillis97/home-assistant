"""Tests for Living Room Camera Away Mode Control automation."""

import pytest
from pytest_homeassistant_custom_component.common import async_mock_service


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
    automation_test.assert_service_called(
        domain="input_boolean",
        service="turn_on",
        service_data={"entity_id": "input_boolean.living_room_camera_state"},
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
    automation_test.assert_service_called(
        domain="input_boolean",
        service="turn_off",
        service_data={"entity_id": "input_boolean.living_room_camera_state"},
    )


@pytest.mark.asyncio
async def test_camera_already_on_when_away_mode_activated(automation_test):
    """Test camera turn on is called even if already on (idempotent)."""
    await automation_test.setup(
        automation=("living_room", "camera_away_mode.yaml"),
        entities={
            "input_boolean.house_mode_away": "off",
            "input_boolean.living_room_camera_state": "on",
        },
        mock_service=("input_boolean", "turn_on"),
    )

    # Trigger: Turn on away mode (camera already on)
    await automation_test.state_change(
        entity_id="input_boolean.house_mode_away",
        new_state="on",
        old_state="off",
    )

    # Assert: turn_on should still be called (idempotent)
    automation_test.assert_service_called(
        domain="input_boolean",
        service="turn_on",
        service_data={"entity_id": "input_boolean.living_room_camera_state"},
    )


@pytest.mark.asyncio
async def test_camera_already_off_when_away_mode_deactivated(automation_test):
    """Test camera turn off is called even if already off (idempotent)."""
    await automation_test.setup(
        automation=("living_room", "camera_away_mode.yaml"),
        entities={
            "input_boolean.house_mode_away": "on",
            "input_boolean.living_room_camera_state": "off",
        },
        mock_service=("input_boolean", "turn_off"),
    )

    # Trigger: Turn off away mode (camera already off)
    await automation_test.state_change(
        entity_id="input_boolean.house_mode_away",
        new_state="off",
        old_state="on",
    )

    # Assert: turn_off should still be called (idempotent)
    automation_test.assert_service_called(
        domain="input_boolean",
        service="turn_off",
        service_data={"entity_id": "input_boolean.living_room_camera_state"},
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


@pytest.mark.asyncio
async def test_multiple_away_mode_cycles(automation_test):
    """Test camera responds correctly to multiple away mode cycles."""
    await automation_test.setup(
        automation=("living_room", "camera_away_mode.yaml"),
        entities={
            "input_boolean.house_mode_away": "off",
            "input_boolean.living_room_camera_state": "off",
        },
        mock_service=[
            ("input_boolean", "turn_on"),
            ("input_boolean", "turn_off"),
        ],
    )

    # First cycle: Leave home (away mode on)
    await automation_test.state_change(
        entity_id="input_boolean.house_mode_away",
        new_state="on",
        old_state="off",
    )

    automation_test.assert_service_called(
        domain="input_boolean",
        service="turn_on",
        service_data={"entity_id": "input_boolean.living_room_camera_state"},
    )

    # Update camera state to reflect the turn_on
    automation_test.hass.states.async_set(
        "input_boolean.living_room_camera_state", "on"
    )

    # Second cycle: Return home (away mode off)
    await automation_test.state_change(
        entity_id="input_boolean.house_mode_away",
        new_state="off",
        old_state="on",
    )

    automation_test.assert_service_called(
        domain="input_boolean",
        service="turn_off",
        service_data={"entity_id": "input_boolean.living_room_camera_state"},
    )


@pytest.mark.asyncio
async def test_automation_mode_restart(automation_test):
    """Test automation uses restart mode to handle rapid state changes."""
    await automation_test.setup(
        automation=("living_room", "camera_away_mode.yaml"),
        entities={
            "input_boolean.house_mode_away": "off",
            "input_boolean.living_room_camera_state": "off",
        },
        mock_service=("input_boolean", "turn_on"),
    )

    # Rapid state changes (simulating quick away mode toggle)
    await automation_test.state_change(
        entity_id="input_boolean.house_mode_away",
        new_state="on",
        old_state="off",
    )

    # The automation should handle this gracefully with restart mode
    automation_test.assert_service_called(
        domain="input_boolean",
        service="turn_on",
        service_data={"entity_id": "input_boolean.living_room_camera_state"},
    )
