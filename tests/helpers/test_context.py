"""Simplified test context for automation testing with minimal boilerplate."""

from datetime import datetime
from typing import Any
from unittest.mock import patch
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_mock_service,
    async_fire_time_changed,
)
from tests.helpers.automation_helpers import setup_automation


class AutomationTestContext:
    """Context manager for simplified automation testing."""

    def __init__(self, hass: HomeAssistant, load_automation):
        """Initialize the test context.

        Args:
            hass: Home Assistant instance
            load_automation: Fixture to load automation from YAML
        """
        self.hass = hass
        self.load_automation = load_automation
        self.service_calls = None
        self.automation_entity_id = None
        self._time_patch = None
        self._target_time = None

    async def setup(
        self,
        automation: tuple[str, str],
        entities: dict[str, str] | None = None,
        mock_service: tuple[str, str] | None = None,
        time: datetime | None = None,
        automation_entity_id: str | None = None,
    ):
        """Set up the test with all common boilerplate.

        Args:
            automation: Tuple of (category, filename) for automation to load
            entities: Dictionary of entity_id -> initial_state to set up
            mock_service: Tuple of (domain, service) to mock, e.g. ("input_select", "select_option")
            time: Optional datetime to mock as current time
            automation_entity_id: Optional custom automation entity ID for cleanup
        """
        # Set up entities
        if entities:
            for entity_id, state in entities.items():
                self.hass.states.async_set(entity_id, state)
            await self.hass.async_block_till_done()

        # Mock service
        if mock_service:
            domain, service = mock_service
            self.service_calls = async_mock_service(self.hass, domain, service)

        # Load automation config
        category, filename = automation
        automation_config = self.load_automation(category, filename)

        # Infer automation entity ID from config if not provided
        if automation_entity_id:
            self.automation_entity_id = automation_entity_id
        elif isinstance(automation_config, dict) and "alias" in automation_config:
            # Convert alias to entity_id format (lowercase, replace spaces/special chars with underscores)
            alias = automation_config["alias"]
            entity_name = alias.lower().replace(" ", "_").replace(":", "").replace("-", "_")
            self.automation_entity_id = f"automation.{entity_name}"
        else:
            self.automation_entity_id = None

        # Set up time mocking if requested
        if time:
            self._target_time = time
            self._time_patch = patch("homeassistant.util.dt.now", return_value=time)
            self._time_patch.__enter__()

        # Set up automation
        await setup_automation(self.hass, automation_config)

        # Fire time changed event if time was mocked
        if time:
            async_fire_time_changed(self.hass, time)
            await self.hass.async_block_till_done()

    async def trigger_automation(self, entity_id: str | None = None):
        """Manually trigger the automation.

        Args:
            entity_id: Optional automation entity ID (uses auto-detected if not provided)
        """
        target_entity = entity_id or self.automation_entity_id
        if not target_entity:
            raise ValueError("Cannot trigger automation: entity_id not provided and could not be auto-detected")

        await self.hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": target_entity},
            blocking=True,
        )

    async def state_change(self, entity_id: str, new_state: str, old_state: str | None = None):
        """Trigger a state change.

        Args:
            entity_id: Entity to change
            new_state: New state value
            old_state: Optional old state (will be set first if provided)
        """
        if old_state is not None:
            self.hass.states.async_set(entity_id, old_state)
            await self.hass.async_block_till_done()

        self.hass.states.async_set(entity_id, new_state)
        await self.hass.async_block_till_done()

    async def fire_event(self, event_type: str, event_data: dict[str, Any] | None = None):
        """Fire an event on the Home Assistant bus.

        Args:
            event_type: Type of event to fire (e.g., "zha_event")
            event_data: Optional event data dictionary
        """
        self.hass.bus.async_fire(event_type, event_data or {})
        await self.hass.async_block_till_done()

    async def cleanup(self):
        """Clean up after the test (turn off automation and stop time mocking)."""
        # Stop time mocking
        if self._time_patch:
            self._time_patch.__exit__(None, None, None)
            self._time_patch = None

        # Turn off automation to cancel any timers
        if self.automation_entity_id:
            await self.hass.services.async_call(
                "automation",
                "turn_off",
                {"entity_id": self.automation_entity_id},
                blocking=True,
            )
            await self.hass.async_block_till_done()

    def assert_option_selected(self, expected_option: str):
        """Assert that input_select.select_option was called with the expected option.

        Args:
            expected_option: Expected option value (e.g., "work", "bedtime")
        """
        if not self.service_calls:
            raise AssertionError("No service was mocked. Did you forget to pass mock_service?")

        assert len(self.service_calls) >= 1, "Expected at least one service call"
        last_call = self.service_calls[-1]
        actual_option = last_call.data.get("option")
        assert actual_option == expected_option, (
            f"Expected option '{expected_option}', got '{actual_option}'"
        )

    def assert_option_not_selected(self, forbidden_option: str):
        """Assert that input_select.select_option was NOT called with a specific option.

        Args:
            forbidden_option: Option that should not have been selected
        """
        if not self.service_calls:
            return  # No calls made, so the option wasn't selected

        for call in self.service_calls:
            if "option" in call.data:
                assert call.data["option"] != forbidden_option, (
                    f"Option '{forbidden_option}' should not have been selected"
                )

    def assert_hvac_mode_set(self, expected_mode: str):
        """Assert that climate.set_hvac_mode was called with the expected mode.

        Args:
            expected_mode: Expected HVAC mode (e.g., "off", "cool", "heat")
        """
        if not self.service_calls:
            raise AssertionError("No service was mocked. Did you forget to pass mock_service?")

        assert len(self.service_calls) >= 1, "Expected at least one service call"
        last_call = self.service_calls[-1]
        assert last_call.domain == "climate", f"Expected climate service, got {last_call.domain}"
        assert last_call.service == "set_hvac_mode", f"Expected set_hvac_mode, got {last_call.service}"
        actual_mode = last_call.data.get("hvac_mode")
        assert actual_mode == expected_mode, (
            f"Expected HVAC mode '{expected_mode}', got '{actual_mode}'"
        )

    def assert_no_service_calls(self):
        """Assert that no service calls were made."""
        if not self.service_calls:
            return  # No mock set up, so no calls could have been made

        assert len(self.service_calls) == 0, (
            f"Expected no service calls, but got {len(self.service_calls)}"
        )

    def assert_service_call_count(self, expected_count: int):
        """Assert the number of service calls made.

        Args:
            expected_count: Expected number of calls
        """
        if not self.service_calls:
            actual_count = 0
        else:
            actual_count = len(self.service_calls)

        assert actual_count == expected_count, (
            f"Expected {expected_count} service call(s), got {actual_count}"
        )
