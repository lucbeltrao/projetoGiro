import cv2
import mediapipe as mp

class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        return results, image

    def draw_landmarks(self, image, results):
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return image

    def get_arm_landmarks(self, results, arm_side='right'):
        landmarks = {}
        if results.pose_landmarks:
            if arm_side == 'right':
                landmarks['shoulder'] = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                                         results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
                landmarks['elbow'] = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW].x,
                                      results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW].y]
                landmarks['wrist'] = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].x,
                                       results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].y]
            elif arm_side == 'left':
                landmarks['shoulder'] = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                                         results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y]
                landmarks['elbow'] = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ELBOW].x,
                                      results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ELBOW].y]
                landmarks['wrist'] = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST].x,
                                       results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST].y]
        return landmarks