from djitellopy import tello
import subprocess

def connect_to_drone() -> tello.Tello:
  """
  Connects to the drone and prints the battery level. Prints an error message if
  the drone cannot be connected to the program. Returns the drone object or .
  """
  try:
    drone = tello.Tello()
    drone.connect()
    print("Drone connected!")
    print("Battery: " + str(drone.get_battery()))
    return drone
  except:
    print("Error connecting to drone.")
    exit()

def main() -> None:
  """
  Drone program main function. Includes the main loop of the program for object
  or face detection, drone adjustement, and drone movement.
  """

  # Connect to drone only if on the correct network.
  print("Checking for connection to drone network...")
  if subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces']).decode('utf-8').find("TELLO-") != -1:
    print("Connected to drone network!")
    drone = connect_to_drone()
  else:
    print("Error: not connected to drone network!")
    exit()

if __name__ == "__main__":
  main()