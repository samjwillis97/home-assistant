"""Tests for House Apply Mode Scenes automation."""


async def test_work_mode_activates_always_scenes(automation_test):
    """Test that work mode activates the dining room work scene."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.sam_home": "off",
        },
        mock_service=("scene", "turn_on"),
    )

    # Change house mode to work
    await automation_test.state_change("input_select.house_mode", "work", "default")

    # Verify dining room work scene was activated
    assert len(automation_test.service_calls) >= 1
    call = automation_test.service_calls[0]
    entity_ids = call.data.get("entity_id")
    assert "scene.dining_room_work" in entity_ids


async def test_work_mode_activates_conditional_scene_when_sam_home(automation_test):
    """Test that work mode activates study scene when sam is home."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.sam_home": "on",  # Sam is home
        },
        mock_service=("scene", "turn_on"),
    )

    # Change house mode to work
    await automation_test.state_change("input_select.house_mode", "work", "default")

    # Verify both dining room and study work scenes were activated
    assert len(automation_test.service_calls) >= 2

    # First call should be always scenes
    always_call = automation_test.service_calls[0]
    assert "scene.dining_room_work" in always_call.data.get("entity_id")

    # Second call should be conditional scene
    conditional_call = automation_test.service_calls[1]
    entity_id = conditional_call.data.get("entity_id")
    if isinstance(entity_id, list):
        assert entity_id[0] == "scene.study_work"
    else:
        assert entity_id == "scene.study_work"


async def test_work_mode_skips_conditional_scene_when_sam_not_home(automation_test):
    """Test that work mode does NOT activate study scene when sam is not home."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "default",
            "input_boolean.sam_home": "off",  # Sam is NOT home
        },
        mock_service=("scene", "turn_on"),
    )

    # Change house mode to work
    await automation_test.state_change("input_select.house_mode", "work", "default")

    # Verify only dining room scene was activated (not study)
    automation_test.assert_service_call_count(1)
    call = automation_test.service_calls[0]
    entity_ids = call.data.get("entity_id")
    assert "scene.dining_room_work" in entity_ids
    assert "scene.study_work" not in str(automation_test.service_calls)


async def test_sleep_mode_activates_all_sleep_scenes(automation_test):
    """Test that sleep mode activates all sleep scenes."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "bedtime",
        },
        mock_service=("scene", "turn_on"),
    )

    # Change house mode to sleep
    await automation_test.state_change("input_select.house_mode", "sleep", "bedtime")

    # Verify all sleep scenes were activated
    assert len(automation_test.service_calls) >= 1
    call = automation_test.service_calls[0]
    entity_ids = call.data.get("entity_id")
    assert "scene.living_room_sleep" in entity_ids
    assert "scene.study_sleep" in entity_ids
    assert "scene.bedroom_sleep" in entity_ids
    assert "scene.dining_room_sleep" in entity_ids


async def test_away_mode_activates_all_away_scenes(automation_test):
    """Test that away mode activates all away scenes."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "default",
        },
        mock_service=("scene", "turn_on"),
    )

    # Change house mode to away
    await automation_test.state_change("input_select.house_mode", "away", "default")

    # Verify all away scenes were activated
    assert len(automation_test.service_calls) >= 1
    call = automation_test.service_calls[0]
    entity_ids = call.data.get("entity_id")
    assert "scene.living_room_away" in entity_ids
    assert "scene.dining_room_away" in entity_ids
    assert "scene.study_away" in entity_ids
    assert "scene.bedroom_away" in entity_ids


async def test_bedtime_mode_activates_bedtime_scene(automation_test):
    """Test that bedtime mode activates bedroom bedtime scene."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "relaxation",
        },
        mock_service=("scene", "turn_on"),
    )

    # Change house mode to bedtime
    await automation_test.state_change("input_select.house_mode", "bedtime", "relaxation")

    # Verify bedtime scene was activated
    assert len(automation_test.service_calls) >= 1
    call = automation_test.service_calls[0]
    entity_ids = call.data.get("entity_id")
    assert "scene.bedroom_bed_time" in entity_ids


async def test_unmapped_mode_does_not_activate_scenes(automation_test):
    """Test that modes not in the map don't activate any scenes."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "default",
        },
        mock_service=("scene", "turn_on"),
    )

    # Change to a mode not in the map (dinner)
    await automation_test.state_change("input_select.house_mode", "dinner", "default")

    # Verify no scenes were activated
    automation_test.assert_no_service_calls()


async def test_scene_activation_includes_transition(automation_test):
    """Test that scene activation includes transition time."""
    await automation_test.setup(
        automation=("house", "apply_mode_scenes.yaml"),
        entities={
            "input_select.house_mode": "default",
        },
        mock_service=("scene", "turn_on"),
    )

    # Change house mode to away
    await automation_test.state_change("input_select.house_mode", "away", "default")

    # Verify transition is included
    assert len(automation_test.service_calls) >= 1
    call = automation_test.service_calls[0]
    assert call.data.get("transition") == 2.5
