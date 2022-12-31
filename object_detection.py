"""
Payton Shaltis
12/31/2022

Contains the ObjectDetection class for creating ObjectDetection instances.
An instance of the class requires a set of color ranges for the objects to be
detected, as well as an optional VideoCapture object for the video feed. The 
class provides one useful public method, process_frame(), which takes a frame,
and draws a bounding box around the detected object. This method also segments
the frame into 9 equal regions, and highlights and returns the region that the
object is in. Getters are provided for some of the private instance variables.
"""

import cv2
from ranges import RANGES

class ObjectDetection:

  # Constructor for an ObjectDetection object.
  def __init__(self, bounds, cap=None):

    # Upper and lower bounds for desired color
    self.__bounds = bounds

    # Optional video capture device.
    self.__cap = cap

    # Get the dimensions of the video feed.
    if self.__cap:
      self.__width = int(self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH))
      self.__height = int(self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
      self.__width = 960
      self.__height = 720

  # Getters for private instance variables.
  def get_bounds(self):
    return self.__bounds

  def get_cap(self):
    return self.__cap

  def get_width(self):
    return self.__width

  def get_height(self):
    return self.__height

  # Determines the region that a point is in based on the dimensions of the
  # video feed. Returns an integer from 1-9 representing the region.
  def __get_region(self, point) -> int:
    x, y = point
    if x < self.__width//3:
      if y < self.__height//3:
        return 1
      elif y < self.__height//3*2:
        return 4
      else:
        return 7
    elif x < self.__width//3*2:
      if y < self.__height//3:
        return 2
      elif y < self.__height//3*2:
        return 5
      else:
        return 8
    else:
      if y < self.__height//3:
        return 3
      elif y < self.__height//3*2:
        return 6
      else:
        return 9

  # Adds bounding box around the object, returning an array of all (x,y) pairs
  # representing the center of each bounding box. The length of this array 
  # represents the number of objects detected in the frame.
  def __add_bounding_box(self, img, mask) -> list:
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
  def __add_grid(self, img, region=-1):
    cv2.line(img, (self.__width//3, 0), (self.__width//3, self.__height), (224, 224, 224), 1)
    cv2.line(img, (self.__width//3*2, 0), (self.__width//3*2, self.__height), (224, 224, 224), 1)
    cv2.line(img, (0, self.__height//3), (self.__width, self.__height//3), (224, 224, 224), 1)
    cv2.line(img, (0, self.__height//3*2), (self.__width, self.__height//3*2), (224, 224, 224), 1)

    if region == 1:
      cv2.rectangle(img, (0, 0), (self.__width//3, self.__height//3), (0, 0, 255), 1)
    elif region == 2:
      cv2.rectangle(img, (self.__width//3, 0), (self.__width//3*2, self.__height//3), (0, 0, 255), 1)
    elif region == 3:
      cv2.rectangle(img, (self.__width//3*2, 0), (self.__width, self.__height//3), (0, 0, 255), 1)
    elif region == 4:
      cv2.rectangle(img, (0, self.__height//3), (self.__width//3, self.__height//3*2), (0, 0, 255), 1)
    elif region == 5:
      cv2.rectangle(img, (self.__width//3, self.__height//3), (self.__width//3*2, self.__height//3*2), (0, 0, 255), 1)
    elif region == 6:
      cv2.rectangle(img, (self.__width//3*2, self.__height//3), (self.__width, self.__height//3*2), (0, 0, 255), 1)
    elif region == 7:
      cv2.rectangle(img, (0, self.__height//3*2), (self.__width//3, self.__height), (0, 0, 255), 1)
    elif region == 8:
      cv2.rectangle(img, (self.__width//3, self.__height//3*2), (self.__width//3*2, self.__height), (0, 0, 255), 1)
    elif region == 9:
      cv2.rectangle(img, (self.__width//3*2, self.__height//3*2), (self.__width, self.__height), (0, 0, 255), 1)
    else:
        return

  # Process and return a single frame of the video feed. This includes adding
  # a bounding box around the object, and drawing a grid to segment the video
  # feed into 9 equal regions, and determining the region that the object is
  # in.
  def process_frame(self, frame) -> tuple:
    # Convert the frame to HSV and apply mask(s) to filter out the object.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = None

    # If only a single bound is provided, that is the mask.
    if len(self.__bounds) == 1:
      lb, ub = self.__bounds[0]
      mask = cv2.inRange(hsv, lb, ub)

    # If multiple bounds are provided, combine them into a single mask.
    for bound in self.__bounds:
      lb, ub = bound
      if mask is None:
        mask = cv2.inRange(hsv, lb, ub)
      else:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lb, ub)) 

    # Add bounding box around the object, and determine the region it is in.
    region = -1
    bounding_coords = self.__add_bounding_box(frame, mask)
    if len(bounding_coords) >= 1:
      region = self.__get_region(bounding_coords[0])
    
    # Add grid lines to the frame and color the region the object is in.
    self.__add_grid(frame, region)

    # Return the frame and the region the object is in.
    return (frame, region)

# Entry point of the program.
def __main():
  print("Starting object recognition...")
  objr = ObjectDetection(RANGES['lime'], cv2.VideoCapture(0))
  print("Frame Resolution:", f'{objr.get_width()}x{objr.get_height()}')

  while objr.get_cap().isOpened():
    # Capture the next frame.
    _, img = objr.get_cap().read()

    # Process the frame.
    img, _ = objr.process_frame(img)

    # Display the resulting frame (uncomment to display mask).
    # cv2.imshow('img', cv2.flip(mask, 1))
    cv2.imshow('img2', cv2.flip(img, 1))
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # Release the video capture object.
  objr.get_cap().release()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  __main()