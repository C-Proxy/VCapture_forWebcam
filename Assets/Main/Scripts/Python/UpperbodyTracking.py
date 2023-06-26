from asyncio.windows_events import NULL
import mediapipe as mp
import socket
import cv2
import json

from sqlalchemy import null

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# cd assets/main/scripts/python

fps = 10
host_setting = ("127.0.0.1", 10800)


def make_handinfo(results_hands):
    if results_hands.multi_hand_world_landmarks:
        return [
            {
                "Label": results_hands.multi_handedness[h_id].classification[0].label,
                "Points": [
                    {"x": lm.x, "y": -lm.y, "z": -lm.z}
                    for lm in hand_landmarks.landmark
                ],
            }
            for h_id, hand_landmarks in enumerate(
                results_hands.multi_hand_world_landmarks
            )
        ]
    else:
        return []


def make_poseinfo(results_pose):
    if results_pose.pose_world_landmarks:
        landmark = results_pose.pose_world_landmarks.landmark
        landmarks = [
            landmark[0],  # nose
            landmark[5],  # eye_R
            landmark[2],  # eye_L
            landmark[12],  # shoulder_R
            landmark[11],  # shoulder_L
            landmark[14],  # elbow_R
            landmark[13],  # elbow_L
            landmark[16],  # hand_R
            landmark[15],  # hand_L
        ]

        return {
            "Label": "Pose",
            "Points": [{"x": lm.x, "y": -lm.y, "z": -lm.z} for lm in landmarks],
        }
    else:
        return {}


def sendto_unity(sock: socket, data):
    if len(data) != 0:
        json_data = json.dumps(data)
        sock.sendto(json_data.encode("utf-8"), host_setting)


# For webcam input:
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
    model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5
) as pose, mp_hands.Hands(
    model_complexity=0, min_detection_confidence=0.7, min_tracking_confidence=0.7
) as hands, socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM
) as sock:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image = cv2.flip(image, 1)
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results_pose = pose.process(image)
        results_hands = hands.process(image)

        sendto_unity(sock, make_poseinfo(results_pose))
        for h_info in make_handinfo(results_hands):
            sendto_unity(sock, h_info)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results_pose.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
        )
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow("MediaPipe Pose", cv2.flip(image, 1))
        if cv2.waitKey(int(1000 / fps)) & 0xFF == 27:
            break
cap.release()
