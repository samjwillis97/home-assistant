"""Tests for Living Room Aircon automation."""

from datetime import datetime
from freezegun import freeze_time
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    async_mock_service,
    async_fire_time_changed,
)
from homeassistant.util import dt as dt_util
from tests.helpers.automation_helpers import (
    setup_automation,
    assert_service_called,
    assert_service_not_called,
)


async def test_aircon_turns_off_at_2am(hass: HomeAssistant, load_automation):
    """Test that aircon automation turns off HVAC at 2AM."""
    # Mock the climate.set_hvac_mode service
    calls = async_mock_service(hass, "climate", "set_hvac_mode")

    # Load the actual automation from YAML
    automation_config = load_automation("living_room", "aircon.yaml")

    # Set up the automation
    with freeze_time("2025-01-15 01:59:00"):
        await setup_automation(hass, automation_config)

    # Verify no calls yet
    assert_service_not_called(calls)

    # Advance time to 2:00 AM
    with freeze_time("2025-01-15 02:00:00"):
        target_time = datetime(2025, 1, 15, 2, 0, 0)
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

    # Verify the service was called
    assert len(calls) == 1
    call = calls[0]
    assert call.domain == "climate"
    assert call.service == "set_hvac_mode"
    # Note: The automation uses device_id which will trigger the service
    # The exact entity_id may vary, but the hvac_mode should be 'off'
    assert "hvac_mode" in call.data
    assert call.data["hvac_mode"] == "off"


async def test_aircon_does_not_turn_off_before_2am(hass: HomeAssistant, load_automation):
    """Test that aircon automation does not trigger before 2AM."""
    # Mock the climate.set_hvac_mode service
    calls = async_mock_service(hass, "climate", "set_hvac_mode")

    # Load the actual automation from YAML
    automation_config = load_automation("living_room", "aircon.yaml")

    # Set up the automation at 1:00 AM
    with freeze_time("2025-01-15 01:00:00"):
        await setup_automation(hass, automation_config)
        await hass.async_block_till_done()

    # Verify no calls were made
    assert_service_not_called(calls)


async def test_aircon_does_not_turn_off_after_2am(hass: HomeAssistant, load_automation):
    """Test that aircon automation does not trigger after 2AM has passed."""
    # Mock the climate.set_hvac_mode service
    calls = async_mock_service(hass, "climate", "set_hvac_mode")

    # Load the actual automation from YAML
    automation_config = load_automation("living_room", "aircon.yaml")

    # Set up the automation at 3:00 AM (after the trigger time)
    with freeze_time("2025-01-15 03:00:00"):
        await setup_automation(hass, automation_config)
        await hass.async_block_till_done()

    # Verify no calls were made (trigger time has passed)
    assert_service_not_called(calls)
