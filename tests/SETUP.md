# Testing Setup Guide

This guide will help you set up the testing environment for Home Assistant automations.

## Prerequisites

- Python 3.12 or later
- pip (Python package manager)
- Git

## Step-by-Step Setup

### 1. Create a Virtual Environment

It's strongly recommended to use a Python virtual environment to avoid conflicts with system packages:

```bash
# From the repository root
python3 -m venv venv
```

### 2. Activate the Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### 3. Install Testing Dependencies

```bash
pip install --upgrade pip
pip install -r requirements-test.txt
```

**Note:** This may take 5-10 minutes as it installs Home Assistant and all its dependencies.

### 4. Verify Installation

```bash
pytest --version
python -c "import homeassistant; print(f'Home Assistant {homeassistant.__version__} installed')"
```

You should see pytest version and Home Assistant version printed.

### 5. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Or use the convenience script
./scripts/run-tests.sh
```

## Troubleshooting

### Issue: `AttributeError` or build errors during installation

**Solution:** Upgrade pip and setuptools:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements-test.txt
```

### Issue: `ImportError: No module named 'homeassistant'`

**Solution:** Make sure you've activated the virtual environment:
```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

Then reinstall dependencies:
```bash
pip install -r requirements-test.txt
```

### Issue: Tests fail with `ModuleNotFoundError`

**Solution:** Install the package in development mode:
```bash
pip install -e .
```

### Issue: `pytest-homeassistant-custom-component` installation fails

**Solution:** Try installing Home Assistant first, then the testing plugin:
```bash
pip install homeassistant>=2024.1.0
pip install pytest-homeassistant-custom-component
```

If that still fails, you can try installing from a specific version:
```bash
pip install pytest-homeassistant-custom-component==0.13.100
```

### Issue: Tests run but fail with fixture errors

**Solution:** Make sure you're running tests from the repository root:
```bash
cd /path/to/home-assistant
pytest tests/
```

### Issue: "No tests collected" or "cannot import name"

**Solution:** Ensure the `tests/` directory structure is correct:
```bash
tests/
├── __init__.py (should exist, can be empty)
├── conftest.py
├── helpers/
│   ├── __init__.py
│   └── automation_helpers.py
└── automations/
    ├── __init__.py
    └── test_*.py
```

Create missing `__init__.py` files if needed:
```bash
touch tests/__init__.py
```

## Docker Alternative

If you have issues with local installation, you can use Docker:

```bash
# Build testing image
docker build -f tests/Dockerfile -t ha-tests .

# Run tests
docker run --rm ha-tests pytest tests/ -v
```

**tests/Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY . .

CMD ["pytest", "tests/", "-v"]
```

## VS Code Integration

If you're using VS Code, add this to `.vscode/settings.json`:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
}
```

Then you can run tests directly from the VS Code Test Explorer.

## GitHub Codespaces / Dev Containers

For GitHub Codespaces or VS Code Dev Containers, create `.devcontainer/devcontainer.json`:

```json
{
  "name": "Home Assistant Testing",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "postCreateCommand": "pip install -r requirements-test.txt",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ]
    }
  }
}
```

## Next Steps

Once setup is complete:

1. **Review existing tests**: `ls tests/automations/`
2. **Run tests**: `pytest tests/ -v`
3. **Read testing guide**: See [tests/README.md](README.md)
4. **Write your first test**: Follow examples in `tests/automations/`

## Getting Help

If you encounter issues not covered here:

1. Check the [main testing documentation](README.md)
2. Review [pytest-homeassistant-custom-component docs](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
3. Look at [Home Assistant developer docs](https://developers.home-assistant.io/docs/development_testing)
4. Open an issue in this repository with details about your error

## Cleanup

To remove the virtual environment when done:

```bash
# Deactivate first
deactivate

# Then remove the directory
rm -rf venv/
```
