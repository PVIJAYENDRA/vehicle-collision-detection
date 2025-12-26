# Enhanced Alert System - Based on Distance, Speed, and Angle

## Overview

The alert system now triggers warnings based on three key factors:
1. **Distance** - How close the vehicle is
2. **Speed** - How fast the vehicle is moving
3. **Angle** - Whether the vehicle is on a collision path

## Alert Thresholds

### Distance Thresholds (in meters)
- **CRITICAL**: ≤ 5.0m - Very close, immediate danger
- **HIGH**: ≤ 10.0m - Close, high risk
- **MEDIUM**: ≤ 20.0m - Moderate distance, medium risk
- **LOW**: ≤ 30.0m - Far but still monitored

### Speed Thresholds (in pixels/frame)
- **CRITICAL**: ≥ 20.0 px/s - Very fast movement
- **HIGH**: ≥ 15.0 px/s - Fast movement
- **MEDIUM**: ≥ 10.0 px/s - Moderate speed
- **LOW**: ≥ 5.0 px/s - Slow but moving

### Angle Thresholds (in degrees from center)
- **CRITICAL**: ≤ 15° - Directly in path
- **HIGH**: ≤ 30° - On collision path
- **MEDIUM**: ≤ 45° - Approaching path
- **LOW**: ≤ 60° - Near path

## Alert Logic

The system uses a **weighted scoring system**:
- **Distance**: 40% weight (most important)
- **Speed**: 35% weight
- **Angle**: 25% weight

### Alert Severity Levels

**CRITICAL Alert** - Triggered when:
- Vehicle is within 5m AND moving at any speed AND directly in path (≤15°)
- OR vehicle is very close (≤2.5m) regardless of other factors
- OR very high speed (≥20 px/s) approaching within 10m at ≤30° angle

**HIGH Alert** - Triggered when:
- Vehicle within 10m AND moving at medium+ speed AND on path (≤30°)
- OR combined risk score ≥ 0.7

**MEDIUM Alert** - Triggered when:
- Vehicle within 20m AND moving AND approaching path (≤45°)
- OR combined risk score ≥ 0.5

**LOW Alert** - Triggered when:
- Vehicle within 30m AND moving AND near path (≤60°)
- OR combined risk score ≥ 0.3

## Alert Display

### Visual Indicators

1. **Bounding Box Colors**:
   - Green: Safe vehicle (no alert)
   - Red: Vehicle with collision risk

2. **Alert Text**:
   - Shows severity level (CRITICAL, HIGH, MEDIUM, LOW)
   - Shows which factors triggered: CLOSE/FAST/DIRECT PATH
   - Example: "⚠ CRITICAL: CLOSE | FAST | DIRECT"

3. **Alert Background Colors**:
   - Red: Critical/High alerts
   - Orange: Medium/Low alerts

### Information Display

For each vehicle, you'll see:
- **ID**: Vehicle tracking ID
- **Speed**: Movement speed in pixels/second
- **Distance**: Estimated distance in meters
- **Angle**: Relative angle in degrees
- **Alert Status**: If collision risk detected

## Configuration

You can adjust thresholds in `config.py`:

```python
# Distance thresholds
CRITICAL_DISTANCE = 5.0
HIGH_DISTANCE = 10.0
MEDIUM_DISTANCE = 20.0
LOW_DISTANCE = 30.0

# Speed thresholds
CRITICAL_SPEED = 20.0
HIGH_SPEED = 15.0
MEDIUM_SPEED = 10.0
LOW_SPEED = 5.0

# Angle thresholds
CRITICAL_ANGLE = 15.0
HIGH_ANGLE = 30.0
MEDIUM_ANGLE = 45.0
LOW_ANGLE = 60.0
```

## Examples

### Example 1: Critical Alert
- **Distance**: 4m (CRITICAL)
- **Speed**: 18 px/s (HIGH)
- **Angle**: 10° (CRITICAL - directly in path)
- **Result**: CRITICAL alert - "⚠ CRITICAL: CLOSE | FAST | DIRECT"

### Example 2: High Alert
- **Distance**: 8m (HIGH)
- **Speed**: 12 px/s (MEDIUM)
- **Angle**: 25° (HIGH - on path)
- **Result**: HIGH alert - "⚠ HIGH: Near | Fast | OnPath"

### Example 3: Medium Alert
- **Distance**: 15m (MEDIUM)
- **Speed**: 8 px/s (LOW)
- **Angle**: 40° (MEDIUM - approaching)
- **Result**: MEDIUM alert - "⚠ MEDIUM: Alert"

### Example 4: Low Alert
- **Distance**: 25m (LOW)
- **Speed**: 6 px/s (LOW)
- **Angle**: 50° (LOW - near path)
- **Result**: LOW alert - "⚠ LOW: Alert"

## Audio Alerts

Audio alerts (beep sounds) are triggered for:
- Critical alerts: Immediate beep
- High alerts: Frequent beeps
- Medium/Low alerts: Occasional beeps

## Real-Time Updates

The system continuously monitors:
- Distance changes (getting closer/farther)
- Speed changes (accelerating/decelerating)
- Angle changes (changing direction)

Alerts update in real-time as these factors change.

## Customization

### Make Alerts More Sensitive
Lower the thresholds:
```python
CRITICAL_DISTANCE = 3.0  # Alert sooner
CRITICAL_SPEED = 15.0    # Alert at lower speeds
CRITICAL_ANGLE = 20.0    # Alert at wider angles
```

### Make Alerts Less Sensitive
Raise the thresholds:
```python
CRITICAL_DISTANCE = 8.0  # Alert later
CRITICAL_SPEED = 25.0    # Alert at higher speeds
CRITICAL_ANGLE = 10.0    # Alert only for direct path
```

## Best Practices

1. **Calibrate Distance**: Adjust `PIXELS_PER_METER` in config.py for accurate distance measurements
2. **Adjust for Environment**: 
   - Urban: Lower thresholds (more alerts)
   - Highway: Higher thresholds (fewer false alerts)
3. **Test and Tune**: Use different scenarios to find optimal thresholds
4. **Monitor Performance**: Check alert accuracy and adjust as needed


