import cv2
import mediapipe as mp
import numpy as np
import time

# Final Status Array Indices:
# Indices 0-9: Finger Status (L-Pinky to R-Pinky)
# Index 10: Gaze Status
# [P(L), R(L), M(L), I(L), T(L), T(R), I(R), M(R), R(R), P(R), Gaze]

class MultiEngine:
    """
    Combines hand gesture detection and gaze detection in a single thread 
    to prevent camera access conflicts.
    """
    def __init__(self, camera_index=1):
        self.camera_index = camera_index
        
        # --- Camera Setup (Only one capture object) ---
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
             print(f"Error: Cannot open camera with index {camera_index}.")
        
        # --- MediaPipe Hand Setup ---
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        
        # --- MediaPipe FaceMesh Setup (for Gaze) ---
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # --- Status Array (11 elements) ---
        self.multi_status = [-1] * 11 

    # ====================================================================
    # --- HAND GESTURE DETECTION METHODS ---
    # ====================================================================

    def _update_finger_status(self, hand_landmarks, hand_label):
        """
        Updates the first 10 elements of the multi_status array.
        """
        tip_ids = [4, 8, 12, 16, 20]
        landmarks = hand_landmarks.landmark

        # Left Hand (Indices 0-4: Pinky, Ring, Middle, Index, Thumb)
        if hand_label == "Left":
            # Thumb (index 4)
            # 1 = Open, 0 = Closed
            self.multi_status[4] = 1 if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x else 0
            
            # Other 4 fingers (indices 0, 1, 2, 3: Pinky, Ring, Middle, Index)
            for i in range(1, 5):
                # 1 = Open (tip above knuckle), 0 = Closed
                self.multi_status[4-i] = 1 if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y else 0

        # Right Hand (Indices 5-9: Thumb, Index, Middle, Ring, Pinky)
        elif hand_label == "Right":
            # Thumb (index 5)
            # 1 = Open, 0 = Closed
            self.multi_status[5] = 1 if landmarks[tip_ids[0]].x > landmarks[tip_ids[0] - 1].x else 0

            # Other 4 fingers (indices 6-9: Index, Middle, Ring, Pinky)
            for i in range(1, 5):
                # 1 = Open (tip above knuckle), 0 = Closed
                self.multi_status[5+i] = 1 if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y else 0


    # ====================================================================
    # --- GAZE DETECTION METHODS ---
    # ====================================================================

    def _get_gaze_ratios(self, frame, frame_w, frame_h):
        """
        Calculates horizontal and vertical gaze ratios from a frame.
        """
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
        TOP_LEFT_EYE = 386 
        BOTTOM_LEFT_EYE = 374
        TOP_RIGHT_EYE = 159
        BOTTOM_RIGHT_EYE = 145

        # Horizontal Gaze Ratios
        left_iris_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in LEFT_IRIS])
        left_iris_center = left_iris_points.mean(axis=0).astype(np.int32)
        left_eye_corner_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in LEFT_EYE_CORNERS])
        left_eye_width = np.linalg.norm(left_eye_corner_points[0] - left_eye_corner_points[1])
        left_gaze_ratio_h = (left_eye_corner_points[0][0] - left_iris_center[0]) / left_eye_width if left_eye_width > 0 else 0.5

        right_iris_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in RIGHT_IRIS])
        right_iris_center = right_iris_points.mean(axis=0).astype(np.int32)
        right_eye_corner_points = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) for i in RIGHT_EYE_CORNERS])
        right_eye_width = np.linalg.norm(right_eye_corner_points[0] - right_eye_corner_points[1])
        right_gaze_ratio_h = (right_eye_corner_points[0][0] - right_iris_center[0]) / right_eye_width if right_eye_width > 0 else 0.5
        
        avg_gaze_ratio_h = (left_gaze_ratio_h + right_gaze_ratio_h) / 2

        # Vertical Gaze Ratios
        top_left_eye = landmarks[TOP_LEFT_EYE]
        bottom_left_eye = landmarks[BOTTOM_LEFT_EYE]
        left_eye_height = np.linalg.norm(np.array([top_left_eye.x, top_left_eye.y]) - np.array([bottom_left_eye.x, bottom_left_eye.y])) * frame_h
        left_gaze_ratio_v = (top_left_eye.y * frame_h - left_iris_center[1]) / left_eye_height if left_eye_height > 0 else 0.5
        
        top_right_eye = landmarks[TOP_RIGHT_EYE]
        bottom_right_eye = landmarks[BOTTOM_RIGHT_EYE]
        right_eye_height = np.linalg.norm(np.array([top_right_eye.x, top_right_eye.y]) - np.array([bottom_right_eye.x, bottom_right_eye.y])) * frame_h
        right_gaze_ratio_v = (top_right_eye.y * frame_h - right_iris_center[1]) / right_eye_height if right_eye_height > 0 else 0.5

        avg_gaze_ratio_v = (left_gaze_ratio_v + right_gaze_ratio_v) / 2
        return avg_gaze_ratio_h, avg_gaze_ratio_v


    def _update_gaze_status(self, frame):
        """
        Determines the gaze status and updates the 10th index of multi_status.
        """
        frame_h, frame_w, _ = frame.shape
        ratios = self._get_gaze_ratios(frame, frame_w, frame_h)
        
        current_gaze_status = -1
        
        if ratios is None:
            current_gaze_status = -1  # No Face Detected
        else:
            avg_gaze_ratio_h, avg_gaze_ratio_v = ratios

            # Calibrated thresholds
            h_min_ratio = 0.00
            h_max_ratio = 0.10
            v_min_ratio = -0.40
            v_max_ratio = -0.20

            if (h_min_ratio <= avg_gaze_ratio_h <= h_max_ratio) and \
               (v_min_ratio <= avg_gaze_ratio_v <= v_max_ratio):
                current_gaze_status = 1  # Looking At Screen
            else:
                current_gaze_status = 0  # Looking Away

        self.multi_status[10] = current_gaze_status

    # ====================================================================
    # --- MAIN PROCESSING METHOD ---
    # ====================================================================

    def process_frame(self):
        """
        Reads a frame, processes both hands and gaze sequentially, and returns the frame image.
        """
        success, img = self.cap.read()
        if not success:
            # Check if the camera was disconnected
            if not self.cap.isOpened():
                print("Camera feed lost or unavailable.")
                return None
            time.sleep(0.01)
            return None # Skip this frame if read failed temporarily

        # 1. Reset status array (only fingers 0-9)
        for i in range(10):
            self.multi_status[i] = -1
        
        # 2. Hand Gesture Detection
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(img_rgb)

        if hand_results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
                hand_label = handedness.classification[0].label
                self._update_finger_status(hand_landmarks, hand_label)
                # Draw landmarks only if the module is run as __main__
                if __name__ == '__main__':
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
        # 3. Gaze Detection
        # Pass the frame to the gaze detector
        self._update_gaze_status(img) 
        
        return img

    def get_multi_status(self):
        """
        Returns the current 11-element status array.
        """
        return self.multi_status[:] # Return a copy

    def __del__(self):
        """
        Releases all resources.
        """
        if self.cap.isOpened():
            self.cap.release()
        self.hands.close()
        self.face_mesh.close()
        # Only destroy windows if the module was run as main
        if __name__ == '__main__':
            cv2.destroyAllWindows()


# ====================================================================
# --- MAIN EXECUTION BLOCK (Conditional Display) ---
# ====================================================================

if __name__ == '__main__':
    # This block executes ONLY when the script is run directly (e.g., python your_script.py)
    
    CAMERA_INDEX = 1 
    
    engine = MultiEngine(camera_index=CAMERA_INDEX)
    print(f"MultiEngine running on camera index {CAMERA_INDEX}. Displaying live feed.")

    # Initialize CV2 window
    cv2.namedWindow("Live Feed", cv2.WINDOW_AUTOSIZE)

    while True:
        # Process frame (Hands and Gaze)
        img = engine.process_frame()
        
        if img is not None:
            # Display the frame - only executed inside this __main__ block
            cv2.imshow("Live Feed", img)
            
            # Print the combined status to the console
            current_status = engine.get_multi_status()
            print(f"Status (11-elem): {current_status}")

        # Break loop on 'q' press or if the camera stops
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # Explicit check for camera status to exit cleanly if disconnected
        if not engine.cap.isOpened() and img is None:
             break
        
        time.sleep(0.001) # Small delay to yield CPU time

    # Cleanup upon exit
    del engine
    print("Engine stopped and resources released.")

