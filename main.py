
import cv2
import numpy as np
from ultralytics import YOLO
import threading
from alert_system import send_emergency_mail

# Configuration
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("20261010-0705-24.0267316.mp4")
print("Video opened:", cap.isOpened())
print("Video path:", cap.get(cv2.CAP_PROP_FRAME_COUNT))
CONF_THRESHOLD = 0.4
OVERLAP_THRESHOLD = 0.35
STOP_THRESHOLD = 3
CONFIRM_FRAMES = 5
ALERT_FRAMES = 80

frame_count = 0
candidate_frames = 0
accident_detected = False
accident_point = None
alert_timer = 0
email_sent = False


previous_centers = {}
stationary_counts = {}


# Calculate Intersection over Union (IoU)
def iou(a, b):
    xA = max(a[0], b[0])
    yA = max(a[1], b[1])
    xB = min(a[2], b[2])
    yB = min(a[3], b[3])

    intersection = max(0, xB - xA) * max(0, yB - yA)

    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])

    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0


# Main video loop
try:
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1
        height, width = frame.shape[:2]

        small = cv2.resize(frame, (640, 360))

        results = model.track(
            small,
            persist=True,
            tracker="bytetrack.yaml",
            conf=CONF_THRESHOLD,
            verbose=False
        )

        boxes = []
        centers = []
        track_ids = []

        sx, sy = width / 640, height / 360

        # Detect and track vehicles
        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                cls = int(box.cls[0])

                # Car, motorcycle, bus and truck
                if cls not in [2, 3, 5, 7] or box.id is None:
                    continue

                track_id = int(box.id[0])

                x1, y1, x2, y2 = map(
                    int, box.xyxy[0].tolist()
                )

                x1, x2 = int(x1 * sx), int(x2 * sx)
                y1, y2 = int(y1 * sy), int(y2 * sy)

                center = (
                    (x1 + x2) // 2,
                    (y1 + y2) // 2
                )

                boxes.append((x1, y1, x2, y2))
                centers.append(center)
                track_ids.append(track_id)

                cv2.rectangle(
                    frame, (x1, y1), (x2, y2),
                    (0, 255, 0), 2
                )

                cv2.putText(
                    frame, f"ID: {track_id}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2
                )

        # Measure vehicle movement
        current_centers = {}
        current_stationary_counts = {}

        for track_id, center in zip(track_ids, centers):
            current_centers[track_id] = center

            if track_id in previous_centers:
                movement = np.linalg.norm(
                    np.array(center, dtype=float)
                    - np.array(previous_centers[track_id], dtype=float)
                )

                if movement < STOP_THRESHOLD:
                    current_stationary_counts[track_id] = (
                        stationary_counts.get(track_id, 0) + 1
                    )
                else:
                    current_stationary_counts[track_id] = 0
            else:
                current_stationary_counts[track_id] = 0

        # Check possible accidents
        if frame_count > 20 and not accident_detected:
            potential_accident = False
            candidate_point = None

            for i in range(len(boxes)):
                for j in range(i + 1, len(boxes)):
                    if iou(boxes[i], boxes[j]) <= OVERLAP_THRESHOLD:
                        continue

                    id_a, id_b = track_ids[i], track_ids[j]

                    stopped_a = (
                        current_stationary_counts.get(id_a, 0)
                        >= CONFIRM_FRAMES
                    )
                    stopped_b = (
                        current_stationary_counts.get(id_b, 0)
                        >= CONFIRM_FRAMES
                    )

                    if stopped_a and stopped_b:
                        potential_accident = True
                        candidate_point = (
                            (centers[i][0] + centers[j][0]) // 2,
                            (centers[i][1] + centers[j][1]) // 2
                        )
                        break

                if potential_accident:
                    break

            if potential_accident:
                candidate_frames += 1
                accident_point = candidate_point
            else:
                candidate_frames = 0
                accident_point = None

            if candidate_frames >= CONFIRM_FRAMES:
                accident_detected = True
                alert_timer = ALERT_FRAMES

                if not email_sent:
                    print("Potential accident confirmed. Sending email.")

                    threading.Thread(
                        target=send_emergency_mail,
                        daemon=True
                    ).start()

                    email_sent = True

        previous_centers = current_centers.copy()
        stationary_counts = current_stationary_counts.copy()

        # Display alert
        if alert_timer > 0 and accident_point is not None:
            x, y = accident_point

            cv2.putText(
                frame, "ACCIDENT DETECTED",
                (max(10, x - 140), max(30, y - 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 0, 255), 3
            )

            alert_timer -= 1

        display_frame = cv2.resize(frame, (1000, 600))
        cv2.imshow("Road Accident Detection System", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
