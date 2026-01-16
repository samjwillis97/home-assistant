# Home Assistant Configuration

Personal Home Assistant configuration with automated testing and validation.

## Features

- **Organized automations** by room and function
- **Scene-based home modes** (wake up, work, dinner, relaxation, bedtime, sleep, away)
- **Automated testing** for automation logic using pytest
- **Nix flake** for reproducible development environment
- **Pre-commit hooks** for YAML linting, formatting, and validation
- **CI/CD integration** with GitHub Actions

## Development

### Using Nix (Recommended)

```bash
# Enter development environment
nix develop

# Run automation tests
run-ha-tests

# Validate Home Assistant configuration
validate-ha-config
```

See [NIX_GUIDE.md](NIX_GUIDE.md) for detailed Nix documentation.

### Without Nix

```bash
# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install testing dependencies
pip install -r requirements-test.txt

# Run tests
pytest tests/ -v --cov

# Validate configuration
./scripts/validate-config.sh
```

## Testing

This repository includes comprehensive unit tests for Home Assistant automations using `pytest-homeassistant-custom-component`.

```bash
# Run all tests
run-ha-tests  # or pytest tests/

# Run specific test file
run-ha-tests tests/automations/test_house_mode.py

# Run tests matching pattern
run-ha-tests -k test_work_mode
```

See [TESTING.md](TESTING.md) for testing framework overview and [tests/README.md](tests/README.md) for detailed testing guide.

## Project Structure

```
.
├── automations/          # Automations organized by room/function
│   ├── house/           # House-wide automations (modes, etc.)
│   ├── living_room/     # Living room automations
│   └── bedroom/         # Bedroom automations
├── scenes/              # Scenes for different modes
│   ├── dining_room/
│   └── study/
├── tests/               # Automation logic tests
│   ├── automations/     # Test files
│   ├── helpers/         # Test utilities
│   └── conftest.py      # Pytest configuration
├── scripts/             # Utility scripts
├── flake.nix           # Nix development environment
└── .github/workflows/  # CI/CD workflows
```

## Documentation

- [TESTING.md](TESTING.md) - Testing framework overview
- [NIX_GUIDE.md](NIX_GUIDE.md) - Nix flake integration guide
- [tests/README.md](tests/README.md) - Detailed testing documentation
- [tests/QUICK_REFERENCE.md](tests/QUICK_REFERENCE.md) - Testing quick reference
- [tests/SETUP.md](tests/SETUP.md) - Testing environment setup

## CI/CD

GitHub Actions automatically:
- Lints YAML files with yamllint
- Checks formatting with Prettier
- Validates Home Assistant configuration
- Runs automation logic tests with pytest
- Reports test coverage

## Entities

