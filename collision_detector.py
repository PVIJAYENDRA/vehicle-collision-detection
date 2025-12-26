"""
Collision detection and prediction module
"""

import numpy as np
import math
from config import *


class CollisionDetector:
    """Detects and predicts potential collisions"""
    
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_center = (frame_width / 2, frame_height / 2)
        
    def calculate_distance(self, bbox, view):
        """
        Calculate distance to vehicle using bounding box size
        
        Args:
            bbox: (x, y, w, h) bounding box
            view: 'front', 'back', 'left', 'right'
        
        Returns:
            Distance in meters (estimated)
        """
        x, y, w, h = bbox
        
        # Use height of bounding box as primary indicator
        # Larger vehicles appear larger, so we normalize
        pixel_height = h
        
        # Estimate distance based on pixel size
        # This is a simplified model - in production, use proper camera calibration
        if pixel_height > 0:
            # Inverse relationship: larger pixel size = closer distance
            distance_pixels = (REAL_VEHICLE_WIDTH * FOCAL_LENGTH) / pixel_height
            distance_meters = distance_pixels / PIXELS_PER_METER
            
            # Clamp to reasonable values
            distance_meters = max(1.0, min(distance_meters, 200.0))
        else:
            distance_meters = 100.0  # Default far distance
        
        return distance_meters
    
    def calculate_angle(self, bbox, view):
        """
        Calculate angle of vehicle relative to our vehicle
        
        Args:
            bbox: (x, y, w, h) bounding box
            view: 'front', 'back', 'left', 'right'
        
        Returns:
            Angle in degrees (0-360)
        """
        x, y, w, h = bbox
        cx = x + w / 2
        cy = y + h / 2
        
        # Calculate angle from center of frame to vehicle center
        dx = cx - self.frame_center[0]
        dy = cy - self.frame_center[1]
        
        # Calculate angle in radians
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360
        if angle_deg < 0:
            angle_deg += 360
        
        # Adjust based on view direction
        if view == 'front':
            # 0 degrees = straight ahead, 90 = right, 270 = left
            pass
        elif view == 'back':
            # Flip the angle
            angle_deg = (angle_deg + 180) % 360
        elif view == 'left':
            # Rotate coordinate system
            angle_deg = (angle_deg + 90) % 360
        elif view == 'right':
            # Rotate coordinate system
            angle_deg = (angle_deg - 90) % 360
        
        return angle_deg
    
    def predict_collision(self, vehicle_info, view):
        """
        Predict if a collision is likely to occur based on Distance, Speed, and Angle
        
        Args:
            vehicle_info: Dictionary with 'position', 'velocity', 'speed', 'distance', 'angle'
            view: 'front', 'back', 'left', 'right'
        
        Returns:
            (is_collision, time_to_collision, severity)
        """
        position = vehicle_info['position']
        velocity = vehicle_info['velocity']
        speed = vehicle_info['speed']
        distance = vehicle_info.get('distance', 100.0)
        angle = vehicle_info.get('angle', 0.0)
        
        # Calculate speed magnitude
        vx, vy = velocity
        speed_magnitude = np.sqrt(vx**2 + vy**2)
        # Use the tracked speed if available, otherwise use velocity magnitude
        actual_speed = max(speed, speed_magnitude)
        
        # Calculate angle from center (0° = directly ahead/behind)
        if view in ['front', 'back']:
            # For front/back views, 0° is straight ahead/behind
            angle_from_center = abs(angle - 0)
        else:
            # For left/right views, 90° is straight ahead
            angle_from_center = abs(angle - 90)
        
        # Normalize angle to 0-180
        if angle_from_center > 180:
            angle_from_center = 360 - angle_from_center
        
        # Calculate time to collision
        time_to_collision = float('inf')
        velocity_towards_center = False
        
        # Check if vehicle is moving towards center
        dx = position[0] - self.frame_center[0]
        dy = position[1] - self.frame_center[1]
        velocity_towards_center = (vx * dx + vy * dy) < 0
        
        if actual_speed > SPEED_THRESHOLD and velocity_towards_center:
            # Convert pixel speed to approximate m/s (rough calibration)
            speed_ms = actual_speed * 0.1
            if speed_ms > 0:
                time_to_collision = distance / speed_ms
        
        # Calculate risk scores for each factor (0-1 scale, higher = more dangerous)
        # Distance score: closer = higher risk
        if distance <= CRITICAL_DISTANCE:
            distance_score = 1.0
        elif distance <= HIGH_DISTANCE:
            distance_score = 0.8
        elif distance <= MEDIUM_DISTANCE:
            distance_score = 0.6
        elif distance <= LOW_DISTANCE:
            distance_score = 0.4
        else:
            distance_score = max(0.0, 1.0 - (distance - LOW_DISTANCE) / 50.0)
        
        # Speed score: faster = higher risk
        if actual_speed >= CRITICAL_SPEED:
            speed_score = 1.0
        elif actual_speed >= HIGH_SPEED:
            speed_score = 0.8
        elif actual_speed >= MEDIUM_SPEED:
            speed_score = 0.6
        elif actual_speed >= LOW_SPEED:
            speed_score = 0.4
        else:
            speed_score = actual_speed / LOW_SPEED * 0.4
        
        # Angle score: directly ahead/behind = higher risk
        if angle_from_center <= CRITICAL_ANGLE:
            angle_score = 1.0
        elif angle_from_center <= HIGH_ANGLE:
            angle_score = 0.8
        elif angle_from_center <= MEDIUM_ANGLE:
            angle_score = 0.6
        elif angle_from_center <= LOW_ANGLE:
            angle_score = 0.4
        else:
            angle_score = max(0.0, 1.0 - (angle_from_center - LOW_ANGLE) / 60.0)
        
        # Combined risk score (weighted average)
        # Distance is most important (40%), then speed (35%), then angle (25%)
        combined_score = (distance_score * 0.4 + speed_score * 0.35 + angle_score * 0.25)
        
        # Determine severity based on combined score and individual thresholds
        is_collision = False
        severity = 'none'
        
        # Check if any critical threshold is met
        if (distance <= CRITICAL_DISTANCE and actual_speed >= LOW_SPEED and 
            angle_from_center <= CRITICAL_ANGLE):
            is_collision = True
            severity = 'critical'
        # Check if high risk combination
        elif (distance <= HIGH_DISTANCE and actual_speed >= MEDIUM_SPEED and 
              angle_from_center <= HIGH_ANGLE):
            is_collision = True
            severity = 'high'
        # Check if medium risk combination
        elif (distance <= MEDIUM_DISTANCE and actual_speed >= LOW_SPEED and 
              angle_from_center <= MEDIUM_ANGLE):
            is_collision = True
            severity = 'medium'
        # Check if low risk combination
        elif (distance <= LOW_DISTANCE and actual_speed >= LOW_SPEED and 
              angle_from_center <= LOW_ANGLE):
            is_collision = True
            severity = 'low'
        # Use combined score as fallback
        elif combined_score >= 0.7:
            is_collision = True
            severity = 'high'
        elif combined_score >= 0.5:
            is_collision = True
            severity = 'medium'
        elif combined_score >= 0.3:
            is_collision = True
            severity = 'low'
        
        # Additional check: very close vehicle regardless of other factors
        if distance <= CRITICAL_DISTANCE / 2:
            is_collision = True
            if severity == 'none' or severity == 'low':
                severity = 'high'
            elif severity != 'critical':
                severity = 'critical'
        
        # Additional check: very high speed approaching
        if actual_speed >= CRITICAL_SPEED and distance <= HIGH_DISTANCE and angle_from_center <= HIGH_ANGLE:
            is_collision = True
            if severity != 'critical':
                severity = 'critical'
        
        return is_collision, time_to_collision, severity
    
    def analyze_vehicle(self, bbox, vehicle_tracker_info, view):
        """
        Complete analysis of a vehicle: distance, angle, and collision prediction
        
        Args:
            bbox: (x, y, w, h) bounding box
            vehicle_tracker_info: Info from VehicleTracker
            view: 'front', 'back', 'left', 'right'
        
        Returns:
            Dictionary with all vehicle information
        """
        distance = self.calculate_distance(bbox, view)
        angle = self.calculate_angle(bbox, view)
        
        vehicle_info = {
            'position': vehicle_tracker_info['position'],
            'velocity': vehicle_tracker_info['velocity'],
            'speed': vehicle_tracker_info['speed'],
            'distance': distance,
            'angle': angle,
            'id': vehicle_tracker_info['id']
        }
        
        is_collision, time_to_collision, severity = self.predict_collision(vehicle_info, view)
        
        vehicle_info['collision_detected'] = is_collision
        vehicle_info['time_to_collision'] = time_to_collision
        vehicle_info['severity'] = severity
        
        return vehicle_info

