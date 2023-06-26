from asyncio.windows_events import NULL
import socket
import time
import json
import mediapipe as mp
import cv2

sock_setting = ("127.0.0.1", 10800)
fps = 2.0

connectunity = True

landmark_line_ids = []


def ConnectUnity():
    if connectunity == False:
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock


def init_mp():
    global landmark_line_ids

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,  # 最大検出数
        min_detection_confidence=0.7,  # 検出信頼度
        min_tracking_confidence=0.7,  # 追跡信頼度
    )

    # landmarkの繋がり表示用
    landmark_line_ids = [
        (0, 1),
        (1, 5),
        (5, 9),
        (9, 13),
        (13, 17),
        (17, 0),  # 掌
        (1, 2),
        (2, 3),
        (3, 4),  # 親指
        (5, 6),
        (6, 7),
        (7, 8),  # 人差し指
        (9, 10),
        (10, 11),
        (11, 12),  # 中指
        (13, 14),
        (14, 15),
        (15, 16),  # 薬指
        (17, 18),
        (18, 19),
        (19, 20),  # 小指
    ]

    cap = cv2.VideoCapture(0)  # カメラのID指定
    return hands, cap


def GetHands(hands, cap):
    global landmark_line_ids

    if cap.isOpened():
        # カメラから画像取得
        success, img = cap.read()
        if not success:
            return NULL
        img = cv2.flip(img, 1)  # 画像を左右反転
        img_h, img_w, _ = img.shape  # サイズ取得

        Res = NULL
        # 検出処理の実行
        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if results.multi_hand_world_landmarks:
            # 検出した情報をまとめる
            Res = make_hand_landmarks_json(
                results.multi_hand_world_landmarks[0], img_h, img_w
            )
    return Res


def make_hand_landmarks_json(hand_landmarks, img_h, img_w):
    res = []
    index = 0
    for lm in hand_landmarks.landmark:
        data_p = {}
        data = {}

        data_p["x"] = lm.x * img_w
        data_p["y"] = lm.y * img_h
        data_p["z"] = lm.z
        data["Index"] = index
        data["Point"] = data_p
        # print(index, data_p['x'], data_p['y'], data_p['z'])
        res.append(data)
        index += 1
    return res


def main():
    sock = ConnectUnity()

    hands, cap = init_mp()
    try:
        while True:
            data = GetHands(hands, cap)
            json_data = json.dumps(data)
            if connectunity == True:
                sock.sendto(json_data.encode("utf-8"), sock_setting)
            # FPSは2で行う
            time.sleep(1 / fps)
    except ConnectionAbortedError:
        print("Connection aborte")
    finally:
        cap.release()
        print("closing socket")
        sock.close()
        print("done")


if __name__ == "__main__":
    main()
