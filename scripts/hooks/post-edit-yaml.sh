#!/usr/bin/env bash
set -e

# Hook script for validating YAML files after Write/Edit operations
# This runs yamllint, prettier, and Home Assistant config validation

# Read hook input from stdin
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

# Only process YAML files
if [[ ! "$file_path" =~ \.(yaml|yml)$ ]]; then
  exit 0
fi

# Change to project directory
cd "$CLAUDE_PROJECT_DIR"

echo "🔍 Validating YAML file: $file_path"

# Track if any checks failed
failed=0

# Check if yamllint is available
if command -v yamllint &> /dev/null; then
  echo "Running yamllint..."
  if ! yamllint "$file_path" 2>&1; then
    echo "❌ yamllint found issues"
    failed=1
  else
    echo "✅ yamllint passed"
  fi
else
  echo "⚠️  yamllint not found, skipping"
fi

# Check if prettier is available
if command -v prettier &> /dev/null; then
  echo "Running prettier..."
  if ! prettier --check "$file_path" 2>&1; then
    echo "❌ prettier found formatting issues"
    echo "💡 Run: prettier --write \"$file_path\" to fix"
    failed=1
  else
    echo "✅ prettier passed"
  fi
else
  echo "⚠️  prettier not found, skipping"
fi

# Run Home Assistant config validation for configuration files
# Skip this for test files or non-config YAML files
if [[ "$file_path" =~ (configuration\.yaml|automations\.yaml|scripts\.yaml|scenes\.yaml|customize\.yaml) ]]; then
  echo "Running Home Assistant config validation..."
  if ! "$CLAUDE_PROJECT_DIR"/scripts/validate-config.sh 2>&1; then
    echo "❌ Home Assistant config validation failed"
    failed=1
  else
    echo "✅ Home Assistant config validation passed"
  fi
fi

if [ $failed -eq 1 ]; then
  echo ""
  echo "⚠️  Some validation checks failed. Please review the issues above."
  # Use exit code 2 to block and show feedback to Claude
  exit 2
fi

echo "✅ All validation checks passed"
exit 0
