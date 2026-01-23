import cv2
import apriltag
import time

FAMILY = "tag36h11"
dic_platforms = {0: "Voie A", 1: "Voie B", 2: "Voie C", 3: "Voie D"}

def run_vision():

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    options = apriltag.DetectorOptions(families=FAMILY)
    detector = apriltag.Detector(options)

    print(f"--- VISION ACTIVE ({FAMILY}) ---")
    print("Recherche de tags AprilTag...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detections = detector.detect(gray)

            if len(detections) > 0:
                for detection in detections:
                    tag_id = detection.tag_id
                    center_x = int(detection.center[0])
                    center_y = int(detection.center[1])
                    platform_name = dic_platforms.get(tag_id, "Unknown Platform")
                    print(f"Detected Tag ID: {tag_id} - {platform_name}")
    
    except KeyboardInterrupt:
        print("Vision process interrupted by user.")
    finally:
        cap.release()
        print("Vision process terminated.")

if __name__ == "__main__":
    run_vision()