"""Tests for House Mode Control automation."""

from datetime import datetime
from homeassistant.util import dt as dt_util


async def test_bedtime_mode_when_apple_tv_off_at_night(automation_test):
    """Test that bedtime mode is activated when Apple TV turns off between 21:00-00:00."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
            "media_player.lounge_room": "playing",
        },
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 21, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),
    )

    # Turn off Apple TV
    await automation_test.state_change("media_player.lounge_room", "off", "playing")

    # Verify bedtime mode was selected
    automation_test.assert_option_selected("bedtime")


async def test_no_bedtime_mode_when_apple_tv_off_during_day(automation_test):
    """Test that bedtime mode is NOT activated when Apple TV turns off during the day."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
            "media_player.lounge_room": "playing",
        },
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),
    )

    # Turn off Apple TV
    await automation_test.state_change("media_player.lounge_room", "off", "playing")

    # Bedtime should NOT be triggered
    automation_test.assert_option_not_selected("bedtime")


async def test_work_mode_on_weekday_morning(automation_test):
    """Test that work mode is activated on weekday mornings when not on holidays."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        },
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    # Manually trigger the automation (simulates time_pattern trigger)
    await automation_test.trigger_automation()

    # Verify work mode was selected
    automation_test.assert_option_selected("work")


async def test_no_work_mode_on_holidays(automation_test):
    """Test that work mode is NOT activated when holidays mode is on."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "on",  # Holidays enabled
        },
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    # Work mode should NOT be triggered
    automation_test.assert_option_not_selected("work")


async def test_wakeup_mode_on_weekday_morning(automation_test):
    """Test that wake-up mode is activated on weekday mornings (06:00-08:00)."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        },
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
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        },
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
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        },
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
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        },
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
        entities={
            "input_select.house_mode": "default",
            "input_boolean.house_mode_away": "off",
            "input_boolean.holidays": "off",
        },
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 15, 18, 30, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # 18:30
    )

    # Manually trigger the automation
    await automation_test.trigger_automation()

    # Verify dinner mode was selected
    automation_test.assert_option_selected("dinner")


async def test_away_mode_prevents_automatic_mode_changes(automation_test):
    """Test that when house is in away mode, automatic mode changes don't occur."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities={
            "input_select.house_mode": "away",
            "input_boolean.house_mode_away": "on",
            "input_boolean.holidays": "off",
        },
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    # No mode changes should occur
    automation_test.assert_no_service_calls()


async def test_returning_home_from_away_changes_mode(automation_test):
    """Test that when returning home from away, mode is updated appropriately."""
    await automation_test.setup(
        automation=("house", "mode.yaml"),
        entities={
            "input_select.house_mode": "away",
            "input_boolean.house_mode_away": "on",
            "input_boolean.holidays": "off",
        },
        mock_service=("input_select", "select_option"),
        time=datetime(2025, 1, 20, 9, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # Monday 09:00
    )

    # Turn off away mode (returning home)
    await automation_test.state_change("input_boolean.house_mode_away", "off", "on")

    # Mode should be changed (not away)
    automation_test.assert_option_not_selected("away")
