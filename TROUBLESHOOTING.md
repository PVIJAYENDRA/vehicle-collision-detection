# Troubleshooting Guide - Vehicle Detection Issues

## Problem: Vehicles Not Being Detected/Marked

If vehicles are not being detected or marked, follow these steps:

### Step 1: Run Debug Script

First, test if detection is working at all:

```bash
python debug_detection.py vv.mp4
```

Or with camera:
```bash
python debug_detection.py --camera 0
```

This will show:
- What objects are being detected
- Which classes are found
- Confidence scores
- Visual output with bounding boxes

### Step 2: Check Configuration

Edit `config.py` and verify:

1. **Confidence Threshold** (currently 0.25):
   ```python
   CONFIDENCE_THRESHOLD = 0.25  # Lower = more detections, Higher = fewer but more accurate
   ```
   - If too high, vehicles might not be detected
   - Try lowering to 0.1 for more detections
   - Try raising to 0.4 for more accurate detections

2. **Vehicle Classes** (currently [2, 3, 5, 7]):
   ```python
   VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck
   ```
   - Class 2 = car
   - Class 3 = motorcycle  
   - Class 5 = bus
   - Class 7 = truck
   - If you want bicycles too: `[1, 2, 3, 5, 7]`

### Step 3: Common Issues and Solutions

#### Issue: No vehicles detected at all

**Possible causes:**
1. Video/image has no vehicles
2. Confidence threshold too high
3. Vehicles too small or unclear
4. Model not loaded properly

**Solutions:**
- Lower `CONFIDENCE_THRESHOLD` to 0.1 in `config.py`
- Check video quality and lighting
- Try with a different video/image
- Verify model loaded (check GUI status)

#### Issue: Some vehicles detected but not all

**Possible causes:**
1. Vehicles too small in frame
2. Partial occlusion
3. Unusual vehicle types
4. Poor lighting/quality

**Solutions:**
- Lower confidence threshold
- Improve video quality
- Use larger YOLOv8 model (yolov8s.pt or yolov8m.pt)
- Check if vehicles are actually visible

#### Issue: Boxes drawn but very small/invisible

**Possible causes:**
1. Display scaling issue
2. Boxes drawn outside frame
3. Color matching background

**Solutions:**
- Boxes are now thicker (3px) and green
- Check if boxes appear in debug script
- Verify frame dimensions

#### Issue: Detection works in debug but not in GUI/CLI

**Possible causes:**
1. Threading issues
2. Frame not being processed
3. Display update issues

**Solutions:**
- Check console for error messages
- Verify model is loaded (GUI shows "Model loaded successfully")
- Try restarting the application
- Check if video/image is loading correctly

### Step 4: Adjust Settings

If detection is working but not optimal:

1. **For more detections:**
   ```python
   CONFIDENCE_THRESHOLD = 0.1  # Very sensitive
   ```

2. **For more accurate detections:**
   ```python
   CONFIDENCE_THRESHOLD = 0.4  # More strict
   ```

3. **For better model accuracy:**
   - In `gui_app.py` or `run_detection.py`, change:
   ```python
   self.model = YOLO('yolov8s.pt')  # or 'yolov8m.pt'
   ```
   (Note: Larger models are slower but more accurate)

### Step 5: Verify Detection Pipeline

The detection process:
1. Frame → YOLOv8 model → Detections
2. Filter by vehicle classes → Valid detections
3. Draw bounding boxes → Visual output
4. Track vehicles → Speed/distance calculation

Check each step:
- Step 1: Run debug script to see raw detections
- Step 2: Check if vehicle classes match
- Step 3: Verify boxes are drawn (check debug output)
- Step 4: Check tracking in info panel

### Step 6: Test with Known Good Video

Test with a video that definitely has vehicles:
- Traffic videos from YouTube
- Highway footage
- Parking lot videos
- Clear, well-lit vehicle footage

### Quick Fixes

**Quick Fix 1: Lower Confidence**
```python
# In config.py
CONFIDENCE_THRESHOLD = 0.1
```

**Quick Fix 2: Add More Classes**
```python
# In config.py - include bicycles
VEHICLE_CLASSES = [1, 2, 3, 5, 7]
```

**Quick Fix 3: Use Larger Model**
```python
# In gui_app.py line ~33, change:
self.model = YOLO('yolov8s.pt')  # Instead of yolov8n.pt
```

### Debug Output

When running, check console for:
- "Detected X vehicles" messages
- Any error messages
- Model loading status

### Still Not Working?

1. **Check video content:**
   - Does the video actually have vehicles?
   - Are vehicles clearly visible?
   - Is lighting good?

2. **Test with debug script:**
   ```bash
   python debug_detection.py vv.mp4
   ```
   This will show exactly what's being detected

3. **Try different input:**
   - Test with live camera
   - Test with different video
   - Test with clear image

4. **Check system requirements:**
   - Python 3.8+
   - All dependencies installed
   - Sufficient RAM/GPU

### Expected Behavior

**Working correctly:**
- Green boxes around vehicles
- "Vehicle" labels on boxes
- Vehicle count in status
- Info panel shows vehicle details

**Not working:**
- No boxes visible
- Status shows "0 vehicles"
- Info panel empty
- No console output

### Contact/Report

If issues persist:
1. Run debug script and note output
2. Check config.py settings
3. Note what input you're using (video/image/live)
4. Check console for errors


