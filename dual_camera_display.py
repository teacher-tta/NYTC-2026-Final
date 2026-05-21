"""
Dual Camera Display Script
==========================
This script captures video from two sources simultaneously:
  1. The UGOT robot camera
  2. Your local webcam (accessed via OpenCV's VideoCapture)

Each frame from both sources is read in a loop, resized to match dimensions,
and then combined into a single OpenCV window for display.

Layout options (see below in main()):
  - Side by side (horizontal): np.hstack()  <-- active by default
  - Stacked vertically:        np.vstack()  <-- commented out

Press 'q' at any time to quit.
"""

import cv2
import numpy as np
from ugot import ugot

# --- Robot camera setup ---
# Initialize the UGOT robot and connect to it over the local network
got = ugot.UGOT()
got.initialize("192.168.88.1")  # Replace with your robot's IP if different
got.open_camera()  # Start the robot's onboard camera stream

# --- Webcam setup ---
# 0 = default system webcam. Change to 1, 2, etc. for other connected cameras
webcam = cv2.VideoCapture(0)


def main():
    while True:

        #  Robot Camera

        # Read a raw JPEG frame from the robot camera over the network
        frame = got.read_camera_data()

        if not frame:
            print("Failed to grab robot camera frame")
            break

        # Convert the raw bytes into a NumPy array, then decode into a BGR image
        nparr = np.frombuffer(frame, np.uint8)
        robot_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        #  Webcam

        # Read a frame from the local webcam
        # ret = bool indicating success, webcam_frame = the image array
        ret, webcam_frame = webcam.read()

        if not ret:
            print("Failed to grab webcam frame")
            break

        #  Resize frames

        # HORIZONTAL LAYOUT (side by side):
        # Both frames must share the same HEIGHT so hstack lines them up cleanly.
        # Each frame is scaled proportionally to preserve its aspect ratio.
        target_height = 480

        robot_h, robot_w = robot_frame.shape[:2]
        robot_frame = cv2.resize(
            robot_frame, (int(robot_w * target_height / robot_h), target_height)
        )

        webcam_h, webcam_w = webcam_frame.shape[:2]
        webcam_frame = cv2.resize(
            webcam_frame, (int(webcam_w * target_height / webcam_h), target_height)
        )

        # VERTICAL LAYOUT (stacked):
        # Uncomment the block below (and comment out the horizontal block above)
        # if you prefer a vertical stack. Frames must share the same WIDTH instead.
        #
        # target_width = 640
        #
        # robot_h, robot_w = robot_frame.shape[:2]
        # robot_frame = cv2.resize(
        #     robot_frame,
        #     (target_width, int(robot_h * target_width / robot_w))
        # )
        #
        # webcam_h, webcam_w = webcam_frame.shape[:2]
        # webcam_frame = cv2.resize(
        #     webcam_frame,
        #     (target_width, int(webcam_h * target_width / webcam_w))
        # )

        #  Combine and display

        # Horizontal: place robot feed on the left, webcam on the right
        combined = np.hstack((robot_frame, webcam_frame))

        # Vertical: place robot feed on top, webcam on the bottom
        # Uncomment the line below and comment out the hstack line above to switch
        # combined = np.vstack((robot_frame, webcam_frame))

        cv2.imshow("Robot Camera | Webcam", combined)

        #  Quit

        # Wait 1ms for a keypress. If 'q' is pressed, exit the loop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the webcam and close all OpenCV windows on exit
    webcam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
