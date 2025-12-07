import cv2
import mediapipe as mp
import numpy as np
import threading
import time

class GazeEngine:
    def __init__(self, camera_number=1):
        """
        Initializes the GazeEngine to run in a background thread.
        """
        self.camera_number = camera_number
        self.video_capture = cv2.VideoCapture(self.camera_number)

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        self.gazeStatus = -1  # -1: not detected, 0: not looking, 1: looking
        
        self._running = False
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _get_gaze_ratios(self, frame):
        """
        Calculates horizontal and vertical gaze ratios from a frame.
        """
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame.flags.writeable = False
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        frame.flags.writeable = True

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        
        LEFT_IRIS = [474, 475, 476, 477]
        RIGHT_IRIS = [469, 470, 471, 472]
        LEFT_EYE_CORNERS = [362, 263]
        RIGHT_EYE_CORNERS = [133, 33]

        frame_h, frame_w, _ = frame.shape

        left_iris_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in LEFT_IRIS])
        right_iris_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in RIGHT_IRIS])
        left_iris_center = left_iris_points.mean(axis=0).astype(np.int32)
        right_iris_center = right_iris_points.mean(axis=0).astype(np.int32)

        left_eye_corner_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in LEFT_EYE_CORNERS])
        right_eye_corner_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in RIGHT_EYE_CORNERS])

        left_eye_width = np.linalg.norm(left_eye_corner_points[0] - left_eye_corner_points[1])
        left_gaze_ratio = (left_eye_corner_points[0][0] - left_iris_center[0]) / left_eye_width if left_eye_width > 0 else 0.5
        
        right_eye_width = np.linalg.norm(right_eye_corner_points[0] - right_eye_corner_points[1])
        right_gaze_ratio = (right_eye_corner_points[0][0] - right_iris_center[0]) / right_eye_width if right_eye_width > 0 else 0.5
        
        avg_gaze_ratio_h = (left_gaze_ratio + right_gaze_ratio) / 2

        top_left_eye = landmarks[386]
        bottom_left_eye = landmarks[374]
        top_right_eye = landmarks[159]
        bottom_right_eye = landmarks[145]

        left_eye_height = np.linalg.norm(np.array([top_left_eye.x, top_left_eye.y]) - np.array([bottom_left_eye.x, bottom_left_eye.y])) * frame_h
        left_gaze_ratio_v = (top_left_eye.y * frame_h - left_iris_center[1]) / left_eye_height if left_eye_height > 0 else 0.5
        
        right_eye_height = np.linalg.norm(np.array([top_right_eye.x, top_right_eye.y]) - np.array([bottom_right_eye.x, bottom_right_eye.y])) * frame_h
        right_gaze_ratio_v = (top_right_eye.y * frame_h - right_iris_center[1]) / right_eye_height if right_eye_height > 0 else 0.5

        avg_gaze_ratio_v = (left_gaze_ratio_v + right_gaze_ratio_v) / 2
        return avg_gaze_ratio_h, avg_gaze_ratio_v

    def _update_gaze_status(self, frame):
        """
        Determines the gaze status and updates self.gazeStatus.
        - 1 for Looking At Screen
        - 0 for Looking Away
        - -1 for No Face Detected
        """
        ratios = self._get_gaze_ratios(frame)
        if ratios is None:
            self.gazeStatus = -1  # No Face Detected
            return
        
        avg_gaze_ratio_h, avg_gaze_ratio_v = ratios

        # Calibrated thresholds
        h_min_ratio = 0.00
        h_max_ratio = 0.10
        v_min_ratio = -0.40
        v_max_ratio = -0.20

        if (h_min_ratio <= avg_gaze_ratio_h <= h_max_ratio) and \
           (v_min_ratio <= avg_gaze_ratio_v <= v_max_ratio):
            self.gazeStatus = 1  # Looking At Screen
        else:
            self.gazeStatus = 0  # Looking Away

    def _run(self):
        """
        Main loop for the background thread.
        """
        while self._running:
            if not self.video_capture.isOpened():
                self.gazeStatus = -1
                print("Error: Cannot open camera. Retrying in 1s...")
                time.sleep(1)
                # Try to reconnect
                self.video_capture.release()
                self.video_capture.open(self.camera_number)
                continue

            ret, frame = self.video_capture.read()
            if not ret:
                self.gazeStatus = -1
                time.sleep(0.1) # Avoid busy-waiting
                continue
            
            self._update_gaze_status(frame)
    
    def start(self):
        """
        Starts the gaze detection thread.
        """
        if self._running:
            return
        self._running = True
        self.thread.start()

    def stop(self):
        """
        Stops the gaze detection thread.
        """
        if not self._running:
            return
        self._running = False
        # The thread is a daemon, so we don't need to join it.
        # It will exit when the main program exits.
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.face_mesh.close()