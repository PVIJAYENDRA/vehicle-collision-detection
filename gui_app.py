"""
GUI Application for Vehicle Collision Detection System
Supports Image, Video, and Live Feed inputs
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
from ultralytics import YOLO
from config import *
from config import (CRITICAL_DISTANCE, HIGH_DISTANCE, MEDIUM_DISTANCE, LOW_DISTANCE,
                    CRITICAL_SPEED, HIGH_SPEED, MEDIUM_SPEED, LOW_SPEED,
                    CRITICAL_ANGLE, HIGH_ANGLE, MEDIUM_ANGLE, LOW_ANGLE)
from vehicle_tracker import VehicleTracker
from collision_detector import CollisionDetector
from alert_system import AlertSystem
from input_handler import InputHandler


class CollisionDetectionGUI:
    """Main GUI application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Collision Detection System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # State variables
        self.is_processing = False
        self.is_paused = False
        self.current_input_type = None
        self.current_input_source = None
        self.input_handler = None
        
        # Detection components
        self.model = None
        self.tracker = None
        self.collision_detector = None
        self.alert_system = None
        
        # Video playback
        self.video_thread = None
        self.current_frame = None
        
        # Setup UI
        self.setup_ui()
        
        # Load model in background
        self.load_model_async()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#2b2b2b')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg='#3c3c3c', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel - Display and Info
        right_panel = tk.Frame(main_container, bg='#2b2b2b')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_control_panel(left_panel)
        self.setup_display_panel(right_panel)
        self.setup_info_panel(right_panel)
    
    def setup_control_panel(self, parent):
        """Setup the control panel"""
        # Title
        title_label = tk.Label(
            parent, 
            text="Vehicle Collision Detection",
            font=('Arial', 16, 'bold'),
            bg='#3c3c3c',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Input Type Selection
        input_frame = tk.LabelFrame(
            parent,
            text="Input Type",
            font=('Arial', 12, 'bold'),
            bg='#3c3c3c',
            fg='white',
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_type_var = tk.StringVar(value="image")
        
        tk.Radiobutton(
            input_frame,
            text="Image File",
            variable=self.input_type_var,
            value="image",
            font=('Arial', 10),
            bg='#3c3c3c',
            fg='white',
            selectcolor='#2b2b2b',
            activebackground='#3c3c3c',
            activeforeground='white',
            command=self.on_input_type_change
        ).pack(anchor=tk.W, pady=5)
        
        tk.Radiobutton(
            input_frame,
            text="Video File",
            variable=self.input_type_var,
            value="video",
            font=('Arial', 10),
            bg='#3c3c3c',
            fg='white',
            selectcolor='#2b2b2b',
            activebackground='#3c3c3c',
            activeforeground='white',
            command=self.on_input_type_change
        ).pack(anchor=tk.W, pady=5)
        
        tk.Radiobutton(
            input_frame,
            text="Live Feed",
            variable=self.input_type_var,
            value="live",
            font=('Arial', 10),
            bg='#3c3c3c',
            fg='white',
            selectcolor='#2b2b2b',
            activebackground='#3c3c3c',
            activeforeground='white',
            command=self.on_input_type_change
        ).pack(anchor=tk.W, pady=5)
        
        # Input Source Selection
        source_frame = tk.LabelFrame(
            parent,
            text="Input Source",
            font=('Arial', 12, 'bold'),
            bg='#3c3c3c',
            fg='white',
            padx=10,
            pady=10
        )
        source_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.source_label = tk.Label(
            source_frame,
            text="No source selected",
            font=('Arial', 9),
            bg='#3c3c3c',
            fg='#aaaaaa',
            wraplength=250
        )
        self.source_label.pack(pady=5)
        
        self.browse_button = tk.Button(
            source_frame,
            text="Browse / Select",
            command=self.select_source,
            font=('Arial', 10),
            bg='#4a9eff',
            fg='white',
            activebackground='#357abd',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        self.browse_button.pack(pady=5)
        
        # Camera selection for live feed
        self.camera_frame = tk.Frame(source_frame, bg='#3c3c3c')
        self.camera_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            self.camera_frame,
            text="Camera Index:",
            font=('Arial', 9),
            bg='#3c3c3c',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.camera_var = tk.StringVar(value="0")
        camera_spinbox = tk.Spinbox(
            self.camera_frame,
            from_=0,
            to=10,
            textvariable=self.camera_var,
            width=5,
            font=('Arial', 9),
            bg='#4a4a4a',
            fg='white',
            buttonbackground='#4a9eff'
        )
        camera_spinbox.pack(side=tk.LEFT, padx=5)
        self.camera_frame.pack_forget()  # Hide initially
        
        # Control Buttons
        control_frame = tk.LabelFrame(
            parent,
            text="Controls",
            font=('Arial', 12, 'bold'),
            bg='#3c3c3c',
            fg='white',
            padx=10,
            pady=10
        )
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = tk.Button(
            control_frame,
            text="Start Detection",
            command=self.start_detection,
            font=('Arial', 11, 'bold'),
            bg='#28a745',
            fg='white',
            activebackground='#218838',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.start_button.pack(fill=tk.X, pady=5)
        
        self.stop_button = tk.Button(
            control_frame,
            text="Stop Detection",
            command=self.stop_detection,
            font=('Arial', 11, 'bold'),
            bg='#dc3545',
            fg='white',
            activebackground='#c82333',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, pady=5)
        
        self.pause_button = tk.Button(
            control_frame,
            text="Pause",
            command=self.toggle_pause,
            font=('Arial', 10),
            bg='#ffc107',
            fg='black',
            activebackground='#e0a800',
            activeforeground='black',
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.pause_button.pack(fill=tk.X, pady=5)
        
        # Status
        status_frame = tk.LabelFrame(
            parent,
            text="Status",
            font=('Arial', 12, 'bold'),
            bg='#3c3c3c',
            fg='white',
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=('Arial', 10),
            bg='#3c3c3c',
            fg='#28a745',
            wraplength=250
        )
        self.status_label.pack(pady=5)
        
        # Model loading indicator
        self.model_status_label = tk.Label(
            status_frame,
            text="Loading model...",
            font=('Arial', 9),
            bg='#3c3c3c',
            fg='#ffc107',
            wraplength=250
        )
        self.model_status_label.pack(pady=5)
    
    def setup_display_panel(self, parent):
        """Setup the display panel"""
        display_frame = tk.LabelFrame(
            parent,
            text="Video Display",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            padx=10,
            pady=10
        )
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas for video display
        self.canvas = tk.Canvas(
            display_frame,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder text
        self.canvas.create_text(
            400, 300,
            text="Select input source and click 'Start Detection'",
            fill='#888888',
            font=('Arial', 14)
        )
    
    def setup_info_panel(self, parent):
        """Setup the information panel"""
        info_frame = tk.LabelFrame(
            parent,
            text="Vehicle Information",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white',
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create scrollable text widget
        text_frame = tk.Frame(info_frame, bg='#2b2b2b')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.info_text = tk.Text(
            text_frame,
            height=8,
            font=('Courier', 9),
            bg='#1a1a1a',
            fg='#00ff00',
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.info_text.yview)
        
        # Alert indicator
        self.alert_label = tk.Label(
            info_frame,
            text="",
            font=('Arial', 12, 'bold'),
            bg='#2b2b2b',
            fg='white'
        )
        self.alert_label.pack(pady=5)
    
    def load_model_async(self):
        """Load YOLOv8 model in background thread"""
        def load_model():
            try:
                self.model_status_label.config(text="Loading YOLOv8 model...", fg='#ffc107')
                self.model = YOLO('yolov8n.pt')
                self.model_status_label.config(text="Model loaded successfully", fg='#28a745')
            except Exception as e:
                self.model_status_label.config(text=f"Error loading model: {str(e)}", fg='#dc3545')
        
        thread = threading.Thread(target=load_model, daemon=True)
        thread.start()
    
    def on_input_type_change(self):
        """Handle input type change"""
        input_type = self.input_type_var.get()
        
        if input_type == "live":
            self.camera_frame.pack(fill=tk.X, pady=5)
            self.browse_button.config(text="Use Camera")
        else:
            self.camera_frame.pack_forget()
            self.browse_button.config(text="Browse File")
        
        # Reset source
        self.current_input_source = None
        self.source_label.config(text="No source selected")
    
    def select_source(self):
        """Select input source based on type"""
        input_type = self.input_type_var.get()
        
        if input_type == "live":
            # Use camera index
            camera_index = int(self.camera_var.get())
            self.current_input_source = camera_index
            self.source_label.config(text=f"Camera {camera_index}", fg='white')
        elif input_type == "image":
            # Browse image file
            file_path = filedialog.askopenfilename(
                title="Select Image File",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                self.current_input_source = file_path
                self.source_label.config(text=f"Image: {file_path.split('/')[-1]}", fg='white')
        elif input_type == "video":
            # Browse video file
            file_path = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[
                    ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                self.current_input_source = file_path
                self.source_label.config(text=f"Video: {file_path.split('/')[-1]}", fg='white')
    
    def start_detection(self):
        """Start the detection process"""
        if self.model is None:
            messagebox.showerror("Error", "Model is still loading. Please wait...")
            return
        
        if self.current_input_source is None:
            messagebox.showerror("Error", "Please select an input source first!")
            return
        
        try:
            # Initialize input handler
            input_type = self.input_type_var.get()
            self.input_handler = InputHandler(self.current_input_source, input_type)
            
            # Get frame size
            if self.input_handler.is_image:
                h, w = self.input_handler.image.shape[:2]
                frame_size = (w, h)
            else:
                w = int(self.input_handler.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(self.input_handler.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                frame_size = (w, h)
            
            # Initialize detection components
            self.tracker = VehicleTracker()
            self.collision_detector = CollisionDetector(frame_size[0], frame_size[1])
            self.alert_system = AlertSystem()
            
            # Update UI state
            self.is_processing = True
            self.is_paused = False
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL if not self.input_handler.is_image else tk.DISABLED)
            self.status_label.config(text="Processing...", fg='#28a745')
            
            # Start processing
            if self.input_handler.is_image:
                self.process_image()
            else:
                self.start_video_processing()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start detection: {str(e)}")
            self.stop_detection()
    
    def process_image(self):
        """Process a single image"""
        ret, frame = self.input_handler.read()
        if ret and frame is not None:
            processed_frame, vehicles_info = self.process_frame(frame)
            self.display_frame(processed_frame)
            self.update_info(vehicles_info)
            vehicle_count = len(vehicles_info)
            self.status_label.config(
                text=f"Image processed - Vehicles detected: {vehicle_count}", 
                fg='#28a745' if vehicle_count > 0 else '#ffc107'
            )
    
    def start_video_processing(self):
        """Start video processing in a separate thread"""
        if self.video_thread is not None and self.video_thread.is_alive():
            return
        
        self.video_thread = threading.Thread(target=self.video_processing_loop, daemon=True)
        self.video_thread.start()
    
    def video_processing_loop(self):
        """Main video processing loop"""
        last_alert_time = 0
        alert_interval = 0.5
        
        while self.is_processing:
            if not self.is_paused:
                ret, frame = self.input_handler.read()
                
                if not ret or frame is None:
                    if self.input_handler.is_finished():
                        self.root.after(0, lambda: self.status_label.config(
                            text="Video finished", fg='#ffc107'))
                        break
                    continue
                
                # Process frame
                processed_frame, vehicles_info = self.process_frame(frame)
                
                # Check alerts
                should_alert, severity, messages = self.alert_system.check_alerts(vehicles_info)
                
                # Update UI in main thread
                self.root.after(0, lambda f=processed_frame: self.display_frame(f))
                self.root.after(0, lambda v=vehicles_info: self.update_info(v))
                
                # Play alert sound
                current_time = time.time()
                if should_alert and (current_time - last_alert_time) > alert_interval:
                    self.alert_system.play_alert_sound()
                    last_alert_time = current_time
                    self.root.after(0, lambda s=severity: self.update_alert_indicator(s, messages))
                
            # Update status with detection count
            vehicle_count = len(vehicles_info)
            if self.input_handler.is_video:
                frame_num = self.input_handler.get_frame_number()
                total_frames = self.input_handler.get_total_frames()
                status_text = f"Frame {frame_num}/{total_frames} - Vehicles: {vehicle_count}"
                self.root.after(0, lambda: self.status_label.config(
                    text=status_text, fg='#28a745'))
            else:
                status_text = f"Live feed - Vehicles detected: {vehicle_count}"
                self.root.after(0, lambda: self.status_label.config(
                    text=status_text, fg='#28a745'))
            
            time.sleep(0.03)  # ~30 FPS
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Detect vehicles
        detections = self.detect_vehicles(frame)
        
        # Update tracker
        h, w = frame.shape[:2]
        self.tracker.update(detections, (w/2, h/2))
        
        # Get tracked vehicles
        tracked_vehicles = self.tracker.get_tracked_vehicles()
        
        # Analyze vehicles
        vehicles_info = []
        for vehicle_tracker_info in tracked_vehicles:
            bbox = vehicle_tracker_info.get('bbox', None)
            if bbox is None:
                x, y = vehicle_tracker_info['position']
                bbox = (int(x - 50), int(y - 50), 100, 100)
            
            vehicle_info = self.collision_detector.analyze_vehicle(
                bbox, vehicle_tracker_info, 'main'
            )
            vehicles_info.append(vehicle_info)
        
        # Draw on frame
        frame = self.draw_detections(frame, detections, vehicles_info)
        frame = self.alert_system.draw_alert_overlay(frame, vehicles_info)
        
        return frame, vehicles_info
    
    def detect_vehicles(self, frame):
        """Detect vehicles in frame"""
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD, verbose=False)
            
            detections = []
            all_detections_count = 0
            
            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes
                    all_detections_count += len(boxes)
                    
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
            
            # Debug: Print detection info (can be removed later)
            if len(detections) > 0:
                print(f"Detected {len(detections)} vehicles (out of {all_detections_count} total detections)")
            
            return detections
        except Exception as e:
            print(f"Error in vehicle detection: {e}")
            return []
    
    def draw_text_with_background(self, frame, text, position, font_scale=0.6, thickness=2, 
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
    
    def draw_detections(self, frame, detections, vehicles_info):
        """Draw detections and information on frame"""
        # Draw detection boxes (green for all detections)
        for bbox in detections:
            x, y, w, h = bbox
            # Ensure coordinates are valid
            if x >= 0 and y >= 0 and w > 0 and h > 0:
                # Draw thicker, more visible boxes
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                # Add label with background
                self.draw_text_with_background(
                    frame, "Vehicle", (x + 5, y + 25),
                    font_scale=0.7, thickness=2,
                    text_color=(0, 255, 0), bg_color=(0, 0, 0)
                )
        
        # Draw vehicle information
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
            
            # Draw information with background - position inside or near bounding box
            info_text = f"ID:{vehicle_id} Speed:{speed:.1f}px/s"
            info_text2 = f"Dist:{distance:.1f}m Angle:{angle:.1f}°"
            
            # Position text inside bounding box (top-left corner)
            text_x = int(x + 5)
            text_y = int(y + 25)
            
            # Draw first line of info
            self.draw_text_with_background(
                frame, info_text, (text_x, text_y),
                font_scale=0.6, thickness=2,
                text_color=(255, 255, 255), bg_color=(0, 0, 0)
            )
            
            # Draw second line of info
            self.draw_text_with_background(
                frame, info_text2, (text_x, text_y + 25),
                font_scale=0.6, thickness=2,
                text_color=(255, 255, 255), bg_color=(0, 0, 0)
            )
            
            if collision:
                # Create detailed alert message showing which factors triggered it
                factors = []
                if distance <= CRITICAL_DISTANCE:
                    factors.append("CLOSE")
                elif distance <= HIGH_DISTANCE:
                    factors.append("Near")
                
                if speed >= CRITICAL_SPEED:
                    factors.append("FAST")
                elif speed >= HIGH_SPEED:
                    factors.append("Fast")
                
                # Calculate angle from center
                angle_from_center = abs(angle - 0)  # Simplified for main view
                if angle_from_center > 180:
                    angle_from_center = 360 - angle_from_center
                
                if angle_from_center <= CRITICAL_ANGLE:
                    factors.append("DIRECT")
                elif angle_from_center <= HIGH_ANGLE:
                    factors.append("OnPath")
                
                factors_str = " | ".join(factors) if factors else "Alert"
                severity_text = f"⚠ {severity.upper()}: {factors_str}"
                
                alert_color = (0, 0, 255) if severity in ['critical', 'high'] else (0, 165, 255)
                self.draw_text_with_background(
                    frame, severity_text, (text_x, text_y + 50),
                    font_scale=0.7, thickness=2,
                    text_color=(255, 255, 255), bg_color=alert_color
                )
        
        return frame
    
    def display_frame(self, frame):
        """Display frame on canvas"""
        if frame is None:
            return
        
        # Resize frame to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate scaling
            frame_height, frame_width = frame.shape[:2]
            scale = min(canvas_width / frame_width, canvas_height / frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            # Resize frame
            frame_resized = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB and then to PhotoImage
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=photo,
                anchor=tk.CENTER
            )
            self.canvas.image = photo  # Keep a reference
    
    def update_info(self, vehicles_info):
        """Update information panel"""
        self.info_text.delete(1.0, tk.END)
        
        if not vehicles_info:
            self.info_text.insert(tk.END, "No vehicles detected\n")
            return
        
        # Summary
        collision_count = sum(1 for v in vehicles_info if v.get('collision_detected', False))
        self.info_text.insert(tk.END, f"=== Summary ===\n")
        self.info_text.insert(tk.END, f"Total Vehicles: {len(vehicles_info)}\n")
        self.info_text.insert(tk.END, f"Collision Risks: {collision_count}\n\n")
        
        # Vehicle details
        self.info_text.insert(tk.END, f"=== Vehicle Details ===\n")
        for vehicle in vehicles_info:
            vehicle_id = vehicle['id']
            speed = vehicle['speed']
            distance = vehicle['distance']
            angle = vehicle['angle']
            collision = vehicle['collision_detected']
            severity = vehicle.get('severity', 'none')
            ttc = vehicle.get('time_to_collision', float('inf'))
            
            self.info_text.insert(tk.END, f"\nVehicle ID: {vehicle_id}\n")
            self.info_text.insert(tk.END, f"  Speed: {speed:.2f} px/s\n")
            self.info_text.insert(tk.END, f"  Distance: {distance:.2f} m\n")
            self.info_text.insert(tk.END, f"  Angle: {angle:.1f}°\n")
            
            if collision:
                self.info_text.insert(tk.END, f"  ⚠️ COLLISION RISK: {severity.upper()}\n")
                if ttc < float('inf'):
                    self.info_text.insert(tk.END, f"  Time to Collision: {ttc:.2f} s\n")
            else:
                self.info_text.insert(tk.END, f"  Status: Safe\n")
        
        self.info_text.see(tk.END)
    
    def update_alert_indicator(self, severity, messages):
        """Update alert indicator"""
        if severity == 'critical':
            self.alert_label.config(text="🚨 CRITICAL ALERT", fg='#dc3545', bg='#2b2b2b')
        elif severity == 'high':
            self.alert_label.config(text="⚠️ HIGH ALERT", fg='#ff6b00', bg='#2b2b2b')
        elif severity == 'medium':
            self.alert_label.config(text="⚠️ MEDIUM ALERT", fg='#ffc107', bg='#2b2b2b')
        elif severity == 'low':
            self.alert_label.config(text="⚠️ LOW ALERT", fg='#ffc107', bg='#2b2b2b')
        else:
            self.alert_label.config(text="", bg='#2b2b2b')
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.input_handler and not self.input_handler.is_image:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_button.config(text="Resume", bg='#28a745')
                self.status_label.config(text="Paused", fg='#ffc107')
            else:
                self.pause_button.config(text="Pause", bg='#ffc107')
                self.status_label.config(text="Processing...", fg='#28a745')
    
    def stop_detection(self):
        """Stop the detection process"""
        self.is_processing = False
        self.is_paused = False
        
        if self.input_handler:
            self.input_handler.release()
            self.input_handler = None
        
        # Reset UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.pause_button.config(text="Pause", bg='#ffc107')
        self.status_label.config(text="Stopped", fg='#dc3545')
        self.alert_label.config(text="", bg='#2b2b2b')
        
        # Clear display
        self.canvas.delete("all")
        self.canvas.create_text(
            400, 300,
            text="Detection stopped",
            fill='#888888',
            font=('Arial', 14)
        )
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "Detection stopped.\n")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = CollisionDetectionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

