import cv2
import numpy as np

class ObjectDetection:

  # Constructor for an ObjectDetection object.
  def __init__(self, cap, lb, ub ):

    # Video capture device.
    self.cap = cap

    # Upper and lower bounds for desired color
    self.lb = lb 
    self.ub = ub

    # Get the dimensions of the video feed.
    if self.cap:
      self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
      self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
      self.width = 960
      self.height = 720

  # Determines the region that a point is in based on the dimensions of the
  # video feed. Returns an integer from 1-9 representing the region.
  def get_region(self, point) -> int:
    x, y = point
    if x < self.width//3:
      if y < self.height//3:
        return 1
      elif y < self.height//3*2:
        return 4
      else:
        return 7
    elif x < self.width//3*2:
      if y < self.height//3:
        return 2
      elif y < self.height//3*2:
        return 5
      else:
        return 8
    else:
      if y < self.height//3:
        return 3
      elif y < self.height//3*2:
        return 6
      else:
        return 9

  # Adds bounding box around the object, returning an array of all (x,y) pairs
  # representing the center of each bounding box. The length of this array 
  # represents the number of objects detected in the frame.
  def add_bounding_box(self, img, mask) -> list:
    points = []
    contours, _= cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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
        points.append((cx,cy))
    return points

  # Draws 4 lines to segment video feed into 9 equal regions. Additionally,
  # draws a red rectangle around the region that the object is in if the
  # 'region' parameter is supplied.
  def add_grid(self, img, region=-1):
    cv2.line(img, (self.width//3, 0), (self.width//3, self.height), (224, 224, 224), 1)
    cv2.line(img, (self.width//3*2, 0), (self.width//3*2, self.height), (224, 224, 224), 1)
    cv2.line(img, (0, self.height//3), (self.width, self.height//3), (224, 224, 224), 1)
    cv2.line(img, (0, self.height//3*2), (self.width, self.height//3*2), (224, 224, 224), 1)

    if region == 1:
      cv2.rectangle(img, (0, 0), (self.width//3, self.height//3), (0, 0, 255), 1)
    elif region == 2:
      cv2.rectangle(img, (self.width//3, 0), (self.width//3*2, self.height//3), (0, 0, 255), 1)
    elif region == 3:
      cv2.rectangle(img, (self.width//3*2, 0), (self.width, self.height//3), (0, 0, 255), 1)
    elif region == 4:
      cv2.rectangle(img, (0, self.height//3), (self.width//3, self.height//3*2), (0, 0, 255), 1)
    elif region == 5:
      cv2.rectangle(img, (self.width//3, self.height//3), (self.width//3*2, self.height//3*2), (0, 0, 255), 1)
    elif region == 6:
      cv2.rectangle(img, (self.width//3*2, self.height//3), (self.width, self.height//3*2), (0, 0, 255), 1)
    elif region == 7:
      cv2.rectangle(img, (0, self.height//3*2), (self.width//3, self.height), (0, 0, 255), 1)
    elif region == 8:
      cv2.rectangle(img, (self.width//3, self.height//3*2), (self.width//3*2, self.height), (0, 0, 255), 1)
    elif region == 9:
      cv2.rectangle(img, (self.width//3*2, self.height//3*2), (self.width, self.height), (0, 0, 255), 1)
    else:
        return

  # Process and return a single frame of the video feed. This includes adding
  # a bounding box around the object, and drawing a grid to segment the video
  # feed into 9 equal regions, and determining the region that the object is
  # in.
  def process_frame(self, frame):
    # Convert the frame to HSV and apply a mask to filter out the object.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, self.lb, self.ub)

    # Add bounding box around the object, and determine the region it is in.
    region = -1
    bounding_coords = self.add_bounding_box(frame, mask)
    if len(bounding_coords) >= 1:
      region = self.get_region(bounding_coords[0])
    
    # Add grid lines to the frame and color the region the object is in.
    self.add_grid(frame, region)

    # Return the frame.
    return frame

# Entry point of the program.
def main():
  print("Starting object recognition...")
  objr = ObjectDetection(cv2.VideoCapture(0), np.array([34, 56, 61]), np.array([68, 210, 180]))
  print("Frame Resolution:", f'{objr.width}x{objr.height}')

  while objr.cap.isOpened():
    # Capture the next frame.
    ret, img = objr.cap.read()

    # Process the frame.
    img = objr.process_frame(img)

    # Display the resulting frame (uncomment to display mask).
    # cv2.imshow('img', cv2.flip(mask, 1))
    cv2.imshow('img2', cv2.flip(img, 1))
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # Release the video capture object.
  objr.cap.release()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()