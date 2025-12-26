"""
Configuration file for Vehicle Collision Detection System
"""

# Input sources for each view
# Can be:
#   - Integer: Camera/webcam index (e.g., 0, 1, 2)
#   - String path: Image file (jpg, png, etc.) or Video file (mp4, avi, etc.)
#   - None: Skip this view
CAMERA_SOURCES = {
    'front': 0,   # Front camera/webcam index, or 'front_video.mp4', or 'front_image.jpg'
    'back': 1,    # Back camera/webcam index, or 'back_video.mp4', or 'back_image.jpg'
    'left': 2,    # Left camera/webcam index, or 'left_video.mp4', or 'left_image.jpg'
    'right': 3    # Right camera/webcam index, or 'right_video.mp4', or 'right_image.jpg'
}

# Single input mode (for single image/video/live feed processing)
# Set to None to use multi-view mode, or set to a single input source
SINGLE_INPUT_MODE = None  # e.g., 0 for live feed, 'video.mp4' for video, 'image.jpg' for image

# Detection settings
CONFIDENCE_THRESHOLD = 0.25  # Minimum confidence for vehicle detection (lowered for better detection)
IOU_THRESHOLD = 0.45        # Intersection over Union threshold

# Vehicle classes in COCO dataset (YOLOv8)
# COCO class indices: 
#   0=person, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck
# Note: YOLOv8 uses COCO format
# Verified: class 2=car, 3=motorcycle, 5=bus, 7=truck
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

# Alternative: If you want to detect all vehicles including bicycles
# VEHICLE_CLASSES = [1, 2, 3, 5, 7]  # bicycle, car, motorcycle, bus, truck

# Collision detection parameters - Alert thresholds based on Distance, Speed, and Angle
# Distance thresholds (in meters)
CRITICAL_DISTANCE = 5.0          # Critical alert if vehicle within this distance
HIGH_DISTANCE = 10.0             # High alert if vehicle within this distance
MEDIUM_DISTANCE = 20.0           # Medium alert if vehicle within this distance
LOW_DISTANCE = 30.0              # Low alert if vehicle within this distance

# Speed thresholds (in pixels/frame)
CRITICAL_SPEED = 20.0            # Critical alert if speed above this
HIGH_SPEED = 15.0                # High alert if speed above this
MEDIUM_SPEED = 10.0              # Medium alert if speed above this
LOW_SPEED = 5.0                  # Low alert if speed above this

# Angle thresholds (in degrees from center)
# Vehicles directly ahead/behind (0-15°) are most dangerous
CRITICAL_ANGLE = 15.0            # Critical if within this angle from center
HIGH_ANGLE = 30.0                # High if within this angle
MEDIUM_ANGLE = 45.0              # Medium if within this angle
LOW_ANGLE = 60.0                 # Low if within this angle

# Legacy parameters (kept for backward compatibility)
MIN_DISTANCE_THRESHOLD = 50      # Minimum distance in pixels for collision warning
SPEED_THRESHOLD = 5.0            # Minimum speed (pixels/frame) to consider
COLLISION_TIME_THRESHOLD = 2.0   # Time to collision threshold (seconds)
ANGLE_TOLERANCE = 30             # Angle tolerance in degrees

# Camera calibration (adjust based on your camera setup)
FOCAL_LENGTH = 700              # Focal length in pixels
REAL_VEHICLE_WIDTH = 1.8        # Average vehicle width in meters
PIXELS_PER_METER = 50           # Calibration factor

# Display settings
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
SHOW_DETECTIONS = True
SHOW_TRACKS = True
SHOW_INFO = True

# Alert settings
ALERT_SOUND_ENABLED = True
ALERT_COLOR = (0, 0, 255)  # Red color for alerts
WARNING_COLOR = (0, 165, 255)  # Orange color for warnings

# Kalman filter parameters for tracking
PROCESS_NOISE = 0.03
MEASUREMENT_NOISE = 0.3

