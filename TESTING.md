# Testing Home Assistant Automations

This repository includes a comprehensive testing framework for Home Assistant automations using `pytest-homeassistant-custom-component`.

## Why Test Automations?

While Home Assistant's `check_config` validates YAML syntax, it **cannot verify that your automation logic actually works**. Testing lets you:

- Verify automations trigger under the right conditions
- Ensure conditions properly gate execution
- Catch logic errors before deploying to production
- Document expected behavior
- Safely refactor automations
- Test edge cases and time-based logic

## Quick Start

### Option 1: Using Nix Flake (Recommended)

If you're using Nix, the testing framework is fully integrated:

```bash
# Enter the development shell
nix develop

# Run tests (automatically sets up venv and installs dependencies)
run-ha-tests

# Or run directly without entering the shell
nix run .#test

# Run specific tests
run-ha-tests tests/automations/test_house_mode.py
run-ha-tests -k test_work_mode
```

### Option 2: Using Python Virtual Environment

```bash
# 1. Install Dependencies
pip install -r requirements-test.txt

# 2. Run Tests
pytest tests/

# Run with coverage report
pytest tests/ --cov --cov-report=term-missing
```

### 3. Write Your First Test

Create a test file in `tests/automations/`:

```python
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_mock_service
from tests.helpers.automation_helpers import setup_automation

async def test_my_automation(hass: HomeAssistant, load_automation):
    """Test that lights turn on when motion detected."""
    # Mock the service that will be called
    calls = async_mock_service(hass, "light", "turn_on")

    # Load your actual automation from YAML
    automation_config = load_automation("living_room", "my_automation.yaml")

    # Set up the automation
    await setup_automation(hass, automation_config)

    # Trigger it by changing state
    hass.states.async_set("binary_sensor.motion", "on")
    await hass.async_block_till_done()

    # Assert the service was called
    assert len(calls) == 1
    assert calls[0].data["entity_id"] == "light.living_room"
```

## What Can Be Tested

✅ **State-based triggers**: Motion sensors, door sensors, switches
✅ **Time-based triggers**: Scheduled automations, time patterns
✅ **Conditions**: Time ranges, state checks, templates
✅ **Actions**: Service calls with specific data
✅ **Complex logic**: Choose blocks, conditions, sequences

❌ **External integrations**: Real Zigbee/Z-Wave devices (must be mocked)
❌ **UI-configured automations**: Stored in `.storage/` (need different approach)

## Project Structure

```
home-assistant/
├── automations/              # Your automation YAML files
│   ├── house/
│   ├── living_room/
│   └── bedroom/
├── tests/                    # Test framework
│   ├── conftest.py          # Pytest configuration & fixtures
│   ├── helpers/             # Test utilities
│   ├── automations/         # Automation tests
│   │   ├── test_house_mode.py
│   │   └── test_living_room_aircon.py
│   └── README.md            # Detailed testing guide
├── requirements-test.txt    # Testing dependencies
└── pyproject.toml          # Pytest configuration
```

## Example Tests

### Time-Based Automation

```python
from freezegun import freeze_time
from datetime import datetime

async def test_aircon_turns_off_at_2am(hass, load_automation):
    """Test aircon turns off at 2 AM."""
    calls = async_mock_service(hass, "climate", "set_hvac_mode")

    automation_config = load_automation("living_room", "aircon.yaml")

    with freeze_time("2025-01-15 01:59:00"):
        await setup_automation(hass, automation_config)

    # Advance time to 2:00 AM
    with freeze_time("2025-01-15 02:00:00"):
        async_fire_time_changed(hass, datetime(2025, 1, 15, 2, 0, 0))
        await hass.async_block_till_done()

    assert len(calls) == 1
    assert calls[0].data["hvac_mode"] == "off"
```

### Conditional Logic

```python
async def test_only_runs_at_night(hass, load_automation, setup_test_entities):
    """Test automation only runs during night hours."""
    await setup_test_entities({"binary_sensor.motion": "off"})
    calls = async_mock_service(hass, "light", "turn_on")

    automation_config = load_automation("bedroom", "night_light.yaml")

    # Test during day - should NOT trigger
    with freeze_time("2025-01-15 14:00:00"):
        await setup_automation(hass, automation_config)
        hass.states.async_set("binary_sensor.motion", "on")
        await hass.async_block_till_done()

    assert len(calls) == 0  # Blocked by time condition

    # Reset and test at night - SHOULD trigger
    hass.states.async_set("binary_sensor.motion", "off")
    with freeze_time("2025-01-15 23:00:00"):
        hass.states.async_set("binary_sensor.motion", "on")
        await hass.async_block_till_done()

    assert len(calls) == 1  # Allowed by time condition
```

## CI/CD Integration

Tests run automatically on every push and pull request via GitHub Actions:

```yaml
# .github/workflows/checks.yaml
pytest:
  name: Automation Logic Tests
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - run: pip install -r requirements-test.txt
    - run: pytest tests/ -v --cov
```

This ensures all automation logic is validated before merging changes.

## Available Fixtures & Helpers

### Fixtures (from `conftest.py`)

- `load_automation(category, filename)` - Load automation from YAML
- `load_scene(room, filename)` - Load scene from YAML
- `setup_test_entities(entity_dict)` - Set up entities with initial states
- `mock_time(datetime)` - Mock current time
- `common_entities` - Common entity IDs with defaults

### Helper Functions (from `tests/helpers/automation_helpers.py`)

- `setup_automation(hass, config)` - Set up automation from config
- `trigger_state_change(hass, entity_id, new_state, old_state)` - Trigger state change
- `assert_service_called(calls, domain, service, data, count)` - Assert service call
- `assert_service_not_called(calls)` - Assert no calls made

## Best Practices

1. **Test actual YAML files** - Use `load_automation()` to test real configs
2. **Test both paths** - Verify conditions pass AND fail appropriately
3. **Use descriptive names** - `test_work_mode_on_weekday_morning` over `test_mode_1`
4. **Test edge cases** - Midnight boundaries, weekend/weekday transitions
5. **One assertion per test** - Keep tests focused and debuggable
6. **Mock external dependencies** - Use `async_mock_service()` for all service calls

## Running Tests Locally

```bash
# All tests with verbose output
pytest tests/ -v

# Specific test file
pytest tests/automations/test_house_mode.py

# Specific test function
pytest tests/automations/test_house_mode.py::test_work_mode_on_weekday_morning

# With coverage report
pytest tests/ --cov --cov-report=html
# Then open htmlcov/index.html

# With output (for debugging print statements)
pytest tests/ -v -s
```

## Resources

- **Detailed Guide**: See [tests/README.md](tests/README.md) for comprehensive documentation
- **Example Tests**: Check `tests/automations/` for real examples
- **pytest-homeassistant-custom-component**: [GitHub](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
- **Home Assistant Testing**: [Developers Docs](https://developers.home-assistant.io/docs/development_testing)

## Getting Help

If tests fail:
1. Run with `-v -s` for verbose output and print statements
2. Check that mocks are set up before automation setup
3. Verify entity states are correct before triggers
4. Ensure `await hass.async_block_till_done()` after state changes
5. For time-based tests, verify `freeze_time` and `async_fire_time_changed` usage

## Next Steps

1. Run existing tests: `pytest tests/ -v`
2. Review example tests in `tests/automations/`
3. Write tests for your own automations
4. Add tests to CI/CD pipeline
5. Achieve comprehensive automation coverage

Happy testing! 🧪
