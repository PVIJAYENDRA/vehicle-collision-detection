"""
Alert system for collision warnings
"""

import cv2
import numpy as np
import pygame
from config import *


class AlertSystem:
    """Manages visual and audio alerts for collision warnings"""
    
    def __init__(self):
        self.alert_sound_enabled = ALERT_SOUND_ENABLED
        self.alert_active = False
        self.current_severity = 'none'
        
        # Initialize pygame for audio alerts
        if self.alert_sound_enabled:
            try:
                pygame.mixer.init()
                # Create a simple beep sound (can be replaced with actual sound file)
                self.beep_frequency = 440  # A4 note
                self.beep_duration = 200   # milliseconds
            except:
                self.alert_sound_enabled = False
    
    def check_alerts(self, vehicles_info):
        """
        Check all vehicles and determine if alert should be triggered
        
        Args:
            vehicles_info: List of vehicle info dictionaries
        
        Returns:
            (should_alert, severity, alert_message)
        """
        should_alert = False
        max_severity = 'none'
        alert_messages = []
        
        for vehicle in vehicles_info:
            if vehicle.get('collision_detected', False):
                should_alert = True
                severity = vehicle.get('severity', 'medium')
                
                # Determine max severity
                severity_levels = {'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                if severity_levels[severity] > severity_levels[max_severity]:
                    max_severity = severity
                
                # Create detailed alert message with distance, speed, and angle
                view = vehicle.get('view', 'unknown')
                distance = vehicle.get('distance', 0)
                speed = vehicle.get('speed', 0)
                angle = vehicle.get('angle', 0)
                ttc = vehicle.get('time_to_collision', float('inf'))
                vehicle_id = vehicle.get('id', '?')
                
                # Determine which factors triggered the alert
                factors = []
                if distance <= CRITICAL_DISTANCE:
                    factors.append(f"CLOSE (Dist: {distance:.1f}m)")
                elif distance <= HIGH_DISTANCE:
                    factors.append(f"Near (Dist: {distance:.1f}m)")
                
                if speed >= CRITICAL_SPEED:
                    factors.append(f"FAST (Speed: {speed:.1f}px/s)")
                elif speed >= HIGH_SPEED:
                    factors.append(f"Fast (Speed: {speed:.1f}px/s)")
                
                angle_from_center = abs(angle - 0) if view in ['front', 'back'] else abs(angle - 90)
                if angle_from_center > 180:
                    angle_from_center = 360 - angle_from_center
                
                if angle_from_center <= CRITICAL_ANGLE:
                    factors.append(f"DIRECT PATH (Angle: {angle:.1f}°)")
                elif angle_from_center <= HIGH_ANGLE:
                    factors.append(f"On Path (Angle: {angle:.1f}°)")
                
                factors_str = " | ".join(factors) if factors else "Risk detected"
                
                if ttc < float('inf'):
                    msg = f"Vehicle ID:{vehicle_id} [{severity.upper()}] - {factors_str} | TTC: {ttc:.1f}s"
                else:
                    msg = f"Vehicle ID:{vehicle_id} [{severity.upper()}] - {factors_str}"
                
                alert_messages.append(msg)
        
        self.alert_active = should_alert
        self.current_severity = max_severity
        
        return should_alert, max_severity, alert_messages
    
    def draw_alert_overlay(self, frame, vehicles_info):
        """
        Draw visual alerts on the frame
        
        Args:
            frame: OpenCV frame
            vehicles_info: List of vehicle info dictionaries
        
        Returns:
            Frame with alert overlays
        """
        h, w = frame.shape[:2]
        
        # Draw alert border if collision detected
        should_alert, severity, messages = self.check_alerts(vehicles_info)
        
        if should_alert:
            # Determine border color based on severity
            if severity == 'critical':
                color = (0, 0, 255)  # Red
                thickness = 10
            elif severity == 'high':
                color = (0, 100, 255)  # Orange-red
                thickness = 8
            elif severity == 'medium':
                color = (0, 165, 255)  # Orange
                thickness = 5
            else:
                color = (0, 255, 255)  # Yellow
                thickness = 3
            
            # Draw border
            cv2.rectangle(frame, (0, 0), (w-1, h-1), color, thickness)
            
            # Draw alert text
            y_offset = 30
            for i, msg in enumerate(messages[:3]):  # Show max 3 messages
                cv2.putText(frame, msg, (10, y_offset + i * 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw vehicle-specific alerts
        for vehicle in vehicles_info:
            if vehicle.get('collision_detected', False):
                self._draw_vehicle_alert(frame, vehicle)
        
        return frame
    
    def _draw_vehicle_alert(self, frame, vehicle):
        """Draw alert indicators for a specific vehicle"""
        x, y = vehicle['position']
        severity = vehicle.get('severity', 'medium')
        distance = vehicle.get('distance', 0)
        angle = vehicle.get('angle', 0)
        
        # Determine color
        if severity == 'critical':
            color = (0, 0, 255)
        elif severity == 'high':
            color = (0, 100, 255)
        elif severity == 'medium':
            color = (0, 165, 255)
        else:
            color = (0, 255, 255)
        
        # Draw warning circle around vehicle
        radius = 30
        cv2.circle(frame, (int(x), int(y)), radius, color, 3)
        
        # Draw warning lines
        for i in range(8):
            angle_rad = np.radians(i * 45)
            x1 = int(x + radius * np.cos(angle_rad))
            y1 = int(y + radius * np.sin(angle_rad))
            x2 = int(x + (radius + 10) * np.cos(angle_rad))
            y2 = int(y + (radius + 10) * np.sin(angle_rad))
            cv2.line(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw info text
        info_text = f"ID:{vehicle['id']} D:{distance:.1f}m A:{angle:.1f}°"
        cv2.putText(frame, info_text, (int(x - 50), int(y - radius - 10)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    def play_alert_sound(self):
        """Play alert sound if enabled"""
        if self.alert_sound_enabled and self.alert_active:
            try:
                # Generate a beep sound
                sample_rate = 22050
                duration_samples = int(sample_rate * self.beep_duration / 1000)
                t = np.linspace(0, self.beep_duration / 1000, duration_samples)
                wave = np.sin(2 * np.pi * self.beep_frequency * t)
                wave = (wave * 32767).astype(np.int16)
                
                sound = pygame.sndarray.make_sound(wave)
                sound.play()
            except:
                pass  # Silently fail if sound can't be played

