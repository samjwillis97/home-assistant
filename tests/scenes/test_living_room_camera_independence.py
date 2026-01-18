"""Regression tests to ensure scenes don't control camera state.

These tests verify that camera control is handled exclusively by the
camera_away_mode automation, not by individual scenes. This prevents
the regression where camera state was managed in every scene.
"""

import pytest


@pytest.mark.asyncio
async def test_away_scene_does_not_control_camera(load_scene):
    """Test away scene does not include camera state control."""
    scene_config = await load_scene("living_room", "away.yaml")

    entities = scene_config.get("entities", {})

    # Assert: Camera state should NOT be in the scene
    assert (
        "input_boolean.living_room_camera_state" not in entities
    ), "Away scene should not control camera state - use camera_away_mode automation instead"

    # Assert: Scene should only control lights
    assert "light.living_room_lights" in entities
    assert entities["light.living_room_lights"]["state"] == "off"


@pytest.mark.asyncio
async def test_sleep_scene_does_not_control_camera(load_scene):
    """Test sleep scene does not include camera state control."""
    scene_config = await load_scene("living_room", "sleep.yaml")

    entities = scene_config.get("entities", {})

    # Assert: Camera state should NOT be in the scene
    assert (
        "input_boolean.living_room_camera_state" not in entities
    ), "Sleep scene should not control camera state - use camera_away_mode automation instead"

    # Assert: Scene should control lights
    assert "light.living_room_lights" in entities
    assert "light.living_room_lamp" in entities
    assert "light.donut_lamp" in entities


@pytest.mark.asyncio
async def test_default_scene_does_not_control_camera(load_scene):
    """Test default scene does not include camera state control."""
    scene_config = await load_scene("living_room", "default_lights.yaml")

    entities = scene_config.get("entities", {})

    # Assert: Camera state should NOT be in the scene
    assert (
        "input_boolean.living_room_camera_state" not in entities
    ), "Default scene should not control camera state - use camera_away_mode automation instead"

    # Assert: Scene should control lights
    assert "light.living_room_lights" in entities
    assert "light.living_room_lamp" in entities
    assert "light.donut_lamp" in entities


@pytest.mark.asyncio
async def test_relaxation_scene_does_not_control_camera(load_scene):
    """Test relaxation scene does not include camera state control."""
    scene_config = await load_scene("living_room", "relaxation_lights.yaml")

    entities = scene_config.get("entities", {})

    # Assert: Camera state should NOT be in the scene
    assert (
        "input_boolean.living_room_camera_state" not in entities
    ), "Relaxation scene should not control camera state - use camera_away_mode automation instead"

    # Assert: Scene should control lights with specific settings
    assert "light.living_room_lights" in entities
    assert "light.living_room_lamp" in entities
    assert "light.donut_lamp" in entities


@pytest.mark.asyncio
async def test_dinner_scene_does_not_control_camera(load_scene):
    """Test dinner scene does not include camera state control."""
    scene_config = await load_scene("living_room", "dinner_lights.yaml")

    entities = scene_config.get("entities", {})

    # Assert: Camera state should NOT be in the scene
    assert (
        "input_boolean.living_room_camera_state" not in entities
    ), "Dinner scene should not control camera state - use camera_away_mode automation instead"

    # Assert: Scene should control lights
    assert "light.living_room_lights" in entities
    assert "light.living_room_lamp" in entities
    assert "light.donut_lamp" in entities


@pytest.mark.asyncio
async def test_all_living_room_scenes_camera_independent(load_scene):
    """Test that ALL living room scenes are camera-independent.

    This comprehensive test ensures that camera control remains exclusively
    in the camera_away_mode automation, preventing future regressions where
    camera state might accidentally be added to scenes.
    """
    scene_files = [
        "away.yaml",
        "sleep.yaml",
        "default_lights.yaml",
        "relaxation_lights.yaml",
        "dinner_lights.yaml",
    ]

    for scene_file in scene_files:
        scene_config = await load_scene("living_room", scene_file)
        entities = scene_config.get("entities", {})

        assert "input_boolean.living_room_camera_state" not in entities, (
            f"Scene {scene_file} should not control camera state. "
            f"Camera control belongs exclusively in camera_away_mode automation."
        )
