import cv2
import mediapipe as mp
import mediapipe.python.solutions.drawing_utils as drawing_utils
import mediapipe.python.solutions.pose as mp_pose

class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Definir os landmarks que queremos manter visíveis
        self.desired_landmarks_indices = [
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
            mp_pose.PoseLandmark.RIGHT_ELBOW.value,
            mp_pose.PoseLandmark.RIGHT_WRIST.value,
            mp_pose.PoseLandmark.LEFT_SHOULDER.value,
            mp_pose.PoseLandmark.LEFT_ELBOW.value,
            mp_pose.PoseLandmark.LEFT_WRIST.value,
            # Landmarks da mão (punho + principais pontos dos dedos no modelo de Pose)
            mp_pose.PoseLandmark.RIGHT_PINKY.value,
            mp_pose.PoseLandmark.RIGHT_INDEX.value,
            mp_pose.PoseLandmark.RIGHT_THUMB.value,
            mp_pose.PoseLandmark.LEFT_PINKY.value,
            mp_pose.PoseLandmark.LEFT_INDEX.value,
            mp_pose.PoseLandmark.LEFT_THUMB.value
        ]

        # Definir as especificações de desenho para os landmarks e conexões desejadas
        self.landmark_drawing_spec = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
        self.connection_drawing_spec = drawing_utils.DrawingSpec(color=(255, 255, 255), thickness=2)


    def process_frame(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        return results, image

    def draw_landmarks(self, image, results):
        if results.pose_landmarks:
            # Iterar sobre todos os landmarks e definir a visibilidade para 0 (invisível)
            # e mover suas coordenadas para (0,0) para aqueles que NÃO estão na nossa lista de desejados.
            # Isso modifica o objeto results.pose_landmarks diretamente antes de desenhar.
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                if i not in self.desired_landmarks_indices:
                    landmark.x = 0.0  # Mover para fora da tela
                    landmark.y = 0.0  # Mover para fora da tela
                    landmark.z = 0.0  # Mover para fora da tela
                    landmark.visibility = 0.0 # Tornar invisível para o desenho

            # Desenhar os landmarks.
            # O MediaPipe desenhará os pontos e as conexões APENAS se tiverem visibilidade suficiente.
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks, # Usamos o objeto original modificado aqui
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.landmark_drawing_spec,
                connection_drawing_spec=self.connection_drawing_spec
            )
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