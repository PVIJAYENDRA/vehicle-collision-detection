"""
Main entry point for Vehicle Collision Detection System
Supports three modes: image, video file, and live feed
"""

import cv2
import numpy as np
import sys
import argparse
from ultralytics import YOLO
import time
from config import *
from vehicle_tracker import VehicleTracker
from collision_detector import CollisionDetector
from alert_system import AlertSystem
from input_handler import InputHandler, MultiInputHandler


class VehicleCollisionDetectionSystem:
    """Main system class for collision detection with flexible input support"""
    
    def __init__(self, input_source=None, input_type='auto', multi_view=False):
        """
        Initialize the collision detection system
        
        Args:
            input_source: Single input source (image/video/camera) or None for multi-view
            input_type: 'image', 'video', 'live', or 'auto'
            multi_view: If True, use multi-view mode from config
        """
        # Load YOLOv8 model
        print("Loading YOLOv8 model...")
        self.model = YOLO('yolov8n.pt')
        
        # Initialize input handler
        self.multi_view = multi_view
        if multi_view or (input_source is None and SINGLE_INPUT_MODE is None):
            # Multi-view mode
            self.input_handler = MultiInputHandler(CAMERA_SOURCES)
            self.views = self.input_handler.get_available_views()
            self.frame_sizes = self.input_handler.get_frame_sizes()
        else:
            # Single input mode
            source = input_source if input_source is not None else SINGLE_INPUT_MODE
            self.input_handler = InputHandler(source, input_type)
            self.views = ['main']
            # Get frame size
            if self.input_handler.is_image:
                h, w = self.input_handler.image.shape[:2]
                self.frame_sizes = {'main': (w, h)}
            else:
                w = int(self.input_handler.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(self.input_handler.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.frame_sizes = {'main': (w, h)}
        
        # Initialize trackers
        self.trackers = {}
        for view in self.views:
            self.trackers[view] = VehicleTracker()
        
        # Initialize collision detectors
        self.collision_detectors = {}
        for view in self.views:
            w, h = self.frame_sizes[view]
            self.collision_detectors[view] = CollisionDetector(w, h)
        
        # Initialize alert system
        self.alert_system = AlertSystem()
        
        print("System initialized successfully!")
        print(f"Mode: {'Multi-view' if self.multi_view else 'Single input'}")
        print(f"Input type: {self.input_handler.input_type if not self.multi_view else 'Multiple'}")
    
    def _detect_vehicles(self, frame, view='main'):
        """Detect vehicles in a frame using YOLOv8"""
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD, verbose=False)
            
            detections = []
            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # Check if it's a vehicle class
                        if cls in VEHICLE_CLASSES:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                            
                            # Ensure valid bounding box
                            if w > 0 and h > 0 and x >= 0 and y >= 0:
                                detections.append((x, y, w, h))
            
            return detections
        except Exception as e:
            print(f"Error in vehicle detection: {e}")
            return []
    
    def _process_view(self, frame, view='main'):
        """Process a single frame"""
        if frame is None:
            return None, []
        
        # Detect vehicles
        detections = self._detect_vehicles(frame, view)
        
        # Update tracker
        w, h = self.frame_sizes[view]
        self.trackers[view].update(detections, (w/2, h/2))
        
        # Get tracked vehicles
        tracked_vehicles = self.trackers[view].get_tracked_vehicles()
        
        # Analyze each tracked vehicle
        vehicles_info = []
        for vehicle_tracker_info in tracked_vehicles:
            bbox = vehicle_tracker_info.get('bbox', None)
            if bbox is None:
                x, y = vehicle_tracker_info['position']
                bbox = (int(x - 50), int(y - 50), 100, 100)
            
            vehicle_info = self.collision_detectors[view].analyze_vehicle(
                bbox, vehicle_tracker_info, view
            )
            vehicle_info['view'] = view
            vehicles_info.append(vehicle_info)
        
        # Draw detections and information
        frame = self._draw_detections(frame, detections, tracked_vehicles, vehicles_info, view)
        
        return frame, vehicles_info
    
    def _draw_text_with_background(self, frame, text, position, font_scale=0.6, thickness=2, 
                                   text_color=(255, 255, 255), bg_color=(0, 0, 0), alpha=0.7):
        """Draw text with semi-transparent background for better visibility"""
        x, y = position
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Calculate background rectangle
        padding = 5
        bg_x1 = x - padding
        bg_y1 = y - text_height - padding
        bg_x2 = x + text_width + padding
        bg_y2 = y + baseline + padding
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_color, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Draw text with outline for better visibility
        # Draw black outline
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            cv2.putText(frame, text, (x + dx, y + dy), font, font_scale, (0, 0, 0), thickness + 1)
        # Draw main text
        cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness)
        
        return frame
    
    def _draw_detections(self, frame, detections, tracked_vehicles, vehicles_info, view):
        """Draw detections, tracks, and information on frame"""
        h, w = frame.shape[:2]
        
        # Draw detections (make them more visible)
        if SHOW_DETECTIONS:
            for bbox in detections:
                x, y, w_box, h_box = bbox
                # Ensure valid coordinates
                if x >= 0 and y >= 0 and w_box > 0 and h_box > 0:
                    # Draw thicker, more visible boxes
                    cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 3)
                    # Add label with background
                    self._draw_text_with_background(
                        frame, "Vehicle", (x + 5, y + 25),
                        font_scale=0.7, thickness=2,
                        text_color=(0, 255, 0), bg_color=(0, 0, 0)
                    )
        
        # Draw tracks and vehicle information
        if SHOW_TRACKS:
            for vehicle_info in vehicles_info:
                x, y = vehicle_info['position']
                vehicle_id = vehicle_info['id']
                speed = vehicle_info['speed']
                distance = vehicle_info['distance']
                angle = vehicle_info['angle']
                collision = vehicle_info['collision_detected']
                severity = vehicle_info['severity']
                
                # Draw trajectory
                trajectory = vehicle_info.get('trajectory', [])
                if len(trajectory) > 1:
                    points = np.array(trajectory[-10:], dtype=np.int32)
                    cv2.polylines(frame, [points], False, (255, 0, 0), 2)
                
                # Draw vehicle center
                color = (0, 255, 0) if not collision else (0, 0, 255)
                cv2.circle(frame, (int(x), int(y)), 5, color, -1)
                
                # Draw information with background
                if SHOW_INFO:
                    info_text = f"ID:{vehicle_id} Speed:{speed:.1f}px/s"
                    info_text2 = f"Dist:{distance:.1f}m Angle:{angle:.1f}°"
                    
                    # Position text inside bounding box (top-left corner)
                    text_x = int(x + 5)
                    text_y = int(y + 25)
                    
                    # Draw first line of info
                    self._draw_text_with_background(
                        frame, info_text, (text_x, text_y),
                        font_scale=0.6, thickness=2,
                        text_color=(255, 255, 255), bg_color=(0, 0, 0)
                    )
                    
                    # Draw second line of info
                    self._draw_text_with_background(
                        frame, info_text2, (text_x, text_y + 25),
                        font_scale=0.6, thickness=2,
                        text_color=(255, 255, 255), bg_color=(0, 0, 0)
                    )
                    
                    if collision:
                        severity_text = f"⚠ ALERT: {severity.upper()}"
                        alert_color = (0, 0, 255) if severity in ['critical', 'high'] else (0, 165, 255)
                        self._draw_text_with_background(
                            frame, severity_text, (text_x, text_y + 50),
                            font_scale=0.7, thickness=2,
                            text_color=(255, 255, 255), bg_color=alert_color
                        )
        
        # Draw view label
        view_label = f"{view.upper()} VIEW"
        if not self.multi_view:
            props = self.input_handler.get_properties()
            if props['is_image']:
                view_label += " - IMAGE"
            elif props['is_video']:
                view_label += f" - VIDEO (Frame {self.input_handler.get_frame_number()}/{self.input_handler.get_total_frames()})"
            elif props['is_live']:
                view_label += " - LIVE"
        
        cv2.putText(frame, view_label, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return frame
    
    def run(self):
        """Main processing loop"""
        print("Starting collision detection system...")
        print("Press 'q' to quit, 'p' to pause (video only), 'r' to reset (video/image only)")
        
        last_alert_time = 0
        alert_interval = 0.5
        paused = False
        
        while True:
            if not paused:
                # Read frames
                if self.multi_view:
                    frames_data = self.input_handler.read_all()
                    all_vehicles_info = []
                    processed_frames = {}
                    
                    for view, (ret, frame) in frames_data.items():
                        if ret and frame is not None:
                            processed_frame, vehicles_info = self._process_view(frame, view)
                            if processed_frame is not None:
                                processed_frames[view] = processed_frame
                                all_vehicles_info.extend(vehicles_info)
                    
                    # Check for alerts
                    should_alert, severity, messages = self.alert_system.check_alerts(all_vehicles_info)
                    
                    # Draw alert overlays
                    for view, frame in processed_frames.items():
                        frame = self.alert_system.draw_alert_overlay(frame,
                            [v for v in all_vehicles_info if v.get('view') == view])
                        processed_frames[view] = frame
                    
                    # Play alert sound
                    current_time = time.time()
                    if should_alert and (current_time - last_alert_time) > alert_interval:
                        self.alert_system.play_alert_sound()
                        last_alert_time = current_time
                    
                    # Display frames
                    if processed_frames:
                        self._display_multi_view(processed_frames, all_vehicles_info)
                    
                    # Check if all inputs are finished
                    if all(not ret for ret, _ in frames_data.values()):
                        print("All inputs finished.")
                        break
                
                else:
                    # Single input mode
                    ret, frame = self.input_handler.read()
                    
                    if not ret or frame is None:
                        if self.input_handler.is_finished():
                            print("Input finished.")
                            break
                        continue
                    
                    # Process frame
                    processed_frame, vehicles_info = self._process_view(frame, 'main')
                    
                    if processed_frame is not None:
                        # Check for alerts
                        should_alert, severity, messages = self.alert_system.check_alerts(vehicles_info)
                        
                        # Draw alert overlay
                        processed_frame = self.alert_system.draw_alert_overlay(processed_frame, vehicles_info)
                        
                        # Play alert sound
                        current_time = time.time()
                        if should_alert and (current_time - last_alert_time) > alert_interval:
                            self.alert_system.play_alert_sound()
                            last_alert_time = current_time
                        
                        # Display frame
                        cv2.imshow('Vehicle Collision Detection', processed_frame)
                        
                        # Add summary
                        collision_count = sum(1 for v in vehicles_info if v.get('collision_detected', False))
                        print(f"\rFrame {self.input_handler.get_frame_number()}: "
                              f"Vehicles: {len(vehicles_info)}, Collision Risks: {collision_count}", end='')
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p') and not self.input_handler.is_live:
                paused = not paused
                print(f"\n{'Paused' if paused else 'Resumed'}")
            elif key == ord('r') and not self.input_handler.is_live:
                self.input_handler.reset()
                print("\nReset to beginning")
        
        self.cleanup()
    
    def _display_multi_view(self, frames, all_vehicles_info):
        """Display multiple views in a grid"""
        views = ['front', 'back', 'left', 'right']
        
        grid_rows = []
        for i in range(2):
            row_frames = []
            for j in range(2):
                view_idx = i * 2 + j
                if view_idx < len(views):
                    view = views[view_idx]
                    if view in frames:
                        frame = frames[view].copy()
                        frame = cv2.resize(frame, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
                        row_frames.append(frame)
                    else:
                        black_frame = np.zeros((DISPLAY_HEIGHT // 2, DISPLAY_WIDTH // 2, 3), dtype=np.uint8)
                        cv2.putText(black_frame, f"{views[view_idx].upper()} UNAVAILABLE",
                                   (10, DISPLAY_HEIGHT // 4),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        row_frames.append(black_frame)
                else:
                    row_frames.append(np.zeros((DISPLAY_HEIGHT // 2, DISPLAY_WIDTH // 2, 3), dtype=np.uint8))
            
            if row_frames:
                row = np.hstack(row_frames)
                grid_rows.append(row)
        
        if grid_rows:
            grid = np.vstack(grid_rows)
            collision_count = sum(1 for v in all_vehicles_info if v.get('collision_detected', False))
            info_text = f"Vehicles: {len(all_vehicles_info)} | Collision Risks: {collision_count}"
            cv2.putText(grid, info_text, (10, grid.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow('Vehicle Collision Detection System', grid)
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        if hasattr(self, 'input_handler'):
            if self.multi_view:
                self.input_handler.release_all()
            else:
                self.input_handler.release()
        cv2.destroyAllWindows()
        print("System stopped.")


def main():
    """Main entry point with command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Vehicle Collision Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single image
  python run_detection.py --input image.jpg --type image
  
  # Process a video file
  python run_detection.py --input video.mp4 --type video
  
  # Use live camera feed
  python run_detection.py --input 0 --type live
  
  # Multi-view mode (uses config.py settings)
  python run_detection.py --multi-view
        """
    )
    
    parser.add_argument('--input', '-i', type=str, default=None,
                       help='Input source: image file, video file, or camera index (default: from config)')
    parser.add_argument('--type', '-t', type=str, choices=['image', 'video', 'live', 'auto'],
                       default='auto', help='Input type (default: auto-detect)')
    parser.add_argument('--multi-view', '-m', action='store_true',
                       help='Use multi-view mode from config.py')
    
    args = parser.parse_args()
    
    # Convert input to appropriate type
    input_source = args.input
    if input_source is not None:
        # Try to convert to int if it looks like a number
        try:
            input_source = int(input_source)
            if args.type == 'auto':
                args.type = 'live'
        except ValueError:
            pass  # Keep as string
    
    try:
        system = VehicleCollisionDetectionSystem(
            input_source=input_source,
            input_type=args.type,
            multi_view=args.multi_view
        )
        system.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

