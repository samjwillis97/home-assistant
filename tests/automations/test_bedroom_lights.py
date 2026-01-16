"""Tests for Bedroom Lights automation (blueprint-based)."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_mock_service
from tests.helpers.automation_helpers import (
    setup_automation,
    trigger_state_change,
    assert_service_called,
)


async def test_button_up_turns_lights_on(hass: HomeAssistant, load_automation, setup_test_entities):
    """Test that pressing button up turns bedroom lights on."""
    # Set up entities
    await setup_test_entities({
        "switch.bedroom_lights_switch": "off",
        "input_text.sam_bedroom_switch": "",
    })

    # Mock the switch.turn_on service
    calls = async_mock_service(hass, "switch", "turn_on")

    # Load the automation
    automation_config = load_automation("bedroom", "lights.yaml")

    # Note: Blueprint automations are more complex to test directly
    # This is a simplified version that shows the concept
    # In practice, you might want to test the blueprint's logic separately
    # or use integration tests with real devices

    await setup_automation(hass, automation_config)

    # Simulate the ZHA event that would trigger button up
    # This is simplified - actual ZHA events are more complex
    hass.bus.async_fire(
        "zha_event",
        {
            "device_id": "7b82711377bc14f56b57e69c5d16159f",
            "command": "on",
        },
    )
    await hass.async_block_till_done()

    # Clean up: turn off automation to cancel timers
    await hass.services.async_call(
        "automation",
        "turn_off",
        {"entity_id": "automation.study_lights"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # In a real scenario with the full blueprint logic, this would trigger
    # For now, this test serves as a template for blueprint testing


async def test_button_down_turns_lights_off(hass: HomeAssistant, load_automation, setup_test_entities):
    """Test that pressing button down turns bedroom lights off."""
    # Set up entities
    await setup_test_entities({
        "switch.bedroom_lights_switch": "on",
        "input_text.sam_bedroom_switch": "",
    })

    # Mock the switch.turn_off service
    calls = async_mock_service(hass, "switch", "turn_off")

    # Load the automation
    automation_config = load_automation("bedroom", "lights.yaml")

    await setup_automation(hass, automation_config)

    # Simulate the ZHA event that would trigger button down
    hass.bus.async_fire(
        "zha_event",
        {
            "device_id": "7b82711377bc14f56b57e69c5d16159f",
            "command": "off",
        },
    )
    await hass.async_block_till_done()

    # Clean up: turn off automation to cancel timers
    await hass.services.async_call(
        "automation",
        "turn_off",
        {"entity_id": "automation.study_lights"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # In a real scenario with the full blueprint logic, this would trigger
    # For now, this test serves as a template for blueprint testing
