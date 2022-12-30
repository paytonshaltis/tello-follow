from djitellopy import tello
import mediapipe as mp
import subprocess, cv2, threading

"""
Mediapipe face mesh constants.
"""
MP_FACE_MESH = mp.solutions.face_mesh
MP_DRAWING = mp.solutions.drawing_utils
MP_DRAWING_STYLES = mp.solutions.drawing_styles

drone = None
kill_stream = False
stream_thread_running = False
halt_program = False

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

def show_stream():
  """
  Begins streaming feed from drone to window. This should be called in a seperate
  thread in order to still allow for messages to be received and responded to
  by the main thread.
  """
  global stream_thread_running

  # Add the face mesh and display the live feed.
  # with suppress_stdout:
  with MP_FACE_MESH.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:
    
    # Continue showing the live feed until the user exits.
    while not kill_stream:
      cv2.imshow('MediaPipe Face Mesh', add_mp_face_mesh(face_mesh, drone.get_frame_read().frame))
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

  # Begin displaying the stream in a seperate thread.
  drone.streamon()
  STREAM_THREAD = threading.Thread(target=show_stream)
  STREAM_THREAD.start()

  # Wait for the stream thread to begin displaying.
  global stream_thread_running
  while not stream_thread_running:
    pass

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

        # Land the drone, end the stream, and kill the stream thread.
        case "stop" | "off" | "end" | "kill":
          try: 
            drone.land()
          except:
            pass
          global kill_stream 
          kill_stream = True
          STREAM_THREAD.join()
          drone.streamoff()
          halt_program = True
        case _:
          print("Unknown command.")
    except:
      print("There was an issue giving your command.")


if __name__ == "__main__":
  main()