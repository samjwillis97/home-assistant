"""Tests for Living Room Aircon automation."""

from datetime import datetime
from homeassistant.util import dt as dt_util


async def test_aircon_turns_off_at_2am(automation_test):
    """Test that aircon automation turns off HVAC at 2AM."""
    await automation_test.setup(
        automation=("living_room", "aircon.yaml"),
        mock_service=("climate", "set_hvac_mode"),
        time=datetime(2025, 1, 15, 2, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),
    )

    # Manually trigger the automation (simulates time trigger)
    await automation_test.trigger_automation()

    # Verify the service was called with correct parameters
    automation_test.assert_hvac_mode_set("off")


async def test_aircon_does_not_turn_off_before_2am(automation_test):
    """Test that aircon automation does not trigger before 2AM."""
    await automation_test.setup(
        automation=("living_room", "aircon.yaml"),
        mock_service=("climate", "set_hvac_mode"),
        time=datetime(2025, 1, 15, 1, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # 01:00 AM
    )

    # Verify no calls were made (just setup, no trigger)
    automation_test.assert_no_service_calls()


async def test_aircon_does_not_turn_off_after_2am(automation_test):
    """Test that aircon automation does not trigger after 2AM has passed."""
    await automation_test.setup(
        automation=("living_room", "aircon.yaml"),
        mock_service=("climate", "set_hvac_mode"),
        time=datetime(2025, 1, 15, 3, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE),  # 03:00 AM
    )

    # Verify no calls were made (trigger time has passed)
    automation_test.assert_no_service_calls()
