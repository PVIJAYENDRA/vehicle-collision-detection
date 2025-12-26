"""
Debug script to test vehicle detection and see what's being detected
"""

import cv2
import numpy as np
from ultralytics import YOLO
from config import *

def test_detection_on_frame(frame_path=None, camera_index=0):
    """Test detection on a frame"""
    
    print("=" * 60)
    print("Vehicle Detection Debug Tool")
    print("=" * 60)
    
    # Load model
    print("\nLoading YOLOv8 model...")
    model = YOLO('yolov8n.pt')
    print("Model loaded!")
    
    # Load frame
    if frame_path:
        print(f"\nLoading image: {frame_path}")
        frame = cv2.imread(frame_path)
        if frame is None:
            print(f"Error: Could not load image {frame_path}")
            return
    else:
        print(f"\nOpening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            return
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from camera")
            return
        cap.release()
    
    print(f"Frame size: {frame.shape[1]}x{frame.shape[0]}")
    
    # Run detection with different confidence levels
    print("\n" + "=" * 60)
    print("Testing with different confidence thresholds:")
    print("=" * 60)
    
    for conf_thresh in [0.1, 0.25, 0.5]:
        print(f"\nConfidence threshold: {conf_thresh}")
        results = model(frame, conf=conf_thresh, verbose=False)
        
        all_detections = 0
        vehicle_detections = 0
        detected_classes = {}
        
        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes
                all_detections += len(boxes)
                
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Get class name
                    class_name = model.names[cls] if hasattr(model, 'names') else f"Class_{cls}"
                    
                    if cls not in detected_classes:
                        detected_classes[cls] = []
                    detected_classes[cls].append((conf, class_name))
                    
                    if cls in VEHICLE_CLASSES:
                        vehicle_detections += 1
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        print(f"  ✓ Vehicle detected: {class_name} (conf: {conf:.2f}) at [{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]")
        
        print(f"  Total detections: {all_detections}")
        print(f"  Vehicle detections: {vehicle_detections}")
        
        if detected_classes:
            print(f"  All detected classes:")
            for cls, dets in detected_classes.items():
                class_name = model.names[cls] if hasattr(model, 'names') else f"Class_{cls}"
                print(f"    - {class_name} (class {cls}): {len(dets)} detections")
    
    # Visual test
    print("\n" + "=" * 60)
    print("Creating visualization...")
    print("=" * 60)
    
    # Run with current config settings
    results = model(frame, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD, verbose=False)
    
    output_frame = frame.copy()
    vehicle_count = 0
    
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                if cls in VEHICLE_CLASSES:
                    vehicle_count += 1
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                    
                    # Draw box
                    cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    
                    # Draw label with background for better visibility
                    class_name = model.names[cls] if hasattr(model, 'names') else f"Class_{cls}"
                    label = f"{class_name} {conf:.2f}"
                    
                    # Draw semi-transparent background
                    (text_width, text_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                    padding = 5
                    overlay = output_frame.copy()
                    cv2.rectangle(overlay, 
                                 (x - padding, y - text_height - padding - 5),
                                 (x + text_width + padding, y + baseline + padding),
                                 (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.7, output_frame, 0.3, 0, output_frame)
                    
                    # Draw text with outline
                    for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                        cv2.putText(output_frame, label, (x + dx, y - 10 + dy),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
                    cv2.putText(output_frame, label, (x, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Add info text
    info_text = f"Vehicles detected: {vehicle_count} (Conf: {CONFIDENCE_THRESHOLD})"
    cv2.putText(output_frame, info_text, (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Show COCO class info
    print("\n" + "=" * 60)
    print("COCO Dataset Vehicle Classes:")
    print("=" * 60)
    print("Class 2: car")
    print("Class 3: motorcycle")
    print("Class 5: bus")
    print("Class 7: truck")
    print(f"\nCurrent VEHICLE_CLASSES setting: {VEHICLE_CLASSES}")
    print(f"Current CONFIDENCE_THRESHOLD: {CONFIDENCE_THRESHOLD}")
    
    # Display
    print(f"\nDisplaying result (found {vehicle_count} vehicles)...")
    print("Press any key to close...")
    
    cv2.imshow("Vehicle Detection Debug", output_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 60)
    print("Debug complete!")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with image file
        test_detection_on_frame(frame_path=sys.argv[1])
    elif len(sys.argv) > 2 and sys.argv[1] == "--camera":
        # Test with camera
        camera_idx = int(sys.argv[2])
        test_detection_on_frame(camera_index=camera_idx)
    else:
        print("Usage:")
        print("  python debug_detection.py <image_path>")
        print("  python debug_detection.py --camera <camera_index>")
        print("\nExample:")
        print("  python debug_detection.py vv.mp4  # Will extract first frame")
        print("  python debug_detection.py --camera 0")
        
        # Try to use vv.mp4 if it exists
        import os
        if os.path.exists("vv.mp4"):
            print("\nTrying to extract first frame from vv.mp4...")
            cap = cv2.VideoCapture("vv.mp4")
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite("test_frame.jpg", frame)
                    print("Extracted frame saved as test_frame.jpg")
                    test_detection_on_frame(frame_path="test_frame.jpg")
                cap.release()

