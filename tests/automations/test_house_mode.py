"""Tests for House Mode Control automation."""

from datetime import datetime
from homeassistant.util import dt as dt_util


def get_default_entities():
    """Return default entities for house mode tests including input_datetime helpers."""
    return {
        "input_select.house_mode": "default",
        "input_boolean.house_mode_away": "off",
        "input_boolean.holidays": "off",
        "input_boolean.end_of_day_signal": "off",
        # Input datetime helpers with default schedule values
        "input_datetime.wake_up_weekday_start": "06:00:00",
        "input_datetime.wake_up_weekday_end": "08:00:00",
        "input_datetime.wake_up_weekend_start": "07:00:00",
        "input_datetime.wake_up_weekend_end": "09:00:00",
        "input_datetime.work_start": "08:00:00",
        "input_datetime.work_end": "17:00:00",
        "input_datetime.default_weekend_start": "09:00:00",
        "input_datetime.default_weekend_end": "18:00:00",
        "input_datetime.dinner_time": "18:00:00",
        "input_datetime.relaxation_time": "20:00:00",
        "input_datetime.bedtime_window_start": "21:00:00",
        "input_datetime.bedtime_window_end": "00:00:00",
        "input_datetime.sleep_time_start": "02:00:00",
        "input_datetime.sleep_time_end": "07:00:00",
    }


async def test_bedtime_mode_when_end_of_day_signal_at_night(automation_test):
    """Test that bedtime mode is activated when end-of-day signal triggers between 21:00-00:00."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 21, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),
    )

    # Trigger end-of-day signal
    await automation_test.state_change("input_boolean.end_of_day_signal", "on", "off")

    # Verify bedtime mode was selected
    automation_test.assert_option_selected("bedtime")


async def test_no_bedtime_mode_when_end_of_day_signal_during_day(automation_test):
    """Test that bedtime mode is NOT activated when end-of-day signal triggers during the day."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),
    )

    # Trigger end-of-day signal during the day
    await automation_test.state_change("input_boolean.end_of_day_signal", "on", "off")

    # Bedtime should NOT be triggered
    automation_test.assert_option_not_selected("bedtime")


async def test_work_mode_on_weekday_morning(automation_test):
    """Test that work mode is activated on weekday mornings when not on holidays."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    # Manually trigger the automation (simulates time_pattern trigger)
    await automation_test.trigger_automation()

    # Verify work mode was selected
    automation_test.assert_option_selected("work")


async def test_no_work_mode_on_holidays(automation_test):
    """Test that work mode is NOT activated when holidays mode is on."""
    entities = get_default_entities()
    entities["input_boolean.holidays"] = "on"  # Holidays enabled

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    # Work mode should NOT be triggered
    automation_test.assert_option_not_selected("work")


async def test_wakeup_mode_on_weekday_morning(automation_test):
    """Test that wake-up mode is activated on weekday mornings (06:00-08:00)."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 7, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 07:00
    )

    # Manually trigger the automation
    await automation_test.trigger_automation()

    # Verify wake-up mode was selected
    automation_test.assert_option_selected("wake up")


async def test_wakeup_mode_on_weekend_morning(automation_test):
    """Test that wake-up mode is activated on weekend mornings (07:00-09:00)."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 18, 8, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Saturday 08:00
    )

    # Manually trigger the automation
    await automation_test.trigger_automation()

    # Verify wake-up mode was selected
    automation_test.assert_option_selected("wake up")


async def test_sleep_mode_in_early_morning(automation_test):
    """Test that sleep mode is activated in early morning (02:00-07:00)."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 3, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # 03:00 AM
    )

    # Manually trigger the automation
    await automation_test.trigger_automation()

    # Verify sleep mode was selected
    automation_test.assert_option_selected("sleep")


async def test_relaxation_mode_in_evening(automation_test):
    """Test that relaxation mode is activated after 20:00."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 20, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # 20:30
    )

    # Manually trigger the automation
    await automation_test.trigger_automation()

    # Verify relaxation mode was selected
    automation_test.assert_option_selected("relaxation")


async def test_dinner_mode_in_evening(automation_test):
    """Test that dinner mode is activated after 18:00."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=get_default_entities(),
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 18, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # 18:30
    )

    # Manually trigger the automation
    await automation_test.trigger_automation()

    # Verify dinner mode was selected
    automation_test.assert_option_selected("dinner")


async def test_away_mode_prevents_automatic_mode_changes(automation_test):
    """Test that when house is in away mode, automatic mode changes don't occur."""
    entities = get_default_entities()
    entities["input_select.house_mode"] = "away"
    entities["input_boolean.house_mode_away"] = "on"

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    await automation_test.trigger_automation()

    # No mode changes should occur
    automation_test.assert_no_service_calls()


async def test_away_mode_not_overridden_during_wakeup_time_weekday(automation_test):
    """Test that away mode is NOT overridden by wake-up time on weekdays.

    This addresses the bug where wake-up time patterns (06:00-08:00) would
    override away mode. Away mode should ONLY be cleared when house_mode_away
    is explicitly turned off, never by time patterns.
    """
    entities = get_default_entities()
    entities["input_select.house_mode"] = "away"
    entities["input_boolean.house_mode_away"] = "on"

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 7, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 07:00 (wake-up time)
    )

    await automation_test.trigger_automation()

    # No mode changes should occur - away mode should remain
    automation_test.assert_no_service_calls()


