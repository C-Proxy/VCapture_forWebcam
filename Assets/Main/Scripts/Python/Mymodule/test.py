import cv2
import time

"""cd assets/main/scripts/python/mymodule"""
"""py test.py"""
while True:
    print("test")
    time.sleep(1)
    if cv2.waitKey(0) == 97:
        break
