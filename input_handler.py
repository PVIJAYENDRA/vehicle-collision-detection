"""
Input handler for different input types: image, video, and live feed
"""

import cv2
import os
import numpy as np
from pathlib import Path


class InputHandler:
    """Handles different input types: image, video file, or live camera feed"""
    
    def __init__(self, input_source, input_type='auto'):
        """
        Initialize input handler
        
        Args:
            input_source: Path to image/video file, or camera index (int)
            input_type: 'image', 'video', 'live', or 'auto' (auto-detect)
        """
        self.input_source = input_source
        self.input_type = input_type
        self.cap = None
        self.is_image = False
        self.is_video = False
        self.is_live = False
        self.image = None
        self.frame_count = 0
        self.total_frames = 0
        self.fps = 30.0
        
        # Auto-detect input type if not specified
        if input_type == 'auto':
            self.input_type = self._detect_input_type(input_source)
        
        self._initialize_input()
    
    def _detect_input_type(self, source):
        """Auto-detect input type from source"""
        if isinstance(source, int):
            return 'live'
        elif isinstance(source, str):
            if os.path.isfile(source):
                ext = Path(source).suffix.lower()
                if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                    return 'image'
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']:
                    return 'video'
            return 'live'  # Assume camera index if file doesn't exist
        return 'live'
    
    def _initialize_input(self):
        """Initialize the input source based on type"""
        if self.input_type == 'image':
            self._initialize_image()
        elif self.input_type == 'video':
            self._initialize_video()
        elif self.input_type == 'live':
            self._initialize_live()
        else:
            raise ValueError(f"Unknown input type: {self.input_type}")
    
    def _initialize_image(self):
        """Initialize image input"""
        if not os.path.isfile(self.input_source):
            raise FileNotFoundError(f"Image file not found: {self.input_source}")
        
        self.image = cv2.imread(self.input_source)
        if self.image is None:
            raise ValueError(f"Could not read image: {self.input_source}")
        
        self.is_image = True
        self.total_frames = 1
        print(f"Loaded image: {self.input_source}")
        print(f"Image size: {self.image.shape[1]}x{self.image.shape[0]}")
    
    def _initialize_video(self):
        """Initialize video file input"""
        if not os.path.isfile(self.input_source):
            raise FileNotFoundError(f"Video file not found: {self.input_source}")
        
        self.cap = cv2.VideoCapture(self.input_source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {self.input_source}")
        
        self.is_video = True
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Loaded video: {self.input_source}")
        print(f"Video size: {width}x{height}, FPS: {self.fps:.2f}, Frames: {self.total_frames}")
    
    def _initialize_live(self):
        """Initialize live camera feed"""
        if not isinstance(self.input_source, int):
            # Try to convert to int if it's a string
            try:
                self.input_source = int(self.input_source)
            except:
                raise ValueError(f"Invalid camera index: {self.input_source}")
        
        self.cap = cv2.VideoCapture(self.input_source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera {self.input_source}")
        
        self.is_live = True
        self.total_frames = -1  # Unknown for live feed
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Initialized live camera: {self.input_source}")
        print(f"Camera resolution: {width}x{height}, FPS: {self.fps:.2f}")
    
    def read(self):
        """
        Read next frame
        
        Returns:
            (ret, frame) where ret is True if frame is valid, frame is the image
        """
        if self.is_image:
            if self.frame_count == 0:
                self.frame_count = 1
                return True, self.image.copy()
            else:
                return False, None
        
        elif self.is_video or self.is_live:
            ret, frame = self.cap.read()
            if ret:
                self.frame_count += 1
            return ret, frame
        
        return False, None
    
    def get_frame_number(self):
        """Get current frame number"""
        return self.frame_count
    
    def get_total_frames(self):
        """Get total number of frames (-1 for live feed)"""
        return self.total_frames
    
    def get_fps(self):
        """Get frames per second"""
        return self.fps
    
    def is_finished(self):
        """Check if input is finished (for video/image)"""
        if self.is_image:
            return self.frame_count > 0
        elif self.is_video:
            return self.frame_count >= self.total_frames
        elif self.is_live:
            return False  # Live feed never finishes
        return True
    
    def reset(self):
        """Reset to beginning (for video/image)"""
        if self.is_image:
            self.frame_count = 0
        elif self.is_video and self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_count = 0
    
    def release(self):
        """Release resources"""
        if self.cap is not None:
            self.cap.release()
        self.cap = None
    
    def get_properties(self):
        """Get input properties"""
        return {
            'type': self.input_type,
            'is_image': self.is_image,
            'is_video': self.is_video,
            'is_live': self.is_live,
            'frame_count': self.frame_count,
            'total_frames': self.total_frames,
            'fps': self.fps
        }


class MultiInputHandler:
    """Handles multiple inputs for multi-view system"""
    
    def __init__(self, input_sources):
        """
        Initialize multi-input handler
        
        Args:
            input_sources: Dict with view names as keys and input sources as values
                          e.g., {'front': 0, 'back': 'video.mp4', 'left': 'image.jpg'}
        """
        self.input_handlers = {}
        self.views = list(input_sources.keys())
        
        for view, source in input_sources.items():
            if source is not None:
                try:
                    self.input_handlers[view] = InputHandler(source)
                    print(f"Initialized {view} view: {source}")
                except Exception as e:
                    print(f"Warning: Could not initialize {view} view ({source}): {e}")
    
    def read_all(self):
        """
        Read frames from all inputs
        
        Returns:
            Dict with view names as keys and (ret, frame) tuples as values
        """
        frames = {}
        for view, handler in self.input_handlers.items():
            ret, frame = handler.read()
            frames[view] = (ret, frame)
        return frames
    
    def get_frame_sizes(self):
        """Get frame sizes for all inputs"""
        sizes = {}
        for view, handler in self.input_handlers.items():
            if handler.is_image and handler.image is not None:
                h, w = handler.image.shape[:2]
                sizes[view] = (w, h)
            elif handler.cap is not None:
                w = int(handler.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(handler.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                sizes[view] = (w, h)
        return sizes
    
    def release_all(self):
        """Release all input handlers"""
        for handler in self.input_handlers.values():
            handler.release()
    
    def get_available_views(self):
        """Get list of available views"""
        return list(self.input_handlers.keys())


