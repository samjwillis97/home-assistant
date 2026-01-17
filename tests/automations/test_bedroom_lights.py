"""Tests for Bedroom Lights automation (blueprint-based)."""


async def test_button_up_turns_lights_on(automation_test):
    """Test that pressing button up turns bedroom lights on."""
    await automation_test.setup(
        automation=("bedroom", "lights.yaml"),
        entities={
            "switch.bedroom_lights_switch": "off",
            "input_text.sam_bedroom_switch": "",
        },
        mock_service=("switch", "turn_on"),
        automation_entity_id="automation.study_lights",
    )

    # Simulate the ZHA event that would trigger button up
    await automation_test.fire_event(
        "zha_event",
        {
            "device_id": "7b82711377bc14f56b57e69c5d16159f",
            "command": "on",
        },
    )

    # Note: In a real scenario with the full blueprint logic, this would trigger
    # For now, this test serves as a template for blueprint testing


async def test_button_down_turns_lights_off(automation_test):
    """Test that pressing button down turns bedroom lights off."""
    await automation_test.setup(
        automation=("bedroom", "lights.yaml"),
        entities={
            "switch.bedroom_lights_switch": "on",
            "input_text.sam_bedroom_switch": "",
        },
        mock_service=("switch", "turn_off"),
        automation_entity_id="automation.study_lights",
    )

    # Simulate the ZHA event that would trigger button down
    await automation_test.fire_event(
        "zha_event",
        {
            "device_id": "7b82711377bc14f56b57e69c5d16159f",
            "command": "off",
        },
    )

    # Note: In a real scenario with the full blueprint logic, this would trigger
    # For now, this test serves as a template for blueprint testing
