import cv2
import numpy as np # Importar numpy
from utils.angle_calculator import calculate_angle
from utils.pose_estimator import PoseEstimator
from config.settings import TARGET_ARM, FLEXED_ANGLE_THRESHOLD_DEFAULT, EXTENDED_ANGLE_THRESHOLD_DEFAULT, CALIBRATION_REPS # Importar configurações

def main():
    cap = cv2.VideoCapture(0)
    pose_estimator = PoseEstimator()

    reps = 0
    stage = None

    # Variáveis para calibração
    calibrating = True
    calibration_angles_min = []
    calibration_angles_max = []
    calibration_stage = "estendido"
    calibration_reps_done = 0

    flexed_angle_threshold = FLEXED_ANGLE_THRESHOLD_DEFAULT
    extended_angle_threshold = EXTENDED_ANGLE_THRESHOLD_DEFAULT

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results, annotated_frame = pose_estimator.process_frame(frame)
        annotated_frame = pose_estimator.draw_landmarks(annotated_frame, results)

        landmarks = pose_estimator.get_arm_landmarks(results, arm_side=TARGET_ARM)

        if all(k in landmarks for k in ('shoulder', 'elbow', 'wrist')):
            shoulder = landmarks['shoulder']
            elbow = landmarks['elbow']
            wrist = landmarks['wrist']

            angle = calculate_angle(shoulder, elbow, wrist)

            if calibrating:
                cv2.putText(annotated_frame, f'CALIBRANDO - Reps: {calibration_reps_done}/{CALIBRATION_REPS}',
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(annotated_frame, f'Estenda e Flexione o {TARGET_ARM.capitalize()} Braco',
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

                if calibration_stage == "estendido" and angle > (EXTENDED_ANGLE_THRESHOLD_DEFAULT - 10): # Margem para capturar o max
                    calibration_angles_max.append(angle)
                    # Transicionar para o estado de flexão para a próxima calibração
                    calibration_stage = "flexionado"
                    # print(f"Estendido - Angle: {int(angle)}")
                elif calibration_stage == "flexionado" and angle < (FLEXED_ANGLE_THRESHOLD_DEFAULT + 10): # Margem para capturar o min
                    calibration_angles_min.append(angle)
                    calibration_reps_done += 1
                    # Transicionar de volta para o estado de extensão para a próxima calibração
                    calibration_stage = "estendido"
                    # print(f"Flexionado - Angle: {int(angle)}")

                if calibration_reps_done >= CALIBRATION_REPS:
                    calibrating = False
                    if calibration_angles_min and calibration_angles_max:
                        flexed_angle_threshold = np.mean(calibration_angles_min) + 5 # Adiciona uma margem
                        extended_angle_threshold = np.mean(calibration_angles_max) - 5 # Subtrai uma margem
                        print(f"Calibracao Concluida!")
                        print(f"Novo FLEXED_ANGLE_THRESHOLD: {flexed_angle_threshold:.2f}")
                        print(f"Novo EXTENDED_ANGLE_THRESHOLD: {extended_angle_threshold:.2f}")
                    else:
                        print("Calibracao falhou. Usando valores padrao.")


            else: # Depois da calibração, entra na lógica normal de contagem
                cv2.putText(annotated_frame, f'Angle: {int(angle)}',
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(annotated_frame, f'Reps: {reps}',
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Lógica de contagem de repetições
                if angle > extended_angle_threshold:
                    stage = "down"
                    # Feedback: "Desça mais!"
                    cv2.putText(annotated_frame, "Estenda o braco!",
                                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                elif angle < flexed_angle_threshold and stage == 'down':
                    stage = "up"
                    reps += 1
                    # Feedback: "Boa! Suba!"
                    cv2.putText(annotated_frame, "Boa! Suba!",
                                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                elif angle < flexed_angle_threshold:
                     # Feedback: "Suba mais!" (se já estiver em "up" mas não totalmente estendido)
                     cv2.putText(annotated_frame, "Flexione mais o braco!",
                                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)


        cv2.imshow('Detector de Flexoes', annotated_frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()