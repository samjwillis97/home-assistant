#!/usr/bin/env python3
"""
Home Assistant Configuration Validator

This script validates the Home Assistant configuration by checking:
1. YAML syntax
2. Scene entity ID conversions
3. Input text length limits
4. Scene references exist
"""

import yaml
import json
import glob
import sys
from pathlib import Path


def scene_name_to_entity_id(name: str) -> str:
    """
    Convert a scene name to entity ID following Home Assistant's convention.

    Home Assistant converts scene names to entity IDs by:
    - Converting to lowercase
    - Replacing spaces with underscores
    - Removing special characters like : ( ) /
    - Collapsing multiple underscores
    """
    entity_id = name.lower()
    # Remove colons and other special chars
    entity_id = entity_id.replace(':', '').replace('(', '').replace(')', '').replace('/', '_')
    # Replace spaces with underscores
    entity_id = entity_id.replace(' ', '_')
    # Collapse multiple underscores
    while '__' in entity_id:
        entity_id = entity_id.replace('__', '_')
    # Remove trailing/leading underscores
    entity_id = entity_id.strip('_')

    return f'scene.{entity_id}'


def load_all_scenes(config_dir: Path) -> dict:
    """Load all scene files and return a dict of entity_id -> scene_data"""
    scenes = {}
    scene_files = glob.glob(str(config_dir / 'scenes' / '*' / '*.yaml'))

    for scene_file in scene_files:
        try:
            with open(scene_file, 'r') as f:
                scene_data = yaml.safe_load(f)
                if scene_data and 'name' in scene_data:
                    entity_id = scene_name_to_entity_id(scene_data['name'])
                    scenes[entity_id] = {
                        'name': scene_data['name'],
                        'file': scene_file,
                        'id': scene_data.get('id', 'unknown')
                    }
        except Exception as e:
            print(f"❌ Error loading scene file {scene_file}: {e}")
            return None

    return scenes


def validate_input_text(config_dir: Path) -> bool:
    """Validate input_text entities"""
    errors = []

    input_text_files = glob.glob(str(config_dir / 'entities' / 'input_text' / '*.yaml'))

    for file in input_text_files:
        try:
            with open(file, 'r') as f:
                data = yaml.safe_load(f)

                for entity_name, config in data.items():
                    # Check max value
                    if 'max' in config:
                        max_val = config['max']
                        if max_val > 255:
                            errors.append(
                                f"  input_text.{entity_name}: 'max' value {max_val} exceeds limit of 255"
                            )

                    # Check initial value length
                    if 'initial' in config:
                        initial = config['initial']
                        if isinstance(initial, str) and len(initial) > 255 and 'max' not in config:
                            print(f"⚠️  input_text.{entity_name}: initial value is {len(initial)} chars (no max specified, default is 255)")

        except Exception as e:
            errors.append(f"  Error loading {file}: {e}")

    if errors:
        print("❌ Input text validation errors:")
        for error in errors:
            print(error)
        return False

    return True


def validate_scene_references(config_dir: Path, scenes: dict) -> bool:
    """Validate that all scene references in automation/scripts exist"""
    errors = []

    # Load scene map from automation file
    automation_file = config_dir / 'automations' / 'house' / 'apply_mode_scenes.yaml'
    if automation_file.exists():
        try:
            with open(automation_file, 'r') as f:
                data = yaml.safe_load(f)
                # Extract mode_map from variables section
                scene_map = data.get('variables', {}).get('mode_map', {})

                if not scene_map:
                    errors.append("Error: mode_map not found in automation variables")
                    return False

                print("\n📋 Checking scene references in apply_mode_scenes automation:")

                for mode, config in scene_map.items():
                    # Check 'always' scenes
                    for scene_id in config.get('always', []):
                        if scene_id in scenes:
                            print(f"  ✅ {mode}: {scene_id} → \"{scenes[scene_id]['name']}\"")
                        else:
                            errors.append(f"  ❌ {mode}: {scene_id} NOT FOUND")
                            print(errors[-1])

                    # Check 'conditional' scenes
                    for cond in config.get('conditional', []):
                        if isinstance(cond, dict) and 'scene' in cond:
                            scene_id = cond['scene']
                            if scene_id in scenes:
                                print(f"  ✅ {mode}: {scene_id} → \"{scenes[scene_id]['name']}\" (conditional)")
                            else:
                                errors.append(f"  ❌ {mode}: {scene_id} NOT FOUND (conditional)")
                                print(errors[-1])

        except Exception as e:
            errors.append(f"Error loading automation file: {e}")

    if errors:
        print("\n❌ Scene reference validation failed!")
        print("\n💡 Available bedroom scenes:")
        for entity_id, scene_data in scenes.items():
            if 'bedroom' in entity_id:
                print(f"  {entity_id} → \"{scene_data['name']}\"")
        return False

    return True


def main():
    config_dir = Path('/home/user/home-assistant')

    print("🔍 Home Assistant Configuration Validator")
    print("=" * 60)

    # Load all scenes
    print("\n📦 Loading scenes...")
    scenes = load_all_scenes(config_dir)
    if scenes is None:
        print("❌ Failed to load scenes")
        sys.exit(1)
    print(f"✅ Loaded {len(scenes)} scenes")

    # Validate input_text
    print("\n🔤 Validating input_text entities...")
    input_text_valid = validate_input_text(config_dir)

    # Validate scene references
    scene_refs_valid = validate_scene_references(config_dir, scenes)

    # Summary
    print("\n" + "=" * 60)
    if input_text_valid and scene_refs_valid:
        print("✅ All validations passed!")
        sys.exit(0)
    else:
        print("❌ Validation failed - see errors above")
        sys.exit(1)


if __name__ == '__main__':
    main()
