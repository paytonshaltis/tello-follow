from djitellopy import tello
import mediapipe as mp
import subprocess, cv2

"""
Mediapipe face mesh constants.
"""
MP_FACE_MESH = mp.solutions.face_mesh
MP_DRAWING = mp.solutions.drawing_utils
MP_DRAWING_STYLES = mp.solutions.drawing_styles

def add_mp_face_mesh(face_mesh_params, image):
  """
  Modifies the passed image and returns a new one. This image is modified with
  the mediapipe face mesh overlay for detecting facial features. Also requires
  the tuple of face mesh params.
  """
  # To improve performance, optionally mark the image as not writeable to
  # pass by reference.
  image.flags.writeable = False
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  results = face_mesh_params.process(image)

  # Draw the face mesh annotations on the image.
  image.flags.writeable = True
  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  if results.multi_face_landmarks:
    for face_landmarks in results.multi_face_landmarks:
      MP_DRAWING.draw_landmarks(
          image=image,
          landmark_list=face_landmarks,
          connections=MP_FACE_MESH.FACEMESH_TESSELATION,
          landmark_drawing_spec=None,
          connection_drawing_spec=MP_DRAWING_STYLES
          .get_default_face_mesh_tesselation_style())
      MP_DRAWING.draw_landmarks(
          image=image,
          landmark_list=face_landmarks,
          connections=MP_FACE_MESH.FACEMESH_CONTOURS,
          landmark_drawing_spec=None,
          connection_drawing_spec=MP_DRAWING_STYLES
          .get_default_face_mesh_contours_style())
      MP_DRAWING.draw_landmarks(
          image=image,
          landmark_list=face_landmarks,
          connections=MP_FACE_MESH.FACEMESH_IRISES,
          landmark_drawing_spec=None,
          connection_drawing_spec=MP_DRAWING_STYLES
          .get_default_face_mesh_iris_connections_style())

  # Return the modified image.
  return image


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

        # Add the face mesh and display the live feed.
        with MP_FACE_MESH.FaceMesh(
          max_num_faces=1,
          refine_landmarks=True,
          min_detection_confidence=0.5,
          min_tracking_confidence=0.5) as face_mesh:
          
          # Continue showing the live feed until the user exits.
          while True:
            cv2.imshow('MediaPipe Face Mesh', add_mp_face_mesh(face_mesh, drone.get_frame_read().frame))
            if cv2.waitKey(5) & 0xFF == 27:
              break

if __name__ == "__main__":
  main()