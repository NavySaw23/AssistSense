"""
MediaPipe-based detector that produces an 11-element state array at a target rate.

Array layout (length 11):
 - index 0: eye state -> 1 = looking at screen, 0 = not looking, -1 = eyes not detected
 - indices 1..5: left hand fingers (1=pinky,2=ring,3=middle,4=index,5=thumb)
 - indices 6..10: right hand fingers (6=thumb,7=index,8=middle,9=ring,10=pinky)

Finger state values:
 -1 = finger not detected
  0 = finger closed
  1 = finger open

This module exposes `MediaPipeDetector` which can be started in a background thread
and will call a user callback at ~15 Hz with the latest state array.

Requirements: `mediapipe`, `opencv-python` (or `opencv-python-headless`).
"""
from __future__ import annotations

import os
import time
import threading
from typing import Callable, List, Optional

# Reduce noisy TensorFlow / MediaPipe logs. Set before importing mediapipe/cv2.
# 0 = all logs, 1 = INFO, 2 = WARNING, 3 = ERROR (higher value = fewer logs)
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
os.environ.setdefault('ABSL_CPP_MIN_LOG_LEVEL', '2')

# Import absl and set verbosity where available
try:
    import absl.logging as _absl_logging
    _absl_logging.set_verbosity(_absl_logging.ERROR)
except Exception:
    _absl_logging = None

import logging
logging.getLogger('absl').setLevel(logging.ERROR)
logging.getLogger('mediapipe').setLevel(logging.ERROR)
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import sys
import contextlib

# Some native libraries (TF / MediaPipe) emit log lines to stderr before Python-level
# logging settings or absl are initialized. Redirect stderr to devnull during imports
# to suppress those early startup messages.
_devnull = open(os.devnull, 'w')
with contextlib.redirect_stderr(_devnull):
    import cv2
    import mediapipe as mp
_devnull.close()


