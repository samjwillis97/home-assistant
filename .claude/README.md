# Development Hooks

This project uses hooks to validate Home Assistant configuration files automatically.

## Available Hooks

### Git Pre-commit Hooks (git-hooks.nix)

For users with Nix, pre-commit hooks are automatically installed when entering the development shell:

```bash
nix develop
```

The hooks run on every git commit and validate:
- **yamllint**: YAML syntax and style
- **prettier**: YAML formatting
- **Home Assistant config**: Full configuration validation (ignores "Unknown device" errors)

### Claude Code Hooks

For Claude Code users, hooks are configured in `.claude/settings.json` and run automatically after Write/Edit operations on YAML files.

The hooks validate:
- **yamllint**: YAML syntax and style
- **prettier**: YAML formatting  
- **Home Assistant config**: For main configuration files only

#### Setup

1. The hooks are automatically active when using Claude Code in this project
2. Make sure you have the required tools installed:
   - `yamllint` - Install via `pip install yamllint` or use Nix
   - `prettier` - Install via `npm install -g prettier` or use Nix
   - `docker` - Required for Home Assistant config validation

#### How It Works

When Claude Code writes or edits a YAML file, the hook script:
1. Runs yamllint to check YAML syntax
2. Runs prettier to check formatting
3. For main config files, runs full Home Assistant validation via Docker

If any check fails, Claude Code receives feedback about the issues and can fix them.

## Manual Validation

You can also run validation manually:

```bash
# Validate Home Assistant config
./scripts/validate-config.sh

# Or use the Nix wrapper
nix develop --command validate-ha-config

# Run yamllint
yamllint .

# Run prettier
prettier --check "**/*.{yaml,yml}"
```

## Configuration Files

- `.claude/settings.json` - Claude Code hooks configuration
- `scripts/hooks/post-edit-yaml.sh` - Hook script for YAML validation
- `scripts/validate-config.sh` - Home Assistant config validation script
- `.yamllint` - yamllint configuration
- `.prettierrc` (if exists) - Prettier configuration
