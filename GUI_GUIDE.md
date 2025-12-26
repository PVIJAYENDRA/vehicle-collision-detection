# GUI Application Guide

## Overview

The GUI application provides an easy-to-use interface for the Vehicle Collision Detection System. It supports all three input modes: Image, Video File, and Live Feed.

## Getting Started

### Launch the GUI

```bash
python gui_app.py
```

The application window will open with a modern dark theme interface.

## Interface Layout

### Left Panel - Controls

#### 1. Input Type Selection
Choose your input type:
- **Image File**: Process a single image
- **Video File**: Process a video file frame by frame
- **Live Feed**: Real-time processing from camera

#### 2. Input Source Selection
- **Browse / Select Button**: 
  - For Image/Video: Opens file browser
  - For Live Feed: Uses selected camera index
- **Camera Index** (Live Feed only): Select camera number (0, 1, 2, etc.)

#### 3. Controls
- **Start Detection**: Begin processing
- **Stop Detection**: Stop and reset
- **Pause**: Pause/resume (Video only)

#### 4. Status Panel
- Current status of the system
- Model loading status

### Right Panel - Display and Information

#### 1. Video Display
- Large canvas showing processed frames
- Real-time vehicle detection visualization
- Bounding boxes, trajectories, and annotations

#### 2. Vehicle Information Panel
- Summary statistics
- Detailed information for each detected vehicle:
  - Vehicle ID
  - Speed (pixels/second)
  - Distance (meters)
  - Angle (degrees)
  - Collision risk status
  - Time to collision (if applicable)

#### 3. Alert Indicator
- Visual alerts for collision risks
- Color-coded by severity:
  - 🔴 Critical
  - 🟠 High
  - 🟡 Medium/Low

## Step-by-Step Usage

### Processing an Image

1. Select **"Image File"** radio button
2. Click **"Browse / Select"** button
3. Choose an image file (.jpg, .png, .bmp, etc.)
4. Click **"Start Detection"**
5. View results in the display and information panels

### Processing a Video

1. Select **"Video File"** radio button
2. Click **"Browse / Select"** button
3. Choose a video file (.mp4, .avi, .mov, etc.)
4. Click **"Start Detection"**
5. Video will play automatically
6. Use **"Pause"** to pause/resume playback
7. Use **"Stop Detection"** to stop

### Using Live Feed

1. Select **"Live Feed"** radio button
2. Set camera index (usually 0 for default webcam)
3. Click **"Use Camera"** or **"Start Detection"**
4. Real-time processing begins
5. Use **"Stop Detection"** to stop

## Features

### Visual Indicators

- **Green Boxes**: Detected vehicles (safe)
- **Red Boxes**: Vehicles with collision risk
- **Blue Lines**: Vehicle trajectories
- **Red Circles**: Vehicle centers with alerts
- **Text Annotations**: ID, speed, distance, angle

### Alert System

- **Visual Alerts**: Colored borders and warning indicators
- **Audio Alerts**: Beep sounds for critical collisions
- **Information Panel**: Detailed alert messages

### Vehicle Information

For each detected vehicle, you'll see:
- **ID**: Unique tracking identifier
- **Speed**: Movement speed in pixels/second
- **Distance**: Estimated distance in meters
- **Angle**: Relative angle in degrees (0-360°)
- **Collision Status**: Risk level (none, low, medium, high, critical)
- **Time to Collision**: Estimated time if on collision course

## Controls Reference

| Button | Function |
|--------|----------|
| **Start Detection** | Begin processing selected input |
| **Stop Detection** | Stop processing and reset |
| **Pause** | Pause/resume video playback (Video only) |
| **Browse / Select** | Select file or camera |

## Tips

1. **Model Loading**: The YOLOv8 model loads automatically in the background. Wait for "Model loaded successfully" before starting.

2. **Performance**: 
   - Processing speed depends on your hardware
   - GPU acceleration is used if available
   - For better accuracy, the model can be changed in code (yolov8s.pt, yolov8m.pt)

3. **Video Playback**:
   - Videos process at ~30 FPS
   - Use pause to examine specific frames
   - Frame counter shows progress

4. **Live Feed**:
   - Ensure camera is not used by other applications
   - Try different camera indices if default doesn't work
   - Processing is continuous until stopped

5. **Image Processing**:
   - Single frame analysis
   - Results are static (no playback controls)
   - Perfect for testing and analysis

## Troubleshooting

### "Model is still loading"
- Wait a few seconds for the model to load
- Check your internet connection (model downloads on first run)

### "Please select an input source first!"
- Make sure you've selected a file or camera before starting

### Camera not working
- Try different camera indices (0, 1, 2, etc.)
- Check if camera is used by another application
- Verify camera permissions

### File not loading
- Check file path is correct
- Verify file format is supported
- Ensure file is not corrupted

### GUI is slow
- Close other applications
- Reduce video resolution in config.py
- Use smaller YOLOv8 model (yolov8n.pt)

## Keyboard Shortcuts

Currently, all controls are mouse-based. Keyboard shortcuts may be added in future versions.

## Advanced Configuration

Edit `config.py` to adjust:
- Detection thresholds
- Collision parameters
- Display settings
- Alert settings

## System Requirements

- Python 3.8+
- Tkinter (usually included with Python)
- OpenCV
- PIL/Pillow
- All dependencies from requirements.txt

## Next Steps

- Try processing different types of inputs
- Experiment with different camera angles
- Adjust detection parameters in config.py
- Review vehicle information for analysis


