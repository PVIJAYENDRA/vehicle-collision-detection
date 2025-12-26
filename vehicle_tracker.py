"""
Vehicle tracking module using Kalman filter for speed estimation
"""

import numpy as np
from filterpy.kalman import KalmanFilter
from collections import defaultdict
import time


class VehicleTracker:
    """Tracks vehicles and estimates their speed, position, and trajectory"""
    
    def __init__(self, max_disappeared=30):
        self.next_id = 0
        self.trackers = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared
        self.speeds = defaultdict(list)
        self.positions_history = defaultdict(list)
        self.timestamps = defaultdict(list)
        self.bboxes = {}  # Store last known bbox for each tracked vehicle
        
    def _create_kalman_filter(self):
        """Create a Kalman filter for vehicle tracking"""
        kf = KalmanFilter(dim_x=4, dim_z=2)
        
        # State: [x, y, vx, vy] (position and velocity)
        kf.F = np.array([[1, 0, 1, 0],    # State transition
                         [0, 1, 0, 1],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype=np.float32)
        
        kf.H = np.array([[1, 0, 0, 0],    # Measurement function
                         [0, 1, 0, 0]], dtype=np.float32)
        
        kf.P *= 1000.  # Covariance matrix
        kf.R = np.array([[5, 0],          # Measurement noise
                         [0, 5]], dtype=np.float32)
        kf.Q = np.array([[1, 0, 0, 0],    # Process noise
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype=np.float32) * 0.03
        
        return kf
    
    def update(self, detections, frame_center):
        """
        Update trackers with new detections
        
        Args:
            detections: List of (x, y, w, h) bounding boxes
            frame_center: (cx, cy) center of the frame
        """
        current_time = time.time()
        
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._remove_tracker(object_id)
            return
        
        # Match detections to existing trackers
        if len(self.trackers) == 0:
            # Create new trackers for all detections
            for detection in detections:
                self._create_tracker(detection, frame_center, current_time)
        else:
            # Match detections to existing trackers
            matched, unmatched_dets, unmatched_trks = self._associate_detections_to_trackers(
                detections, frame_center, current_time
            )
            
            # Update matched trackers
            for det_idx, trk_idx in matched:
                self._update_tracker(trk_idx, detections[det_idx], frame_center, current_time)
            
            # Create new trackers for unmatched detections
            for det_idx in unmatched_dets:
                self._create_tracker(detections[det_idx], frame_center, current_time)
            
            # Mark unmatched trackers as disappeared
            for trk_idx in unmatched_trks:
                object_id = list(self.trackers.keys())[trk_idx]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._remove_tracker(object_id)
    
    def _create_tracker(self, detection, frame_center, current_time):
        """Create a new tracker for a detection"""
        x, y, w, h = detection
        cx = x + w / 2
        cy = y + h / 2
        
        kf = self._create_kalman_filter()
        kf.x = np.array([cx, cy, 0, 0], dtype=np.float32)
        
        object_id = self.next_id
        self.next_id += 1
        
        self.trackers[object_id] = kf
        self.disappeared[object_id] = 0
        self.positions_history[object_id] = [(cx, cy)]
        self.timestamps[object_id] = [current_time]
        self.speeds[object_id] = [0.0]
        self.bboxes[object_id] = detection
    
    def _update_tracker(self, trk_idx, detection, frame_center, current_time):
        """Update an existing tracker"""
        object_id = list(self.trackers.keys())[trk_idx]
        kf = self.trackers[object_id]
        
        x, y, w, h = detection
        cx = x + w / 2
        cy = y + h / 2
        
        # Update Kalman filter
        kf.predict()
        kf.update(np.array([cx, cy], dtype=np.float32))
        
        # Calculate speed
        if len(self.positions_history[object_id]) > 0:
            prev_x, prev_y = self.positions_history[object_id][-1]
            prev_time = self.timestamps[object_id][-1]
            
            dt = current_time - prev_time
            if dt > 0:
                dx = cx - prev_x
                dy = cy - prev_y
                speed = np.sqrt(dx**2 + dy**2) / dt
                self.speeds[object_id].append(speed)
                
                # Keep only recent speeds
                if len(self.speeds[object_id]) > 10:
                    self.speeds[object_id].pop(0)
        
        # Update history
        self.positions_history[object_id].append((cx, cy))
        self.timestamps[object_id].append(current_time)
        self.disappeared[object_id] = 0
        self.bboxes[object_id] = detection
        
        # Keep only recent history
        if len(self.positions_history[object_id]) > 30:
            self.positions_history[object_id].pop(0)
            self.timestamps[object_id].pop(0)
    
    def _associate_detections_to_trackers(self, detections, frame_center, current_time):
        """Match detections to trackers using Hungarian algorithm (simplified)"""
        if len(self.trackers) == 0:
            return [], list(range(len(detections))), []
        
        # Calculate cost matrix (distance between detection and predicted position)
        cost_matrix = []
        for detection in detections:
            x, y, w, h = detection
            det_cx = x + w / 2
            det_cy = y + h / 2
            
            row = []
            for object_id, kf in self.trackers.items():
                kf.predict()
                pred_x, pred_y = kf.x[0], kf.x[1]
                distance = np.sqrt((det_cx - pred_x)**2 + (det_cy - pred_y)**2)
                row.append(distance)
            cost_matrix.append(row)
        
        # Simple greedy matching (can be improved with Hungarian algorithm)
        matched = []
        unmatched_dets = list(range(len(detections)))
        unmatched_trks = list(range(len(self.trackers)))
        
        if len(cost_matrix) > 0 and len(cost_matrix[0]) > 0:
            # Find minimum cost matches
            max_distance = 100  # Maximum distance for matching
            
            while True:
                min_cost = float('inf')
                min_det = -1
                min_trk = -1
                
                for det_idx in unmatched_dets:
                    for trk_idx in unmatched_trks:
                        if cost_matrix[det_idx][trk_idx] < min_cost:
                            min_cost = cost_matrix[det_idx][trk_idx]
                            min_det = det_idx
                            min_trk = trk_idx
                
                if min_cost < max_distance and min_det != -1:
                    matched.append((min_det, min_trk))
                    unmatched_dets.remove(min_det)
                    unmatched_trks.remove(min_trk)
                else:
                    break
        
        return matched, unmatched_dets, unmatched_trks
    
    def _remove_tracker(self, object_id):
        """Remove a tracker"""
        if object_id in self.trackers:
            del self.trackers[object_id]
        if object_id in self.disappeared:
            del self.disappeared[object_id]
        if object_id in self.speeds:
            del self.speeds[object_id]
        if object_id in self.positions_history:
            del self.positions_history[object_id]
        if object_id in self.timestamps:
            del self.timestamps[object_id]
        if object_id in self.bboxes:
            del self.bboxes[object_id]
    
    def get_tracked_vehicles(self):
        """Get current tracked vehicles with their properties"""
        vehicles = []
        
        for object_id, kf in self.trackers.items():
            if object_id in self.disappeared and self.disappeared[object_id] > 0:
                continue
            
            x, y = kf.x[0], kf.x[1]
            vx, vy = kf.x[2], kf.x[3]
            
            # Get average speed
            avg_speed = np.mean(self.speeds[object_id]) if self.speeds[object_id] else 0.0
            
            # Get trajectory
            trajectory = self.positions_history[object_id] if object_id in self.positions_history else []
            
            # Get bbox (use stored bbox or estimate from position)
            if object_id in self.bboxes:
                bbox = self.bboxes[object_id]
            else:
                # Estimate bbox from position (default size)
                bbox = (int(x - 50), int(y - 50), 100, 100)
            
            vehicles.append({
                'id': object_id,
                'position': (x, y),
                'velocity': (vx, vy),
                'speed': avg_speed,
                'trajectory': trajectory,
                'bbox': bbox
            })
        
        return vehicles

