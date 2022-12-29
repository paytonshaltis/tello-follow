from djitellopy import tello


def connect_to_drone() -> tello.Tello:
  """
  Connects to the drone and prints the battery level. Prints an error message if
  the drone cannot be connected to the program. Returns the drone object or .
  """

  drone = tello.Tello()
  if drone.connect():
    print("Drone connected!")
    print("Battery: " + str(drone.get_battery()))
    return drone
  else:
    print("Error connecting to drone!")
    exit()

def main() -> None:
  """
  Drone program main function. Includes the main loop of the program for object
  or face detection, drone adjustement, and drone movement.
  """

  print("")
  drone = connect_to_drone()

if __name__ == "__main__":
  main()