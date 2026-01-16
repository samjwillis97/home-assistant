"""Tests for House Mode Control automation."""

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
    trigger_state_change,
    assert_service_called,
    assert_service_not_called,
)


async def test_bedtime_mode_when_apple_tv_off_at_night(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that bedtime mode is activated when Apple TV turns off between 21:00-00:00."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
            "media_player.lounge_room": "playing",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Set time to 21:30 (during bedtime window)
    target_time = datetime(2025, 1, 15, 21, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        # Fire time changed event
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Turn off Apple TV
        await trigger_state_change(hass, "media_player.lounge_room", "off", "playing")

    # Verify bedtime mode was selected
    assert len(calls) == 1
    last_call = calls[-1]
    assert last_call.data.get("option") == "bedtime"


async def test_no_bedtime_mode_when_apple_tv_off_during_day(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that bedtime mode is NOT activated when Apple TV turns off during the day."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
            "media_player.lounge_room": "playing",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Set time to 14:00 (outside bedtime window)
    target_time = datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Turn off Apple TV
        await trigger_state_change(hass, "media_player.lounge_room", "off", "playing")

    # Bedtime should NOT be triggered (other modes may be)
    # If any calls were made, they should not be for bedtime
    for call in calls:
        if "option" in call.data:
            assert call.data["option"] != "bedtime", (
                "Bedtime mode should not activate during day"
            )


async def test_work_mode_on_weekday_morning(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that work mode is activated on weekday mornings when not on holidays."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Set time to Monday 09:00 (within work hours)
    # 2025-01-20 is a Monday
    target_time = datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        # Fire time changed event and manually trigger the automation
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Manually trigger the automation (simulates time_pattern trigger)
        await hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": "automation.house_mode_control"},
            blocking=True,
        )

    # Verify work mode was selected
    assert len(calls) >= 1
    # The last call should be work mode
    last_call = calls[-1]
    assert last_call.data.get("option") == "work"


async def test_no_work_mode_on_holidays(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that work mode is NOT activated when holidays mode is on."""
    # Set up entities with holidays enabled
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "on",  # Holidays enabled
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Set up automation
    await setup_automation(hass, automation_config)

    # Trigger at Monday 09:00 (would normally be work time)
    # 2025-01-20 is a Monday
    target_time = datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    async_fire_time_changed(hass, target_time)
    await hass.async_block_till_done()

    # Work mode should NOT be triggered
    for call in calls:
        if "option" in call.data:
            assert call.data["option"] != "work", (
                "Work mode should not activate during holidays"
            )


async def test_wakeup_mode_on_weekday_morning(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that wake-up mode is activated on weekday mornings (06:00-08:00)."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Trigger at Monday 07:00 (within wake-up hours)
    # 2025-01-20 is a Monday
    target_time = datetime(2025, 1, 20, 7, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        # Fire time changed event and manually trigger the automation
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Manually trigger the automation (simulates time_pattern trigger)
        await hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": "automation.house_mode_control"},
            blocking=True,
        )

    # Verify wake-up mode was selected
    assert len(calls) >= 1
    last_call = calls[-1]
    assert last_call.data.get("option") == "wake up"


async def test_wakeup_mode_on_weekend_morning(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that wake-up mode is activated on weekend mornings (07:00-09:00)."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Trigger at Saturday 08:00 (within weekend wake-up hours)
    # 2025-01-18 is a Saturday
    target_time = datetime(2025, 1, 18, 8, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        # Fire time changed event and manually trigger the automation
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Manually trigger the automation (simulates time_pattern trigger)
        await hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": "automation.house_mode_control"},
            blocking=True,
        )

    # Verify wake-up mode was selected
    assert len(calls) >= 1
    last_call = calls[-1]
    assert last_call.data.get("option") == "wake up"


async def test_sleep_mode_in_early_morning(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that sleep mode is activated in early morning (02:00-07:00)."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Trigger at 03:00 AM
    target_time = datetime(2025, 1, 15, 3, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        # Fire time changed event and manually trigger the automation
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Manually trigger the automation (simulates time_pattern trigger)
        await hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": "automation.house_mode_control"},
            blocking=True,
        )

    # Verify sleep mode was selected
    assert len(calls) >= 1
    last_call = calls[-1]
    assert last_call.data.get("option") == "sleep"


async def test_relaxation_mode_in_evening(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that relaxation mode is activated after 20:00."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Trigger at 20:30
    target_time = datetime(2025, 1, 15, 20, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        # Fire time changed event and manually trigger the automation
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Manually trigger the automation (simulates time_pattern trigger)
        await hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": "automation.house_mode_control"},
            blocking=True,
        )

    # Verify relaxation mode was selected
    assert len(calls) >= 1
    last_call = calls[-1]
    assert last_call.data.get("option") == "relaxation"


async def test_dinner_mode_in_evening(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that dinner mode is activated after 18:00."""
    # Set up entities
    await setup_test_entities(
        {
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Trigger at 18:30
    target_time = datetime(2025, 1, 15, 18, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)

    # Mock the current time
    with patch("homeassistant.util.dt.now", return_value=target_time):
        # Set up automation
        await setup_automation(hass, automation_config)

        # Fire time changed event and manually trigger the automation
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

        # Manually trigger the automation (simulates time_pattern trigger)
        await hass.services.async_call(
            "automation",
            "trigger",
            {"entity_id": "automation.house_mode_control"},
            blocking=True,
        )

    # Verify dinner mode was selected
    assert len(calls) >= 1
    last_call = calls[-1]
    assert last_call.data.get("option") == "dinner"


async def test_away_mode_prevents_automatic_mode_changes(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that when house is in away mode, automatic mode changes don't occur."""
    # Set up entities with house in away mode
    await setup_test_entities(
        {
            "input_select.house_mode": "away",
            "input_boolean.house_mode_away": "on",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Set up automation
    await setup_automation(hass, automation_config)

    # Trigger at work time on a weekday (Monday 09:00)
    # 2025-01-20 is a Monday
    target_time = datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    async_fire_time_changed(hass, target_time)
    await hass.async_block_till_done()

    # No mode changes should occur (sequence is empty for away mode condition)
    assert_service_not_called(calls)


async def test_returning_home_from_away_changes_mode(
    hass: HomeAssistant, load_automation, setup_test_entities
):
    """Test that when returning home from away, mode is updated appropriately."""
    # Set up entities with house in away mode
    await setup_test_entities(
        {
            "input_select.house_mode": "away",
            "input_boolean.house_mode_away": "on",
            "input_boolean.holidays": "off",
        }
    )

    # Mock the input_select.select_option service
    calls = async_mock_service(hass, "input_select", "select_option")

    # Load the automation
    automation_config = load_automation("house", "mode.yaml")

    # Set up automation
    await setup_automation(hass, automation_config)

    # Set time to work time on a weekday (Monday 09:00)
    # 2025-01-20 is a Monday
    target_time = datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    async_fire_time_changed(hass, target_time)
    await hass.async_block_till_done()

    # Turn off away mode (returning home)
    await trigger_state_change(hass, "input_boolean.house_mode_away", "off", "on")

    # Mode should be changed (likely to work mode given the time)
    assert len(calls) >= 1
    # The mode should no longer be "away"
    last_call = calls[-1]
    assert last_call.data.get("option") != "away"
