# Project Structure

## Core Application Files

### Main Entry Points
- **`gui_app.py`** - GUI application (recommended for users)
- **`run_detection.py`** - Command-line interface with full feature support

### Core Modules
- **`vehicle_tracker.py`** - Kalman filter-based vehicle tracking
- **`collision_detector.py`** - Distance, angle, and collision prediction
- **`alert_system.py`** - Visual and audio alert system
- **`input_handler.py`** - Handles image, video, and live feed inputs

### Configuration
- **`config.py`** - All system configuration parameters

### Dependencies
- **`requirements.txt`** - Python package dependencies

## Documentation

- **`README.md`** - Main documentation and usage guide
- **`GUI_GUIDE.md`** - Detailed GUI usage instructions
- **`TESTING_GUIDE.md`** - Testing instructions and troubleshooting

## Data Files

- **`yolov8n.pt`** - YOLOv8 model file (auto-downloaded)
- **`vv.mp4`** - Your video file (user data)
- **`synthetic_test.mp4`** - Generated test video (can be deleted)

## Usage

### GUI (Recommended)
```bash
python gui_app.py
```

### Command Line
```bash
# Image
python run_detection.py --input image.jpg

# Video
python run_detection.py --input video.mp4

# Live Feed
python run_detection.py --input 0

# Multi-view
python run_detection.py --multi-view
```

## Removed Files

The following redundant files have been removed:
- `main.py` - Replaced by `run_detection.py`
- `test_single_camera.py` - Functionality in `run_detection.py`
- `launch_gui.py` - Use `gui_app.py` directly
- `examples.py` - Redundant helper script
- `quick_test.py` - Testing helper (consolidated)
- `test_with_video.py` - Testing helper (consolidated)
- `download_test_videos.py` - Testing helper (consolidated)
- `FEATURES.md` - Redundant documentation
- `GUI_FEATURES.md` - Redundant documentation
- `QUICKSTART.md` - Consolidated into README
- `USAGE_GUIDE.md` - Consolidated into README