class MediaPipeDetector:
    def __init__(self, src: int = 0, fps: float = 15.0, debug: bool = False, print_to_console: bool = False, show_preview: bool = False):
        self.src = src
        self.fps = fps
        self.debug = debug
        self.print_to_console = print_to_console
        self.show_preview = show_preview

        # mediapipe utilities
        self.mp_face = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands

        # video capture
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)

        # controls
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callback: Optional[Callable[[List[int]], None]] = None

        # latest result
        # 11-element list
        self.latest: List[int] = [-1] * 11
        # whether mediapipe initialized correctly; if False we'll use an OpenCV fallback preview
        self._use_fallback = False

    def start(self, callback: Optional[Callable[[List[int]], None]] = None):
        """Start detection in a background thread. Callback receives the 11-element list."""
        self._callback = callback
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass

    def _run(self):
        target_dt = 1.0 / max(1.0, self.fps)

        # Try to create FaceMesh and Hands. If creation fails (DLL/import issues),
        # fall back to a simple OpenCV preview so the user still sees camera output.
        face_mesh = None
        hands = None
        try:
            _old_stderr = sys.stderr
            _devnull_local = open(os.devnull, 'w')
            try:
                sys.stderr = _devnull_local
                face_mesh = self.mp_face.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
            finally:
                try:
                    _devnull_local.close()
                except Exception:
                    pass
                sys.stderr = _old_stderr
        except Exception as e:
            # mark fallback mode and report error once
            print(f"MediaPipe initialization failed, using OpenCV fallback preview: {e}")
            self._use_fallback = True

        # Main loop: either use MediaPipe if available, or an OpenCV-only preview fallback
        while not self._stop_event.is_set():
            t0 = time.time()
            ok, frame = self.cap.read()
            if not ok or frame is None:
                # camera read failed; sleep then continue
                time.sleep(target_dt)
                continue

            # If using fallback, just show the raw camera and emit a default "no-detection" array
            if self._use_fallback:
                vis = frame.copy()
                cv2.putText(vis, "MediaPipe unavailable - preview", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('mp_preview', vis)
                if self.print_to_console:
                    print(f"{time.strftime('%H:%M:%S')} - {self.latest}")
                if cv2.waitKey(1) & 0xFF == 27:
                    self._stop_event.set()
                    break
                dt = time.time() - t0
                to_sleep = max(0.0, target_dt - dt)
                time.sleep(to_sleep)
                continue

            # flip to be mirror-like (optional)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape

            # default states: -1 for not detected
            arr = [-1] * 11

            # --- face / eye estimation ---
            face_res = face_mesh.process(frame_rgb)
            if not face_res.multi_face_landmarks:
                arr[0] = -1
            else:
                # compute eye-centers (simple heuristic) and decide if looking
                lm = face_res.multi_face_landmarks[0].landmark

                # landmarks lists for left / right eye corners (approximate)
                left_eye_idxs = [33, 133, 160, 159, 158, 157, 173]
                right_eye_idxs = [362, 263, 387, 386, 385, 384, 398]

                def avg_point(idxs):
                    xs = [lm[i].x * w for i in idxs if i < len(lm)]
                    ys = [lm[i].y * h for i in idxs if i < len(lm)]
                    if not xs or not ys:
                        return None
                    return (sum(xs) / len(xs), sum(ys) / len(ys))

                left_center = avg_point(left_eye_idxs)
                right_center = avg_point(right_eye_idxs)

                if left_center and right_center:
                    eye_mid_x = (left_center[0] + right_center[0]) / 2.0
                    frame_cx = w / 2.0
                    # if midpoint is near center (within 25% of width) -> looking
                    tol = 0.25 * w
                    if abs(eye_mid_x - frame_cx) <= tol:
                        arr[0] = 1
                    else:
                        arr[0] = 0
                else:
                    arr[0] = -1

            # --- hand / finger estimation ---
            hand_res = hands.process(frame_rgb)

            # initialize fingers as -1 (not detected)
            for i in range(1, 11):
                arr[i] = -1

            if hand_res.multi_hand_landmarks and hand_res.multi_handedness:
                for hand_landmarks, handedness in zip(
                    hand_res.multi_hand_landmarks, hand_res.multi_handedness
                ):
                    label = handedness.classification[0].label  # 'Left' or 'Right'
                    lm = hand_landmarks.landmark

                    # helper to read normalized coords
                    def xy(i):
                        return (lm[i].x * w, lm[i].y * h)

                    # finger tip and pip indices
                    tips = {
                        'thumb': 4,
                        'index': 8,
                        'middle': 12,
                        'ring': 16,
                        'pinky': 20,
                    }
                    pips = {
                        'index': 6,
                        'middle': 10,
                        'ring': 14,
                        'pinky': 18,
                    }

                    # compute states for each finger
                    states = {}

                    # non-thumb fingers: compare tip.y and pip.y (image origin at top)
                    for name in ('index', 'middle', 'ring', 'pinky'):
                        tip = lm[tips[name]]
                        pip = lm[pips[name]]
                        # if landmarks present
                        if tip and pip:
                            # open if tip is above pip (smaller y)
                            states[name] = 1 if (tip.y * h) < (pip.y * h) else 0
                        else:
                            states[name] = -1

                    # thumb: compare x depending on handedness
                    thumb_tip = lm[tips['thumb']]
                    thumb_ip = lm[3]
                    if thumb_tip and thumb_ip:
                        if label == 'Right':
                            # right hand thumb open when tip.x < ip.x (points left)
                            states['thumb'] = 1 if (thumb_tip.x * w) < (thumb_ip.x * w) else 0
                        else:
                            # left hand thumb open when tip.x > ip.x (points right)
                            states['thumb'] = 1 if (thumb_tip.x * w) > (thumb_ip.x * w) else 0
                    else:
                        states['thumb'] = -1

                    # place states into arr according to mapping
                    if label == 'Left':
                        # left pinky -> arr[1], left ring -> arr[2], left middle -> arr[3], left index -> arr[4], left thumb -> arr[5]
                        arr[1] = states.get('pinky', -1)
                        arr[2] = states.get('ring', -1)
                        arr[3] = states.get('middle', -1)
                        arr[4] = states.get('index', -1)
                        arr[5] = states.get('thumb', -1)
                    else:
                        # right mapping: arr[6]=thumb,7=index,8=middle,9=ring,10=pinky
                        arr[6] = states.get('thumb', -1)
                        arr[7] = states.get('index', -1)
                        arr[8] = states.get('middle', -1)
                        arr[9] = states.get('ring', -1)
                        arr[10] = states.get('pinky', -1)

            # store latest and call callback
            self.latest = arr
            if self._callback:
                try:
                    self._callback(list(arr))
                except Exception:
                    pass

            if self.print_to_console:
                # include a timestamp for easier reading
                print(f"{time.strftime('%H:%M:%S')} - {arr}")

            # optionally show a debug preview window with landmarks
            if self.show_preview or self.debug:
                vis = frame.copy()
                try:
                    # draw face landmarks if available
                    if face_res and getattr(face_res, 'multi_face_landmarks', None):
                        for flm in face_res.multi_face_landmarks:
                            try:
                                mp.solutions.drawing_utils.draw_landmarks(
                                    vis,
                                    flm,
                                    mp.solutions.face_mesh.FACEMESH_TESSELATION,
                                )
                            except Exception:
                                # fallback to generic face connections
                                mp.solutions.drawing_utils.draw_landmarks(
                                    vis,
                                    flm,
                                    mp.solutions.face_mesh.FACE_CONNECTIONS,
                                )

                    # draw hand landmarks if available
                    if hand_res and getattr(hand_res, 'multi_hand_landmarks', None):
                        for hlm in hand_res.multi_hand_landmarks:
                            mp.solutions.drawing_utils.draw_landmarks(
                                vis,
                                hlm,
                                mp.solutions.hands.HAND_CONNECTIONS,
                            )
                except Exception:
                    # drawing can fail on some platforms; ignore errors
                    pass

                cv2.putText(vis, str(arr), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.imshow('mp_preview', vis)
                if cv2.waitKey(1) & 0xFF == 27:
                    self._stop_event.set()

            # maintain target fps
            dt = time.time() - t0
            to_sleep = max(0.0, target_dt - dt)
            time.sleep(to_sleep)

        # clean up mediapipe contexts
        try:
            if 'face_mesh' in locals() and face_mesh:
                try:
                    face_mesh.close()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if 'hands' in locals() and hands:
                try:
                    hands.close()
                except Exception:
                    pass
        except Exception:
            pass

        if self.debug:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    # simple demo: run detector standalone and show console output + preview
    import traceback

    det = None
    try:
        det = MediaPipeDetector(src=0, fps=15.0, debug=False, print_to_console=True, show_preview=True)
        det.start()
        print('Running detector - press Ctrl+C to stop')
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print('Stopping')
    except Exception:
        print('Failed to run MediaPipeDetector standalone:')
        traceback.print_exc()
        # keep process alive briefly so user can read the error
        try:
            time.sleep(2.0)
        except Exception:
            pass
    finally:
        try:
            if det:
                det.stop()
        except Exception:
            pass
