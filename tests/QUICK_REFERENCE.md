# Testing Quick Reference

Quick reference for common testing patterns and commands.

## Setup

### Using Nix (Recommended)

```bash
# Enter development shell (includes all testing tools)
nix develop

# Tests are ready to run - venv and dependencies auto-managed
run-ha-tests
```

### Using Python/pip

```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-test.txt
```

## Running Tests

### With Nix

```bash
# Inside nix develop shell
run-ha-tests                              # All tests with coverage
run-ha-tests tests/automations/           # Specific directory
run-ha-tests -k test_work_mode            # Pattern matching
run-ha-tests tests/automations/test_house_mode.py::test_work_mode_on_weekday_morning  # Specific test

# Outside shell
nix run .#test                            # All tests with coverage
```

### With Python/pip

```bash
# All tests
pytest tests/

# Specific file
pytest tests/automations/test_house_mode.py

# Specific test
pytest tests/automations/test_house_mode.py::test_work_mode_on_weekday_morning

# With coverage
pytest tests/ --cov --cov-report=html

# Verbose with output
pytest tests/ -v -s

# Using convenience script
./scripts/run-tests.sh
```

## Test Template

```python
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_mock_service
from tests.helpers.automation_helpers import setup_automation

async def test_automation_name(hass: HomeAssistant, load_automation):
    """Test description."""
    # 1. Mock services
    calls = async_mock_service(hass, "domain", "service_name")

    # 2. Load automation
    config = load_automation("category", "filename.yaml")

    # 3. Setup automation
    await setup_automation(hass, config)

    # 4. Trigger
    hass.states.async_set("entity_id", "new_state")
    await hass.async_block_till_done()

    # 5. Assert
    assert len(calls) == 1
```

## Common Patterns

### State Change Trigger

```python
hass.states.async_set("binary_sensor.motion", "on")
await hass.async_block_till_done()
```

### Time-Based Trigger

```python
from freezegun import freeze_time
from datetime import datetime
from pytest_homeassistant_custom_component.common import async_fire_time_changed

with freeze_time("2025-01-15 02:00:00"):
    target = datetime(2025, 1, 15, 2, 0, 0)
    async_fire_time_changed(hass, target)
    await hass.async_block_till_done()
```

### Event Trigger

```python
hass.bus.async_fire("zha_event", {"device_id": "abc", "command": "on"})
await hass.async_block_till_done()
```

### Setup Entities

```python
async def test_with_entities(hass, setup_test_entities):
    await setup_test_entities({
        "input_select.mode": "default",
        "input_boolean.flag": "off"
    })
```

### Check Service Calls

```python
from tests.helpers.automation_helpers import assert_service_called

# Assert specific call
assert_service_called(
    calls,
    "light",
    "turn_on",
    {"entity_id": "light.bedroom"},
    call_count=1
)

# Manual check
assert len(calls) == 1
assert calls[0].domain == "light"
assert calls[0].service == "turn_on"
assert calls[0].data["entity_id"] == "light.bedroom"
```

### Test Conditions Pass/Fail

```python
# Test condition passes
with freeze_time("2025-01-15 22:00:00"):  # Night time
    hass.states.async_set("binary_sensor.motion", "on")
    await hass.async_block_till_done()
    assert len(calls) == 1  # Action executed

# Test condition fails
with freeze_time("2025-01-15 14:00:00"):  # Day time
    hass.states.async_set("binary_sensor.motion", "on")
    await hass.async_block_till_done()
    assert len(calls) == 0  # Action blocked
```

## Fixtures

### From conftest.py

| Fixture | Description | Usage |
|---------|-------------|-------|
| `hass` | Home Assistant instance | Auto-injected |
| `load_automation` | Load automation YAML | `load_automation("house", "mode.yaml")` |
| `load_scene` | Load scene YAML | `load_scene("bedroom", "sleep.yaml")` |
| `setup_test_entities` | Setup entity states | `await setup_test_entities({...})` |
| `mock_time` | Mock current time | `with mock_time(datetime(...)):` |

### From pytest-homeassistant-custom-component

| Function | Description | Usage |
|----------|-------------|-------|
| `async_mock_service` | Mock service calls | `calls = async_mock_service(hass, "light", "turn_on")` |
| `async_fire_time_changed` | Fire time changed event | `async_fire_time_changed(hass, datetime(...))` |

## Helper Functions

From `tests/helpers/automation_helpers.py`:

| Function | Description |
|----------|-------------|
| `setup_automation(hass, config)` | Setup automation from config dict |
| `trigger_state_change(hass, entity, new, old)` | Trigger state change |
| `assert_service_called(calls, domain, service, data, count)` | Assert service called correctly |
| `assert_service_not_called(calls)` | Assert no service calls |

## Debugging

```python
# Print calls
for call in calls:
    print(f"{call.domain}.{call.service}: {call.data}")

# Print automation state
state = hass.states.get("automation.my_automation")
print(f"State: {state}")

# Print entity states
for entity_id in hass.states.async_entity_ids():
    state = hass.states.get(entity_id)
    print(f"{entity_id}: {state.state}")
```

## Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("hour,expected_mode", [
    (7, "wake up"),
    (9, "work"),
    (18, "dinner"),
    (20, "relaxation"),
])
async def test_modes(hass, load_automation, hour, expected_mode):
    """Test different modes by time."""
    calls = async_mock_service(hass, "input_select", "select_option")
    config = load_automation("house", "mode.yaml")

    with freeze_time(f"2025-01-20 {hour:02d}:00:00"):
        await setup_automation(hass, config)
        target = datetime(2025, 1, 20, hour, 0, 0)
        async_fire_time_changed(hass, target)
        await hass.async_block_till_done()

    assert calls[-1].data["option"] == expected_mode
```

## CI/CD

Tests run automatically in GitHub Actions:

```yaml
# .github/workflows/checks.yaml
pytest:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - run: pip install -r requirements-test.txt
    - run: pytest tests/ -v --cov
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'homeassistant'` | Activate venv: `source venv/bin/activate` |
| Tests not found | Run from repo root: `cd /path/to/home-assistant && pytest tests/` |
| Automation not triggering | Add `await hass.async_block_till_done()` after trigger |
| Service not called | Mock service BEFORE setup_automation |
| Time test fails | Use both `freeze_time` AND `async_fire_time_changed` |

## File Structure

```
tests/
├── conftest.py              # Fixtures and configuration
├── helpers/
│   └── automation_helpers.py  # Helper functions
├── automations/
│   ├── test_house_mode.py     # Example: Complex logic
│   ├── test_living_room_aircon.py  # Example: Time trigger
│   └── test_bedroom_lights.py      # Example: Blueprint
└── README.md                # Full documentation
```

## Resources

- **Full Guide**: [tests/README.md](README.md)
- **Setup Guide**: [tests/SETUP.md](SETUP.md)
- **Main Docs**: [TESTING.md](../TESTING.md)
- **pytest-ha**: [GitHub](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
