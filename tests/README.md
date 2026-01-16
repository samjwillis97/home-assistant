# Home Assistant Automation Testing Framework

This directory contains unit tests for Home Assistant automations using `pytest-homeassistant-custom-component`.

## Overview

While Home Assistant lacks a dedicated YAML automation testing framework, we can achieve robust automation logic testing using the `pytest-homeassistant-custom-component` library. This approach lets us programmatically set up automations from YAML files, mock states and services, and assert that triggers fire actions correctly.

## Quick Start

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov --cov-report=term-missing

# Run specific test file
pytest tests/automations/test_house_mode.py

# Run specific test
pytest tests/automations/test_house_mode.py::test_work_mode_on_weekday_morning
```

## Project Structure

```
tests/
├── conftest.py                          # Pytest configuration and shared fixtures
├── helpers/
│   ├── __init__.py
│   └── automation_helpers.py            # Helper functions for testing
├── automations/
│   ├── test_house_mode.py              # Tests for house mode automation
│   ├── test_living_room_aircon.py      # Tests for aircon automation
│   └── test_bedroom_lights.py          # Tests for bedroom lights
└── fixtures/                            # Test data and fixtures
```

## Writing Tests

### Basic Test Structure

```python
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_mock_service
from tests.helpers.automation_helpers import setup_automation, assert_service_called

async def test_my_automation(hass: HomeAssistant, load_automation):
    """Test description."""
    # 1. Mock services that will be called
    calls = async_mock_service(hass, "light", "turn_on")

    # 2. Load automation from YAML
    automation_config = load_automation("living_room", "my_automation.yaml")

    # 3. Set up the automation
    await setup_automation(hass, automation_config)

    # 4. Trigger the automation (state change, time change, etc.)
    hass.states.async_set("binary_sensor.motion", "on")
    await hass.async_block_till_done()

    # 5. Assert expected service calls
    assert_service_called(calls, "light", "turn_on", {"entity_id": "light.living_room"})
```

### Testing Time-Based Automations

Use `freezegun` and `async_fire_time_changed` for time-based triggers:

```python
from freezegun import freeze_time
from datetime import datetime
from pytest_homeassistant_custom_component.common import async_fire_time_changed

async def test_scheduled_automation(hass: HomeAssistant, load_automation):
    """Test automation triggered at specific time."""
    calls = async_mock_service(hass, "scene", "turn_on")

    automation_config = load_automation("house", "scheduled.yaml")

    # Set up automation before trigger time
    with freeze_time("2025-01-15 17:59:00"):
        await setup_automation(hass, automation_config)

    # Advance time to trigger
    with freeze_time("2025-01-15 18:00:00"):
        target_time = datetime(2025, 1, 15, 18, 0, 0)
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

    assert len(calls) == 1
```

### Testing Conditions

Test both passing and failing conditions:

```python
async def test_condition_passes(hass: HomeAssistant, load_automation, setup_test_entities):
    """Test automation runs when condition is met."""
    await setup_test_entities({"input_boolean.test": "on"})

    calls = async_mock_service(hass, "light", "turn_on")
    automation_config = load_automation("house", "conditional.yaml")

    await setup_automation(hass, automation_config)
    hass.states.async_set("binary_sensor.trigger", "on")
    await hass.async_block_till_done()

    assert len(calls) == 1  # Condition passed, action executed


async def test_condition_fails(hass: HomeAssistant, load_automation, setup_test_entities):
    """Test automation does NOT run when condition is not met."""
    await setup_test_entities({"input_boolean.test": "off"})

    calls = async_mock_service(hass, "light", "turn_on")
    automation_config = load_automation("house", "conditional.yaml")

    await setup_automation(hass, automation_config)
    hass.states.async_set("binary_sensor.trigger", "on")
    await hass.async_block_till_done()

    assert len(calls) == 0  # Condition failed, no action
```

## Available Fixtures

### Core Fixtures

- **`hass`**: Home Assistant instance (from pytest-homeassistant-custom-component)
- **`load_automation`**: Load automation from YAML file
  ```python
  automation_config = load_automation("house", "mode.yaml")
  ```
- **`load_scene`**: Load scene from YAML file
  ```python
  scene_config = load_scene("dining_room", "work.yaml")
  ```
- **`setup_test_entities`**: Set up entities with initial states
  ```python
  await setup_test_entities({
      "input_select.house_mode": "default",
      "input_boolean.holidays": "off"
  })
  ```
- **`mock_time`**: Mock current time for testing
  ```python
  with mock_time(datetime(2025, 1, 15, 9, 0, 0)):
      # Test code here
  ```
- **`common_entities`**: Dictionary of common entity IDs with default states

### Helper Functions

From `tests/helpers/automation_helpers.py`:

- **`setup_automation(hass, automation_config)`**: Set up automation from config
- **`trigger_state_change(hass, entity_id, new_state, old_state)`**: Trigger state change
- **`assert_service_called(calls, domain, service, data, count)`**: Assert service was called
- **`assert_service_not_called(calls)`**: Assert no service calls were made
- **`advance_time_and_trigger(hass, datetime)`**: Advance time and fire time_changed event

## Common Patterns

### Testing State Triggers

```python
# Trigger automation by changing state
hass.states.async_set("binary_sensor.motion", "on")
await hass.async_block_till_done()
```

### Testing Time Patterns

```python
from datetime import datetime
from pytest_homeassistant_custom_component.common import async_fire_time_changed

