# House Mode System

The house mode system is a scene-based automation system that automatically manages the state of the home based on time-of-day and presence triggers.

## Available Modes

| Mode | Purpose | Active Times |
|------|---------|--------------|
| **default** | General daytime mode | Weekends 09:00-18:00 |
| **wake up** | Morning transition | Weekdays 06:00-08:00, Weekends 07:00-09:00 |
| **work** | Work hours mode | Weekdays 08:00-17:00 (not on holidays) |
| **away** | Nobody home (security mode) | Manual trigger via iPhone automations |
| **dinner** | Evening dinner time | Daily 18:00-20:00 |
| **relaxation** | Post-dinner evening | Daily 20:00+ |
| **bedtime** | Pre-sleep evening | 21:00-00:00 (when end-of-day signal received) |
| **sleep** | Night mode | 02:00-07:00, or manual via bedroom button |

## Mode Priority System

The mode automation (`mode.yaml`) uses a **priority-based choose structure** to prevent unintended mode transitions. Conditions are evaluated in order from highest to lowest priority.

### Priority 1: Event-Driven Changes (Immediate Override)

These triggers **immediately** change the mode, regardless of time or current state:

- **Away mode turned ON** (`input_boolean.house_mode_away` → ON)
  - Triggered by iPhone automation when leaving home
  - Immediately switches to "away" mode
  - Activates security features (cameras ON, all lights OFF)

### Priority 2: Protected Modes (Block Time Transitions)

These conditions **prevent** time-based triggers from overriding certain modes:

#### Away Mode Protection
- **Always protected** - Cannot be overridden by ANY time pattern
- **Only exits** when `input_boolean.house_mode_away` is turned OFF
- Prevents wake-up time from switching mode when you're not home

#### Sleep/Bedtime Mode Protection
- **Protected except during:**
  - Wake-up time windows (06:00-08:00 weekday / 07:00-09:00 weekend)
  - Returning home from away mode (`house_away_turned_off` trigger)
- Allows natural wake-up transition while preventing mid-sleep interruptions

### Priority 3: Time-Based Scheduling

Time patterns trigger mode changes based on the current time. Evaluated in order:

1. **Wake-up** (06:00-08:00 weekday / 07:00-09:00 weekend)
2. **Work** (08:00-17:00 weekday, not on holidays)
3. **Default** (09:00-18:00 weekend)
4. **Dinner** (18:00+)
5. **Relaxation** (20:00+)
6. **Bedtime** (21:00-00:00, requires end-of-day signal)
7. **Sleep** (02:00-07:00)

**Note:** The automation uses `mode: queued` to ensure all state changes are processed in order.

## Key Entities

### Input Selects
- `input_select.house_mode` - Primary mode state (the single source of truth)

### Input Booleans
- `input_boolean.house_mode_away` - Away mode trigger (controlled by iPhone automations)
- `input_boolean.sam_home` - Sam's presence (affects work mode scenes)
- `input_boolean.maddy_home` - Maddy's presence (affects work mode scenes)
- `input_boolean.holidays` - Prevents work mode activation

### Input DateTimes
- `input_datetime.wake_up_weekday_start` - Wake-up time start (weekdays)
- `input_datetime.wake_up_weekday_end` - Wake-up time end (weekdays)
- `input_datetime.wake_up_weekend_start` - Wake-up time start (weekends)
- `input_datetime.wake_up_weekend_end` - Wake-up time end (weekends)
- `input_datetime.work_start` - Work mode start time
- `input_datetime.work_end` - Work mode end time
- `input_datetime.dinner_time` - Dinner mode start time
- `input_datetime.relaxation_time` - Relaxation mode start time
- `input_datetime.sleep_time_start` - Sleep mode start time
- `input_datetime.sleep_time_end` - Sleep mode end time
- `input_datetime.bedtime_window_start` - Bedtime window start
- `input_datetime.bedtime_window_end` - Bedtime window end

## Scene Activation

When the mode changes, the `apply_mode_scenes.yaml` automation activates corresponding scenes:

### Always Scenes (Unconditional)
- **work** → `scene.dining_room_work`
- **sleep** → `scene.living_room_sleep`, `scene.study_sleep`, `scene.bedroom_sleep`, `scene.dining_room_sleep`
- **away** → `scene.living_room_away` (cameras ON), `scene.dining_room_away`, `scene.study_away`, `scene.bedroom_away`
- **bedtime** → `scene.bedroom_bed_time`

### Conditional Scenes
- **work** → `scene.study_work` (only if `input_boolean.sam_home` is ON)

## Manual Overrides

### Bedroom Scene Button
- **ON press** - Activates mode-appropriate bedroom scene
- **OFF press** - **Forces sleep mode** (bypasses all time protections)

### Living Room Scene Button
- **ON/OFF press** - Controls lighting only (does NOT change mode)

## Presence Integration

### iPhone Automations (External)
- **Leaving home** → Turns ON `input_boolean.house_mode_away`
- **Arriving home** → Turns OFF `input_boolean.house_mode_away`

### Work Mode Presence
- **Sam leaving during work** → Study lights OFF
- **Sam arriving during work** → Study lights ON (`scene.study_work`)
- **Maddy leaving during work** → Desk lamp OFF
- **Maddy arriving during work** → Dining room work scene

## Testing

Comprehensive test coverage ensures mode transitions work correctly:

- `tests/automations/test_house_mode.py` - Mode transition logic (16+ tests)
- `tests/automations/test_house_apply_mode_scenes.py` - Scene activation (8+ tests)

Run tests with:
```bash
pytest tests/automations/test_house_mode.py -v
pytest tests/automations/test_house_apply_mode_scenes.py -v
```

## Recent Changes

### Fix: Prevent wake-up time from overriding away mode (commit c6022cd)
**Problem:** Wake-up time patterns were overriding away mode, causing the house to wake up when nobody was home.

**Solution:** Split protected mode logic into two separate conditions:
1. Away mode - ALWAYS protected
2. Sleep/Bedtime - Protected EXCEPT during wake-up time

This allows sleep→wake transitions while keeping away mode completely isolated.

## Configuration Tips

### Adjusting Wake-Up Times
Update the input_datetime helpers via UI or YAML to change wake-up schedules seasonally.

### Adding a New Mode
1. Add mode to `entities/input_select/house_mode.yaml`
2. Create scenes in `scenes/*/` directories
3. Add scene mapping to `apply_mode_scenes.yaml`
4. Add time-based condition to `mode.yaml` (if needed)
5. Update this README

### Changing Time Schedules
Modify the input_datetime helpers rather than editing automation YAML directly for easier seasonal adjustments.

## File Structure

```
automations/house/
├── README.md                    # This file
├── mode.yaml                    # Main mode control logic
├── apply_mode_scenes.yaml       # Scene activation automation
├── end_of_day_detector.yaml     # Bedtime trigger logic
├── sam_work.yaml                # Sam presence during work mode
└── maddy_work.yaml              # Maddy presence during work mode

entities/
├── input_select/house_mode.yaml           # Mode selector
├── input_boolean/house_mode_away.yaml     # Away mode trigger
├── input_boolean/holidays.yaml            # Holiday flag
└── input_datetime/                        # Time schedule helpers

scenes/
├── bedroom/*.yaml               # Bedroom scenes per mode
├── living_room/*.yaml           # Living room scenes per mode
├── study/*.yaml                 # Study scenes per mode
└── dining_room/*.yaml           # Dining room scenes per mode
```
