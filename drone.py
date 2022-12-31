"""
Payton Shaltis
12/31/2022

Script for sending basic commands to a Tello drone. The script, in its main
thread, will display the video feed from the drone, modifying each frame using
the ObjectDetection class. The script will also create a second thread for
sending commands to the drone. Commands implemented include:
  - 'takeoff': Takes off the drone.
  - 'land': Lands the drone.
  - 'autofollow start': Enables auto-follow mode for the color range specified.
  - 'autofollow stop': Disables auto-follow mode.
  - 'emergency': Stops all motors immediately.
  - 'kill': Lands the drone, stops the video stream, and exits the program. 
"""

from djitellopy import tello
from object_detection import ObjectDetection
from ranges import RANGES
from threading import Thread
import subprocess, cv2, sys, time

# Constant values used by the program.
WIN_WIFI = ['netsh', 'wlan', 'show', 'interfaces']
MAC_WIFI = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']
SPEED = 25

# Global variables needed by multiple functions.
drone = None
kill_stream = False
kill_cmd_loop = False
stream_started = False
auto_follow = False

# Adjusts the drone's position based on the region the object is in. The drone
# will move up, down, left, and right to try and center the object in the frame.
# The velocities will be set for each direction, and set to 0 if the object
# is already in the center of the frame.
def adjust_drone_position(drone, region):
  # Velocities to be modified based on the region.
  left_right_velocity = 0
  up_down_velocity = 0
  forward_backward_velocity = 0
  yaw_velocity = 0

  # Adjust the velocities based on the region.
  result = ""
  match region:
    case 1:
      left_right_velocity = -SPEED
      up_down_velocity = SPEED
      result = "left and up"
    case 2:
      up_down_velocity = SPEED
      result = "up"
    case 3: 
      left_right_velocity = SPEED
      up_down_velocity = SPEED
      result = "right and up"
    case 4:
      left_right_velocity = -SPEED
      result = "left"
    case 5:
      result = "object centered"
      pass
    case 6:
      left_right_velocity = SPEED
      result = "right"
    case 7:
      left_right_velocity = -SPEED
      up_down_velocity = -SPEED
      result = "left and down"
    case 8:
      up_down_velocity = -SPEED
      result = "down"
    case 9:
      left_right_velocity = SPEED
      up_down_velocity = -SPEED
      result = "right and down"
    case _:
      result = "object not found"
      pass

  # Send the command to the drone.
  drone.send_rc_control(left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity)

  # Print the direction the drone is moving in.
  return result

# Display the stream from the drone. This function should be run in a seperate
# thread in order to allow for more commands to be sent to the drone.
def show_stream(drone):
  det_obj = ObjectDetection(RANGES['lime'])
  global kill_stream, stream_started, auto_follow
  prev_direction = ""

  # Continue showing the live feed until the user exits.
  while not kill_stream:
    # Get and process the next frame from the drone.
    img, region = det_obj.process_frame(drone.get_frame_read().frame)

    # Adjust the drone's position if auto_follow is enabled.
    if auto_follow:
      direction = adjust_drone_position(drone, region)
      # Print out the direction that the drone is moving; avoid duplicate prints.
      if prev_direction != direction:
        if direction == "object centered":
          print("Auto Move: Object centered")
        elif direction == "object not found":
          print("Auto Move: Object not found")
        else:
          print(f'Auto Move: Moving {direction}')
        prev_direction = direction
    
    # Display the resulting frame (uncomment to display mask).
    # cv2.imshow('img', cv2.flip(mask, 1))
    stream_started = True
    cv2.imshow('img2', cv2.flip(img, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
  cv2.destroyAllWindows()


# Connects to the drone and prints the battery level. Prints an error message if
# the drone cannot be connected to the program. Returns the drone object or .
def connect_to_drone() -> tello.Tello:
  try:
    global drone 
    drone = tello.Tello()
    drone.connect()
    return drone
  except:
    print("Error connecting to drone.")
    exit()

# Executes a command given by either the user or the object detection algorithm.
# A copy of this funciton should be run in a seperate thread in order to allow
# for more commands to be sent to the drone while streaming in the main thread.
def thread_worker_commands(drone):
  global kill_stream, kill_cmd_loop, stream_started, auto_follow

  # Wait for initial FFMpeg output to pass and stream to appear.
  while not stream_started:
    pass
  time.sleep(2)

  print("Drone connected!")
  print("Battery: " + str(drone.get_battery()))

  # Continue taking commands until the user sends a stop command.
  while not kill_cmd_loop:
    cmd = input("Enter drone command: ")
    try:
      match cmd:
        case "takeoff":
          drone.takeoff()
        case "land":
          drone.land()
        case "autofollow start":
          auto_follow = True
        case "autofollow stop":
          auto_follow = False
        case "emergency":
          drone.emergency()
        case "kill":
          kill_cmd_loop = True
          kill_stream = True
        case _:
          print("Unknown command.")
    except:
      print("There was an issue giving your command.")

# Entry point of the program.
def main() -> None:

  # Connect to drone only if on the correct network.
  global drone
  if len(sys.argv) < 2 or not sys.argv[1] == "mac" and not sys.argv[1] == "windows":
    print("Error: invalid argument for OS: 'python drone.py [mac | windows]''")
    exit()
  print("Checking for connection to drone network...")
  if sys.argv[1] == "mac":
    if subprocess.check_output(MAC_WIFI).decode('utf-8').find("TELLO-") != -1:
      print("Connected to drone network!")
      drone = connect_to_drone()
    else:
      print("Error: not connected to drone network!")
      exit()
  elif sys.argv[1] == "windows":
    if subprocess.check_output(WIN_WIFI).decode('utf-8').find("TELLO-") != -1:
      print("Connected to drone network!")
      drone = connect_to_drone()
    else:
      print("Error: not connected to drone network!")
      exit()

  # Begin the thread for entering additional drone commands.
  cmd_thread = Thread(target=thread_worker_commands, args=(drone,))
  cmd_thread.start()

  # Start streaming the drone's video feed. This will result in the main
  # thread entering an infinite render loop. Use 'esc' to exit.
  drone.streamon()
  show_stream(drone)
  cv2.destroyAllWindows()

  # Wait for the user to enter a command to stop the program.
  cmd_thread.join()
  print("Disconnecting from drone...")
  drone.end()
  print("Exited normally.")
  
if __name__ == "__main__":
  main()