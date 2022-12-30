import cv2
import numpy as np

# Using primary webcam for video capture.
cap = cv2.VideoCapture(0)

# Upper and lower bounds for light green color.
l_b = np.array([167, 0, 100])
u_b = np.array([179, 255, 255])

# Display the video feed.
while cap.isOpened():
  ret, img = cap.read()

  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  mask = cv2.inRange(hsv, l_b, u_b)

  contours, _= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
  for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 1000:
      # cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)
      x, y, w, h = cv2.boundingRect(cnt)
      cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

      M = cv2.moments(cnt)
      cx=int(M['m10']//M['m00'])
      cy=int(M['m01']//M['m00'])
      cv2.circle(img, (cx,cy),3,(255,0,0),-1)
      print(cx, cy)

  cv2.imshow('img', cv2.flip(mask, 1))
  cv2.imshow('img2', cv2.flip(img, 1))
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# Release the video capture object.
cap.release()
cv2.destroyAllWindows()

