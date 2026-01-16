"""Helper utilities for testing Home Assistant automations."""

from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import async_mock_service


async def setup_automation(
    hass: HomeAssistant, automation_config: dict[str, Any]
) -> bool:
    """
    Set up an automation from configuration dictionary.

    Args:
        hass: Home Assistant instance
        automation_config: Automation configuration (from YAML)

    Returns:
        True if setup was successful
    """
    result = await async_setup_component(
        hass, "automation", {"automation": automation_config}
    )
    await hass.async_block_till_done()
    return result


async def trigger_state_change(
    hass: HomeAssistant, entity_id: str, new_state: str, old_state: str | None = None
):
    """
    Trigger a state change for testing.

    Args:
        hass: Home Assistant instance
        entity_id: Entity ID to change
        new_state: New state value
        old_state: Optional old state (will be set first if provided)
    """
    if old_state is not None:
        hass.states.async_set(entity_id, old_state)
        await hass.async_block_till_done()

    hass.states.async_set(entity_id, new_state)
    await hass.async_block_till_done()


def assert_service_called(
    service_calls: list,
    expected_domain: str,
    expected_service: str,
    expected_data: dict[str, Any] | None = None,
    call_count: int = 1,
):
    """
    Assert that a service was called with expected parameters.

    Args:
        service_calls: List of service calls from async_mock_service
        expected_domain: Expected service domain
        expected_service: Expected service name
        expected_data: Optional expected data in the call
        call_count: Expected number of calls (default: 1)
    """
    assert len(service_calls) == call_count, (
        f"Expected {call_count} service call(s), got {len(service_calls)}"
    )

    call = service_calls[0]
    assert call.domain == expected_domain, (
        f"Expected domain '{expected_domain}', got '{call.domain}'"
    )
    assert call.service == expected_service, (
        f"Expected service '{expected_service}', got '{call.service}'"
    )

    if expected_data is not None:
        for key, value in expected_data.items():
            assert key in call.data, f"Expected key '{key}' not found in service call data"
            assert call.data[key] == value, (
                f"Expected {key}='{value}', got '{call.data[key]}'"
            )


def assert_service_not_called(service_calls: list):
    """
    Assert that no service calls were made.

    Args:
        service_calls: List of service calls from async_mock_service
    """
    assert len(service_calls) == 0, (
        f"Expected no service calls, but got {len(service_calls)}"
    )


async def advance_time_and_trigger(
    hass: HomeAssistant, target_datetime, fire_time_changed: bool = True
):
    """
    Advance time to a specific datetime and optionally fire time_changed event.

    Args:
        hass: Home Assistant instance
        target_datetime: Target datetime to advance to
        fire_time_changed: Whether to fire the time_changed event
    """
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    if fire_time_changed:
        async_fire_time_changed(hass, target_datetime)
        await hass.async_block_till_done()
