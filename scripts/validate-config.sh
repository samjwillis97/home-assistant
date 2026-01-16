#!/usr/bin/env bash
set -e

# Script to validate Home Assistant configuration using Docker
# Can be used locally or in CI/CD environments

# Determine project root
if [ -n "$PROJECT_ROOT" ]; then
  # Use PROJECT_ROOT if set (e.g., by Nix wrapper or environment)
  :
elif [[ "$(dirname "${BASH_SOURCE[0]}")" == /nix/store/* ]]; then
  # If running from Nix store without PROJECT_ROOT, use current directory
  PROJECT_ROOT="$(pwd)"
else
  # Otherwise, script is in scripts/ directory
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Read Home Assistant version from .HA_VERSION file
if [ ! -f "$PROJECT_ROOT/.HA_VERSION" ]; then
  echo "❌ .HA_VERSION file not found at: $PROJECT_ROOT/.HA_VERSION"
  exit 1
fi

HA_VERSION=$(cat "$PROJECT_ROOT/.HA_VERSION" | tr -d '[:space:]')

echo "🔍 Validating Home Assistant configuration..."
echo "📦 Using Home Assistant version: $HA_VERSION"

# Run Docker validation
output=$(docker run --rm \
  -v "$PROJECT_ROOT:/config" \
  homeassistant/home-assistant:$HA_VERSION \
  python -m homeassistant --config /config --script check_config 2>&1)

echo "$output"

# Check for ERROR in output (case-insensitive), but skip "Unknown device" errors
if echo "$output" | grep -i "ERROR" | grep -iv "Unknown device" | grep -q .; then
  echo "❌ Configuration check found errors"
  exit 1
fi

# Check for the success message or that config testing was attempted
if echo "$output" | grep -q "Testing configuration at"; then
  echo "✅ Configuration check passed (ignoring Unknown device errors)"
elif echo "$output" | grep -q "Configuration valid"; then
  echo "✅ Configuration check passed"
else
  echo "❌ Configuration validation did not complete successfully"
  exit 1
fi
