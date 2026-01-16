# Claude Code Settings

This directory contains configuration for Claude Code to enhance the development experience for this Home Assistant repository.

## Features

### Session Start Hook
When you start a new Claude Code session, you'll see:
- Current Home Assistant version
- Available validation tools
- Helpful reminders

### User Prompt Submit Hook
Before each prompt is submitted, Claude Code will:
- Check for uncommitted changes
- Show a warning if there are uncommitted files (non-blocking)

### Custom Commands

The following custom commands are available:

#### `lint`
Runs yamllint on all YAML files to check syntax and style.
```bash
yamllint .
```

#### `format-check`
Validates that all YAML files are properly formatted with Prettier.
```bash
prettier --check '**/*.{yaml,yml}'
```

#### `validate`
Runs full Home Assistant configuration validation using Docker.
**Note:** Requires Docker to be installed and running.
```bash
./scripts/validate-config.sh
```

#### `check-all`
Runs both yamllint and prettier checks in sequence.
Useful for quick validation before committing.

## Testing the Settings

All hooks and commands have been tested and verified:

1. **Session Start Hook** - Displays welcome message with HA version
2. **User Prompt Submit Hook** - Checks for uncommitted changes
3. **Custom Commands**:
   - `lint` - ✅ Passes (shows warnings for long lines, which is acceptable)
   - `format-check` - ✅ All files properly formatted
   - `check-all` - ✅ Runs both checks successfully

## Integration with Existing Tools

These settings integrate with:
- **Nix Flake** (`flake.nix`) - Provides development environment
- **Pre-commit Hooks** - Automated checks via git hooks
- **GitHub Actions** (`.github/workflows/checks.yaml`) - CI/CD validation
- **Validation Script** (`scripts/validate-config.sh`) - Docker-based HA config validation

## Usage Tips

- Run `check-all` before committing to catch issues early
- The `validate` command requires Docker, useful for full config validation
- Warnings from yamllint about line length are acceptable (from blueprint files)
- The settings work in any environment with the basic tools installed