async def test_away_mode_not_overridden_during_wakeup_time_weekend(automation_test):
    """Test that away mode is NOT overridden by wake-up time on weekends.

    This addresses the bug where wake-up time patterns (07:00-09:00) would
    override away mode on weekends. Away mode should ONLY be cleared when
    house_mode_away is explicitly turned off, never by time patterns.
    """
    entities = get_default_entities()
    entities["input_select.house_mode"] = "away"
    entities["input_boolean.house_mode_away"] = "on"

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 18, 7, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Saturday 07:30 (wake-up time)
    )

    await automation_test.trigger_automation()

    # No mode changes should occur - away mode should remain
    automation_test.assert_no_service_calls()


async def test_wakeup_time_overrides_sleep_mode(automation_test):
    """Test that wake-up time CAN override sleep mode (unlike away mode).

    This ensures that the fix for away mode protection doesn't break
    the intended behavior where wake-up time should transition from sleep.
    """
    entities = get_default_entities()
    entities["input_select.house_mode"] = "sleep"

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 7, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 07:00 (wake-up time)
    )

    await automation_test.trigger_automation()

    # Wake-up mode should be activated (overriding sleep)
    automation_test.assert_option_selected("wake up")


async def test_wakeup_time_overrides_bedtime_mode(automation_test):
    """Test that wake-up time CAN override bedtime mode (unlike away mode).

    This ensures that the fix for away mode protection doesn't break
    the intended behavior where wake-up time should transition from bedtime.
    """
    entities = get_default_entities()
    entities["input_select.house_mode"] = "bedtime"

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 18, 8, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Saturday 08:00 (wake-up time)
    )

    await automation_test.trigger_automation()

    # Wake-up mode should be activated (overriding bedtime)
    automation_test.assert_option_selected("wake up")


async def test_returning_home_from_away_changes_mode(automation_test):
    """Test that when returning home from away, mode is updated appropriately."""
    entities = get_default_entities()
    entities["input_select.house_mode"] = "away"
    entities["input_boolean.house_mode_away"] = "on"

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    # Turn off away mode (returning home)
    await automation_test.state_change("input_boolean.house_mode_away", "off", "on")

    # Mode should be changed (not away)
    automation_test.assert_option_not_selected("away")


async def test_full_weekday_mode_transitions(automation_test):
    """Test complete 24-hour cycle through all modes on a weekday."""
    entities = get_default_entities()
    entities["input_select.house_mode"] = "sleep"
    entities["media_player.lounge_room"] = "off"

    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities=entities,
        register_input_select_service=True,
        time=datetime(2025, 1, 19, 22, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Sunday 22:30
    )

    await automation_test.trigger_automation()

    # 22:30 - Sleep mode (protected, no change)
    assert automation_test.hass.states.get("input_select.house_mode").state == "sleep"

    # 00:30 - Sleep mode  - should still be on
    await automation_test.advance_time(datetime(2025, 1, 20, 0, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "sleep"

    # 02:30 - Sleep mode (02:00-07:00)
    await automation_test.advance_time(datetime(2025, 1, 20, 2, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "sleep"

    # 06:30 - Wake up mode (06:00-08:00 weekdays)
    await automation_test.advance_time(datetime(2025, 1, 20, 6, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "wake up"

    # 08:30 - Work mode (08:00-17:00 weekdays, not on holidays)
    await automation_test.advance_time(datetime(2025, 1, 20, 8, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "work"

    # 12:00 - Leave house (should change to away mode)
    await automation_test.advance_time(datetime(2025, 1, 20, 12, 00, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.state_change("input_boolean.house_mode_away", "on", "off")
    assert automation_test.hass.states.get("input_select.house_mode").state == "away"

    # 13:00 - Should still be away
    await automation_test.advance_time(datetime(2025, 1, 20, 13, 00, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "away"

    # 13:30 - Return home (should exit away mode)
    await automation_test.advance_time(datetime(2025, 1, 20, 13, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.state_change("input_boolean.house_mode_away", "off", "on")
    assert automation_test.hass.states.get("input_select.house_mode").state == "work"

    # 17:30 - Default mode (after work, before dinner)
    await automation_test.advance_time(datetime(2025, 1, 20, 17, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "default"

    # 18:30 - Dinner mode (18:00-20:00)
    await automation_test.advance_time(datetime(2025, 1, 20, 18, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "dinner"

    # 20:30 - Relaxation mode (20:00+)
    await automation_test.advance_time(datetime(2025, 1, 20, 20, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.trigger_automation()
    assert automation_test.hass.states.get("input_select.house_mode").state == "relaxation"

    # 22:00 - End-of-day signal triggers -> Bedtime mode (21:00-00:00)
    await automation_test.advance_time(datetime(2025, 1, 20, 22, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE))
    await automation_test.state_change("input_boolean.end_of_day_signal", "on", "off")
    assert automation_test.hass.states.get("input_select.house_mode").state == "bedtime"