# Trigger hourly time pattern
target_time = datetime(2025, 1, 15, 9, 0, 0)
async_fire_time_changed(hass, target_time)
await hass.async_block_till_done()
```

### Testing Event Triggers

```python
# Trigger automation with event
hass.bus.async_fire("zha_event", {"device_id": "abc123", "command": "on"})
await hass.async_block_till_done()
```

### Testing Multiple Scenarios

```python
import pytest

@pytest.mark.parametrize("day,hour,expected_mode", [
    ("2025-01-20", 9, "work"),      # Monday 9am -> work mode
    ("2025-01-18", 9, "default"),   # Saturday 9am -> default mode
    ("2025-01-20", 7, "wake up"),   # Monday 7am -> wake up mode
])
async def test_mode_by_time(hass, load_automation, setup_test_entities, day, hour, expected_mode):
    """Test house mode changes based on day and time."""
    await setup_test_entities({"input_select.house_mode": "default"})
    calls = async_mock_service(hass, "input_select", "select_option")

    automation_config = load_automation("house", "mode.yaml")

    with freeze_time(f"{day} {hour:02d}:00:00"):
        await setup_automation(hass, automation_config)
        target_time = datetime.fromisoformat(f"{day}T{hour:02d}:00:00")
        async_fire_time_changed(hass, target_time)
        await hass.async_block_till_done()

    assert calls[-1].data.get("option") == expected_mode
```

## CI/CD Integration

Tests run automatically on push and pull requests via GitHub Actions. See `.github/workflows/checks.yaml`.

The workflow includes:
- YAML linting
- Prettier formatting
- Home Assistant config validation
- **Pytest automation logic tests** (this framework)

## Best Practices

1. **Test actual YAML files**: Use `load_automation()` to test your real configuration
2. **Test both success and failure paths**: Verify conditions work correctly
3. **Use meaningful test names**: Describe what is being tested
4. **Test edge cases**: Time boundaries, state transitions, etc.
5. **Keep tests focused**: One automation aspect per test
6. **Use parametrized tests**: For testing multiple scenarios with same logic
7. **Mock external dependencies**: Use `async_mock_service()` for all service calls

## Debugging Tests

### Run with verbose output

```bash
pytest tests/ -v -s
```

### Run specific test with print statements

```python
async def test_my_automation(hass, load_automation):
    """Test with debugging."""
    calls = async_mock_service(hass, "light", "turn_on")

    automation_config = load_automation("house", "test.yaml")
    print(f"Loaded config: {automation_config}")

    await setup_automation(hass, automation_config)

    hass.states.async_set("binary_sensor.motion", "on")
    await hass.async_block_till_done()

    print(f"Service calls: {len(calls)}")
    for call in calls:
        print(f"  - {call.domain}.{call.service}: {call.data}")

    assert len(calls) == 1
```

### Check automation traces

```python
# Get automation state to inspect traces
automation_state = hass.states.get("automation.my_automation")
print(f"Automation state: {automation_state}")
```

## Troubleshooting

### Import errors

If you get import errors, make sure you're in the repository root:

```bash
cd /path/to/home-assistant
pytest tests/
```

### Automation not triggering

- Verify the automation was set up: Check return value of `setup_automation()`
- Add `await hass.async_block_till_done()` after triggers
- Check entity states are set correctly before trigger
- Verify time is mocked correctly for time-based triggers

### Service not being called

- Ensure mock is set up before automation: `async_mock_service()` before `setup_automation()`
- Check conditions are met
- Verify correct domain and service names
- Add debug prints to inspect `calls` list

## Resources

- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
- [Home Assistant Test Documentation](https://developers.home-assistant.io/docs/development_testing)
- [Pytest Documentation](https://docs.pytest.org/)
- [Home Assistant Automation Documentation](https://www.home-assistant.io/docs/automation/)

## Examples

See existing test files for examples:
- `test_house_mode.py`: Complex time-based conditions and state triggers
- `test_living_room_aircon.py`: Simple time-based trigger
- `test_bedroom_lights.py`: Blueprint-based automation (template for event testing)
