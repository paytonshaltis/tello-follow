from djitellopy import tello
import subprocess, cv2, sys, time
from object_detection import ObjectDetection
from ranges import RANGES
from threading import Thread

# Wi-Fi command for Windows vs. Mac.
WIN_WIFI = ['netsh', 'wlan', 'show', 'interfaces']
MAC_WIFI = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']

# Global variables needed by multiple functions.
drone = None
kill_stream = False
kill_cmd_loop = False
stream_started = False

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
  speed = 10

  # Adjust the velocities based on the region.
  match region:
    case 1:
      left_right_velocity = -speed
      up_down_velocity = speed
      print("left and up")
    case 2:
      up_down_velocity = speed
      print("up")
    case 3:
      left_right_velocity = speed
      up_down_velocity = speed
      print("right and up")
    case 4:
      left_right_velocity = -speed
      print("left")
    case 5:
      pass
      print("center")
    case 6:
      left_right_velocity = speed
      print("right")
    case 7:
      left_right_velocity = -speed
      up_down_velocity = -speed
      print("left and down")
    case 8:
      up_down_velocity = -speed
      print("down")
    case 9:
      left_right_velocity = speed
      up_down_velocity = -speed
      print("right and down")
    case _:
      pass
      print("no object in sight.")

  # Send the command to the drone.
  drone.send_rc_control(left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity)

# Display the stream from the drone. This function should be run in a seperate
# thread in order to allow for more commands to be sent to the drone.
def show_stream(drone):
  det_obj = ObjectDetection(None, RANGES['pink'])

  global kill_stream, stream_started
  count = 0

  # Continue showing the live feed until the user exits.
  while not kill_stream:
    # Get the next frame from the drone.
    img = drone.get_frame_read().frame
    count += 1

    # Process the frame.
    img, region = det_obj.process_frame(img)

    # Adjust the drone's position based on the region.
    if count % 10 == 0:
      adjust_drone_position(drone, region)
    
    if not stream_started:
      stream_started = True
    
    # Display the resulting frame (uncomment to display mask).
    # cv2.imshow('img', cv2.flip(mask, 1))
    cv2.imshow('img2', cv2.flip(img, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break


def connect_to_drone() -> tello.Tello:
  """
  Connects to the drone and prints the battery level. Prints an error message if
  the drone cannot be connected to the program. Returns the drone object or .
  """
  try:
    global drone 
    drone = tello.Tello()
    drone.connect()
    print("Drone connected!")
    print("Battery: " + str(drone.get_battery()))
    return drone
  except:
    print("Error connecting to drone.")
    exit()

# Executes a command given by either the user or the object detection algorithm.
# A copy of this funciton should be run in a seperate thread in order to allow
# for more commands to be sent to the drone while streaming in the main thread.
def execute_command(drone):
  global kill_stream, kill_cmd_loop, stream_started

  # Wait for initial FFMpeg output to pass and stream to appear.
  while not stream_started:
    pass
  time.sleep(2)

  while not kill_cmd_loop:
    cmd = input("Enter drone command: ")
    try:
      match cmd:
        case "takeoff":
          drone.takeoff()
        case "land":
          drone.land()
        case "emergency":
          drone.emergency()
        case "stop" | "off" | "end" | "kill":
          kill_cmd_loop = True
          kill_stream = True
          drone.end()
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
  cmd_thread = Thread(target=execute_command, args=(drone,))
  cmd_thread.start()

  # Start streaming the drone's video feed. This will result in the main
  # thread entering an infinite render loop. Use 'esc' to exit.
  drone.streamon()
  show_stream(drone)
  cv2.destroyAllWindows()

  # Wait for the user to enter a command to stop the program.
  cmd_thread.join()

if __name__ == "__main__":
  main()