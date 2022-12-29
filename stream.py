#!/usr/bin/python3

"""
@brief      This is program for stream video from Tello camera.
@author     Murtadha Bazli Tukimat
@date       17-Nov-2020
"""
import cv2, queue, threading, time

# bufferless VideoCapture
class VideoCapture:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    # print("Starting Thread")
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        continue
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()

import threading
import cv2


""" Welcome note """
print("\nTello Video Stream Program\n")


class Tello:
    def __init__(self):
        self._running = True
        self.video = VideoCapture(0)

    def terminate(self):
        self._running = False
        cv2.destroyAllWindows()

    def recv(self):
        """ Handler for Tello states message """
        while self._running:
            try:
                # Get the most recent frame from the queue.
                frame = self.video.read()

                # Resize frame
                height, width, _ = frame.shape
                new_h = int(height / 2)
                new_w = int(width / 2)

                # Resize for improved performance
                new_frame = cv2.resize(frame, (new_w, new_h))

                # Display the resulting frame
                cv2.imshow('Tello', new_frame)
                # Wait for display image frame
                # cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.waitKey(1)
            except Exception as err:
                print(err)


""" Start new thread for receive Tello response message """
t = Tello()
recvThread = threading.Thread(target=t.recv)
recvThread.start()

while True:
    try:
        # Get input from CLI
        msg = input()

        # Check for "end"
        if msg == "bye":
            t.terminate()
            recvThread.join()
            print("\nGood Bye\n")
            break
    except KeyboardInterrupt:
        t.terminate()
        recvThread.join()
        break

# import subprocess
# import numpy as np
# import cv2

# FFMPEG_CMD = "ffmpeg -flags low_delay -i udp://192.168.10.1:11111 -f sdl 'window'"
# WIDTH = 500
# HEIGHT = 500

# process = subprocess.Popen(FFMPEG_CMD, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

# while True:
#     raw_frame = process.stdout.read(WIDTH*HEIGHT*3)
#     frame = np.frombuffer(raw_frame) 
#     frame = frame.reshape((HEIGHT, WIDTH, 3))
#     cv2.imshow("window", frame)


# cap = cv2.VideoCapture("udp://192.168.10.1:11111")
# while True:
#   ret, frame = cap.read()
#   cv2.imshow("frame", frame)
#   if chr(cv2.waitKey(1)&255) == 'q':
#     break