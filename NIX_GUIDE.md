# Nix Flake Integration

This project includes a comprehensive Nix flake configuration for development and testing.

## Quick Start

```bash
# Enter the development shell
nix develop

# Available commands will be displayed:
# - validate-ha-config: Validate Home Assistant configuration
# - run-ha-tests: Run automation logic tests
```

## Features

### Development Shell

The `nix develop` command provides:
- Python 3.13 with venv support
- Docker for Home Assistant config validation
- Pre-commit hooks (yamllint, prettier, HA config check, pytest)
- Custom commands for validation and testing

### Pre-commit Hooks

Automatically configured when you enter the development shell:

1. **yamllint** - YAML syntax checking
2. **prettier** - YAML formatting validation
3. **home-assistant-config** - HA configuration validation
4. **pytest** - Automation logic tests (runs on pre-push)

The pytest hook runs on `pre-push` (not on every commit) to avoid slowing down your workflow.

### Custom Commands

#### `validate-ha-config`

Validates your Home Assistant configuration using Docker:

```bash
validate-ha-config
```

This wrapper script:
- Sets the PROJECT_ROOT environment variable
- Runs the validation script with proper context
- Uses Docker to spin up a temporary HA instance for validation

#### `run-ha-tests`

Runs automation logic tests with pytest:

```bash
# Run all tests with coverage
run-ha-tests

# Run specific test file
run-ha-tests tests/automations/test_house_mode.py

# Run tests matching pattern
run-ha-tests -k test_work_mode

# Run with custom pytest arguments
run-ha-tests -v -s
```

This wrapper script:
- Automatically creates `.venv` if it doesn't exist
- Installs dependencies from `requirements-test.txt` if needed
- Runs pytest with sensible defaults (verbose, coverage)
- Supports all pytest command-line options

## Running Without Entering the Shell

You can run commands directly without entering the shell:

```bash
# Run tests
nix run .#test

# Run validation
nix run .#validate
```

## Available Apps

The flake exposes two apps:

- `test` - Run automation tests
- `validate` - Validate HA configuration

```bash
nix run .#test       # Run tests
nix run .#validate   # Validate config
```

## Available Packages

The flake provides two packages:

- `run-ha-tests` - Test runner wrapper
- `validate-ha-config` - Config validator wrapper

```bash
nix build .#run-ha-tests
nix build .#validate-ha-config
```

## Pre-commit Hook Management

### Enabling Hooks

Hooks are automatically installed when you enter the development shell:

```bash
nix develop
# Pre-commit hooks are now active
```

### Temporarily Bypassing Hooks

If you need to bypass hooks for a specific commit:

```bash
git commit --no-verify -m "message"
```

### Running Hooks Manually

Test the hooks without making a commit:

```bash
# In the nix develop shell
pre-commit run --all-files
```

## CI/CD Integration

While the Nix flake is primarily for local development, the GitHub Actions workflow uses the same test commands:

```yaml
# .github/workflows/checks.yaml
- name: Run pytest
  run: pytest tests/ -v --cov --cov-report=term-missing
```

This ensures consistency between local and CI testing.

## Virtual Environment Management

The flake uses `.venv` directory for Python virtual environments. This directory:

- Is created automatically by `run-ha-tests` if it doesn't exist
- Is managed by the `venvShellHook` in the development shell
- Should be in `.gitignore` (it is)
- Can be safely deleted and recreated

To reset your virtual environment:

```bash
rm -rf .venv
nix develop  # Will recreate on next run-ha-tests
```

## Troubleshooting

### Issue: "command not found: run-ha-tests"

**Solution:** Make sure you're in the nix development shell:

```bash
nix develop
```

### Issue: Tests fail with import errors

**Solution:** Remove and recreate the virtual environment:

```bash
rm -rf .venv
run-ha-tests  # Will reinstall dependencies
```

### Issue: Pre-commit hooks not running

**Solution:** Exit and re-enter the development shell:

```bash
exit
nix develop
```

### Issue: "nix: command not found"

**Solution:** Install Nix using the official installer:

```bash
# Multi-user installation (recommended)
sh <(curl -L https://nixos.org/nix/install) --daemon

# Or visit https://nixos.org/download.html
```

## Customization

### Modifying Pre-commit Hooks

Edit `flake.nix` and modify the `pre-commit-check` section:

```nix
pre-commit-check = git-hooks.lib.${system}.run {
  src = ./.;
  hooks = {
    # Add or modify hooks here
    your-hook = {
      enable = true;
      name = "Your Hook";
      entry = "your-command";
      files = "\\.yaml$";
    };
  };
};
```

Then reload the shell:

```bash
exit
nix develop
```

### Adding Python Packages

If you need additional Python packages in the development environment, add them to the `python3.withPackages` section in `flake.nix`:

```nix
(pkgs.python3.withPackages (
  python-pkgs: with python-pkgs; [
    # Add packages here
    requests
    pyyaml
  ]
))
```

For testing dependencies, add them to `requirements-test.txt` instead.

## Why Nix?

Benefits of using Nix for this project:

- **Reproducible environments**: Everyone gets the exact same tools and versions
- **No system pollution**: All dependencies are isolated
- **Declarative configuration**: The entire dev environment is described in `flake.nix`
- **Cross-platform**: Works on Linux, macOS, and WSL2
- **Automatic setup**: Pre-commit hooks install automatically
- **Caching**: Nix caches built packages for fast setup

## Resources

- [Nix Package Manager](https://nixos.org/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [flake-utils](https://github.com/numtide/flake-utils)
- [git-hooks.nix](https://github.com/cachix/git-hooks.nix)

## See Also

- [TESTING.md](TESTING.md) - Testing framework overview
- [tests/README.md](tests/README.md) - Detailed testing guide
- [tests/QUICK_REFERENCE.md](tests/QUICK_REFERENCE.md) - Quick reference for testing commands
