"""Tests for Living Room Aircon automation."""

from datetime import datetime
from unittest.mock import patch
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    async_mock_service,
    async_fire_time_changed,
)
from homeassistant.util import dt as dt_util
from tests.helpers.automation_helpers import (
    setup_automation,
    assert_service_not_called,
)


async def test_aircon_turns_off_at_2am(hass: HomeAssistant, load_automation):
    """Test that aircon automation turns off HVAC at 2AM."""
    # Mock the climate.set_hvac_mode service
    calls = async_mock_service(hass, "climate", "set_hvac_mode")

    # Load the actual automation from YAML
    automation_config = load_automation("living_room", "aircon.yaml")

    # Set time to 02:00 AM
    target_time = datetime(2025, 1, 15, 2, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up the automation
        await setup_automation(hass, automation_config)

        # Fire time changed event and manually trigger the automation
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Manually trigger the automation (simulates time trigger)
        await hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": "automation.living_room_aircon"},
            blocking=True,
        )

        # Clean up: turn off automation to cancel timers
        await hass.services.async_call(
            "automation",
            "turn_off",
            {"entity_id": "automation.living_room_aircon"},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Verify the service was called
    assert len(calls) == 1
    last_call = calls[-1]
    assert last_call.domain == "climate"
    assert last_call.service == "set_hvac_mode"
    assert last_call.data.get("hvac_mode") == "off"


async def test_aircon_does_not_turn_off_before_2am(
    hass: HomeAssistant, load_automation
):
    """Test that aircon automation does not trigger before 2AM."""
    # Mock the climate.set_hvac_mode service
    calls = async_mock_service(hass, "climate", "set_hvac_mode")

    # Load the actual automation from YAML
    automation_config = load_automation("living_room", "aircon.yaml")

    # Set time to 01:00 AM (before trigger time)
    target_time = datetime(2025, 1, 15, 1, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up the automation at 1:00 AM
        await setup_automation(hass, automation_config)
        await hass.async_block_till_done()

        # Clean up: turn off automation to cancel timers
        await hass.services.async_call(
            "automation",
            "turn_off",
            {"entity_id": "automation.living_room_aircon"},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Verify no calls were made
    assert_service_not_called(calls)


async def test_aircon_does_not_turn_off_after_2am(hass: HomeAssistant, load_automation):
    """Test that aircon automation does not trigger after 2AM has passed."""
    # Mock the climate.set_hvac_mode service
    calls = async_mock_service(hass, "climate", "set_hvac_mode")

    # Load the actual automation from YAML
    automation_config = load_automation("living_room", "aircon.yaml")

    # Set time to 03:00 AM (after trigger time)
    target_time = datetime(2025, 1, 15, 3, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up the automation at 3:00 AM (after the trigger time)
        await setup_automation(hass, automation_config)
        await hass.async_block_till_done()

        # Clean up: turn off automation to cancel timers
        await hass.services.async_call(
            "automation",
            "turn_off",
            {"entity_id": "automation.living_room_aircon"},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Verify no calls were made (trigger time has passed)
    assert_service_not_called(calls)
