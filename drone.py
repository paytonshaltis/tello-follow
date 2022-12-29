from djitellopy import tello
import mediapipe as mp
import subprocess, cv2

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

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

  # Begin the event loop for user commands.
  while True:
    cmd = input("Enter drone command: ")
    
    match cmd:
      case "takeoff":
        drone.takeoff()
      case "land":
        drone.land()
      case "streamon":
        drone.streamon()
        with mp_face_mesh.FaceMesh(
          max_num_faces=1,
          refine_landmarks=True,
          min_detection_confidence=0.5,
          min_tracking_confidence=0.5) as face_mesh:
          while True:
            image = drone.get_frame_read().frame

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image)

            # Draw the face mesh annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_face_landmarks:
              for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_tesselation_style())
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_contours_style())
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_iris_connections_style())

            # Display the image.
            cv2.imshow('MediaPipe Face Mesh', image)
            if cv2.waitKey(5) & 0xFF == 27:
              break

if __name__ == "__main__":
  main()