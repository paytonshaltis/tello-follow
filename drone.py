from djitellopy import tello
import numpy as np
import subprocess, cv2, threading, sys
from multiprocessing import Process
from object_detection import ObjectDetection
from ranges import RANGES

# Wi-Fi command for Windows vs. Mac.
WIN_WIFI = ['netsh', 'wlan', 'show', 'interfaces']
MAC_WIFI = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']

# Global variables needed by multiple functions.
drone = None
kill_stream = False
stream_thread_running = False
halt_program = False

# Display the stream from the drone. This function should be run in a seperate
# thread in order to allow for more commands to be sent to the drone.
def show_stream(drone):
  global stream_thread_running
  det_obj = ObjectDetection(None, RANGES['lime'])
  print(drone)

  # Continue showing the live feed until the user exits.
  while not kill_stream:
    # Get the next frame from the drone.
    img = drone.get_frame_read().frame

    # Process the frame.
    det_obj.process_frame(img)
    
    # Display the resulting frame (uncomment to display mask).
    # cv2.imshow('img', cv2.flip(mask, 1))
    cv2.imshow('img2', cv2.flip(img, 1))

    if(not stream_thread_running):
      stream_thread_running = True
    if cv2.waitKey(5) & 0xFF == 27:
      break
  stream_thread_running = False
  cv2.destroyAllWindows()

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

  # Begin displaying the stream in a seperate thread.
  drone.streamon()
  STREAM_THREAD = Process(target=show_stream, args=(drone,))
  STREAM_THREAD.start()

  # FIXME: need shared memory for this.
  # # Wait for the stream thread to begin displaying.
  # global stream_thread_running
  # while not stream_thread_running:
  #   pass

  # Begin the event loop for user commands.
  global halt_program
  while not halt_program:
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
          try: 
            drone.land()
          except:
            pass
          # FIXME: need shared memory for this.
          # global kill_stream 
          # kill_stream = True
          # STREAM_THREAD.join()
          drone.streamoff()
          halt_program = True
        case _:
          print("Unknown command.")
    except:
      print("There was an issue giving your command.")

if __name__ == "__main__":
  main()