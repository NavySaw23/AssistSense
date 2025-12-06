import cv2
import mediapipe as mp

fingerDebug = True

class GestureEngine:
    def __init__(self, camera_index=0):
        """
        Initializes the GestureEngine.

        Args:
            camera_index (int): The index of the camera to use.
        """
        self.cap = cv2.VideoCapture(camera_index)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

        # pinky(L), ring(L), middle(L), index(L), thumb(L), thumb(R), index(R), middle(R), ring(R), pinky(R)
        self.fingerStatus = [-1] * 10

    def process_frame(self):
        """
        Processes a single frame from the camera to detect hand gestures.
        """
        success, img = self.cap.read()
        if not success:
            return None

        # Reset finger status to -1 (not detected) for this frame
        self.fingerStatus = [-1] * 10

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = handedness.classification[0].label
                self._update_finger_status(hand_landmarks, hand_label)
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        return img

    def _update_finger_status(self, hand_landmarks, hand_label):
        """
        Updates the fingerStatus array based on the detected hand landmarks.
        """
        tip_ids = [4, 8, 12, 16, 20]
        landmarks = hand_landmarks.landmark

        # Left Hand
        if hand_label == "Left":
            # Thumb
            if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
                self.fingerStatus[4] = 0  # Open
            else:
                self.fingerStatus[4] = 1  # Closed
            
            # Other 4 fingers
            for i in range(1, 5):
                if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y:
                    self.fingerStatus[4-i] = 1 # Open
                else:
                    self.fingerStatus[4-i] = 0 # Closed

        # Right Hand
        if hand_label == "Right":
            # Thumb
            if landmarks[tip_ids[0]].x > landmarks[tip_ids[0] - 1].x:
                self.fingerStatus[5] = 0  # Open
            else:
                self.fingerStatus[5] = 1  # Closed

            # Other 4 fingers
            for i in range(1, 5):
                if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y:
                    self.fingerStatus[5+i] = 1 # Open
                else:
                    self.fingerStatus[5+i] = 0 # Closed


    def get_finger_status(self):
        """
        Returns the current status of the fingers.
        """
        return self.fingerStatus

    def __del__(self):
        """
        Releases the camera capture.
        """
        self.cap.release()

if __name__ == '__main__':
    engine = GestureEngine()
    while True:
        img = engine.process_frame()
        if img is not None:
            # cv2.imshow("Gesture Recognition", img)
            if fingerDebug:
                print("Finger Status:", engine.get_finger_status())

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # cv2.destroyAllWindows()
