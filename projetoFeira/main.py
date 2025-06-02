import cv2
import numpy as np
import time
from utils.angle_calculator import calculate_angle
from utils.pose_estimator import PoseEstimator
from config.settings import FLEXED_ANGLE_THRESHOLD_DEFAULT, EXTENDED_ANGLE_THRESHOLD_DEFAULT, CALIBRATION_REPS

def main():
    # --- Escolha do braço pelo usuário ---
    target_arm_display = ""
    target_arm = None
    while True:
        target_arm_input = input("Qual braço você irá usar para o exercício? (direito/d ou esquerdo/e): ").lower().strip()
        if target_arm_input in ['direito', 'd']:
            target_arm = 'left' #lógica invertida
            target_arm_display = 'Braço Direito'
            print(f"Braço escolhido para monitoramento: {target_arm_display}.")
            break
        elif target_arm_input in ['esquerdo', 'e']:
            target_arm = 'right' #lógica invertida
            target_arm_display = 'Braço Esquerdo'
            print(f"Braço escolhido para monitoramento: {target_arm_display}.")
            break
        else:
            print("Entrada inválida. Por favor, digite 'direito', 'd', 'esquerdo' ou 'e'.")

    # --- Passo 1: Tentar abrir a webcam com diferentes índices ---
    camera_index = 0
    cap = cv2.VideoCapture(camera_index)

    while not cap.isOpened() and camera_index < 3:
        print(f"Tentando abrir a webcam no índice {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        camera_index += 1
        time.sleep(1)

    if not cap.isOpened():
        print("\nERRO CRÍTICO: Não foi possível abrir a webcam.")
        print("Por favor, verifique:")
        print("  1. Se a webcam está conectada corretamente.")
        print("  2. Se a webcam não está sendo usada por outro programa.")
        print("  3. As permissões do sistema para acessar a câmera.")
        print("  4. Tente reiniciar o computador.")
        return

    print(f"Webcam aberta com sucesso no índice: {camera_index - 1}")

    target_width = 1280
    target_height = 720
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)
    
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Resolução da Webcam configurada: {actual_width}x{actual_height}")
    if actual_width != target_width or actual_height != target_height:
        print(f"Atenção: A webcam pode não suportar {target_width}x{target_height}. Usando a resolução disponível.")


    pose_estimator = PoseEstimator()

    window_name = 'Detector de Flexoes'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    reps = 0
    stage = None
    paused = False

    calibrating = True
    calibration_angles_min = []
    calibration_angles_max = []
    calibration_stage = "estendido"
    calibration_reps_done = 0

    flexed_angle_threshold = FLEXED_ANGLE_THRESHOLD_DEFAULT
    extended_angle_threshold = EXTENDED_ANGLE_THRESHOLD_DEFAULT

    # Cores e Parâmetros de Fonte/Contorno
    WHITE = (255, 255, 255) # Cor padrão para os textos
    YELLOW = (0, 255, 255)  # Cor para textos de calibração e "PAUSADO"
    RED = (0, 0, 255)       # Cor para feedback negativo
    GREEN = (0, 255, 0)     # Cor para feedback positivo
    # CYAN = (255, 255, 0) # Não será mais usada diretamente como cor principal

    FONT = cv2.FONT_HERSHEY_COMPLEX_SMALL
    FONT_SCALE_LARGE = 2
    FONT_SCALE_MEDIUM = 1.5
    FONT_THICKNESS = 2
    OUTLINE_THICKNESS = 4
    OUTLINE_COLOR = (0, 0, 0) # Preto para o contorno

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("AVISO: Não foi possível ler o frame da webcam. Tentando novamente ou encerrando em breve.")
                time.sleep(0.1)
                break

            frame = cv2.flip(frame, 1)

            results, annotated_frame = pose_estimator.process_frame(frame)
            # Passa o 'target_arm' escolhido pelo usuário
            landmarks = pose_estimator.get_arm_landmarks(results, arm_side=target_arm)
            
            # Draw landmarks APÓS get_arm_landmarks, para que results não seja modificado
            annotated_frame = pose_estimator.draw_landmarks(annotated_frame, results)


            if all(k in landmarks for k in ('shoulder', 'elbow', 'wrist')):
                shoulder = landmarks['shoulder']
                elbow = landmarks['elbow']
                wrist = landmarks['wrist']

                angle = calculate_angle(shoulder, elbow, wrist)

                if calibrating:
                    # Textos de CALIBRANDO (Amarelo)
                    # Contorno do texto
                    cv2.putText(annotated_frame, f'CALIBRANDO - Reps: {calibration_reps_done}/{CALIBRATION_REPS}',
                                (10, 30), FONT, FONT_SCALE_LARGE, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                    # Texto principal
                    cv2.putText(annotated_frame, f'CALIBRANDO - Reps: {calibration_reps_done}/{CALIBRATION_REPS}',
                                (10, 30), FONT, FONT_SCALE_LARGE, YELLOW, FONT_THICKNESS, cv2.LINE_AA)

                    # Instrução de Estender/Flexionar na calibração (Amarelo)
                    # Contorno do texto
                    cv2.putText(annotated_frame, f'Estenda e Flexione o {target_arm_display}',
                                (10, 70), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                    # Texto principal
                    cv2.putText(annotated_frame, f'Estenda e Flexione o {target_arm_display}',
                                (10, 70), FONT, FONT_SCALE_MEDIUM, YELLOW, FONT_THICKNESS, cv2.LINE_AA)

                    if calibration_stage == "estendido" and angle > (EXTENDED_ANGLE_THRESHOLD_DEFAULT - 10):
                        calibration_angles_max.append(angle)
                        calibration_stage = "flexionado"
                    elif calibration_stage == "flexionado" and angle < (FLEXED_ANGLE_THRESHOLD_DEFAULT + 10):
                        calibration_angles_min.append(angle)
                        calibration_reps_done += 1
                        calibration_stage = "estendido"

                    if calibration_reps_done >= CALIBRATION_REPS:
                        calibrating = False
                        if calibration_angles_min and calibration_angles_max:
                            flexed_angle_threshold = np.mean(calibration_angles_min) + 5
                            extended_angle_threshold = np.mean(calibration_angles_max) - 5
                            print(f"Calibracao Concluida!")
                            print(f"Novo FLEXED_ANGLE_THRESHOLD: {flexed_angle_threshold:.2f}")
                            print(f"Novo EXTENDED_ANGLE_THRESHOLD: {extended_angle_threshold:.2f}")
                        else:
                            print("Calibracao falhou. Usando valores padrao.")


                else: # Depois da calibração, entra na lógica normal de contagem
                    # Textos de Ângulo e Repetições (Branco com Contorno Preto)
                    # Contorno do texto Angle
                    cv2.putText(annotated_frame, f'Angle: {int(angle)}',
                                (10, 30), FONT, FONT_SCALE_LARGE, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                    # Texto principal Angle
                    cv2.putText(annotated_frame, f'Angle: {int(angle)}',
                                (10, 30), FONT, FONT_SCALE_LARGE, WHITE, FONT_THICKNESS, cv2.LINE_AA)

                    # Contorno do texto Reps
                    cv2.putText(annotated_frame, f'Reps: {reps}',
                                (10, 70), FONT, FONT_SCALE_LARGE, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                    # Texto principal Reps
                    cv2.putText(annotated_frame, f'Reps: {reps}',
                                (10, 70), FONT, FONT_SCALE_LARGE, WHITE, FONT_THICKNESS, cv2.LINE_AA)

                    # Lógica de contagem de repetições (Mensagens de Feedback Verde/Vermelho)
                    if not paused:
                        if angle > extended_angle_threshold:
                            stage = "down"
                            # Contorno do texto "Estenda o braco!"
                            cv2.putText(annotated_frame, "Estenda o braco!",
                                        (10, 110), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                            # Texto principal "Estenda o braco!" (Vermelho)
                            cv2.putText(annotated_frame, "Estenda o braco!",
                                        (10, 110), FONT, FONT_SCALE_MEDIUM, RED, FONT_THICKNESS, cv2.LINE_AA)
                        elif angle < flexed_angle_threshold and stage == 'down':
                            stage = "up"
                            reps += 1
                            # Contorno do texto "Boa! Suba!"
                            cv2.putText(annotated_frame, "Boa! Suba!",
                                        (10, 110), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                            # Texto principal "Boa! Suba!" (Verde)
                            cv2.putText(annotated_frame, "Boa! Suba!",
                                        (10, 110), FONT, FONT_SCALE_MEDIUM, GREEN, FONT_THICKNESS, cv2.LINE_AA)
                        elif angle < flexed_angle_threshold:
                            # Contorno do texto "Flexione mais o braco!"
                            cv2.putText(annotated_frame, "Flexione mais o braco!",
                                        (10, 110), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                            # Texto principal "Flexione mais o braco!" (Vermelho)
                            cv2.putText(annotated_frame, "Flexione mais o braco!",
                                        (10, 110), FONT, FONT_SCALE_MEDIUM, RED, FONT_THICKNESS, cv2.LINE_AA)
                    else: # Se estiver pausado, exibe mensagem (Amarelo)
                        # Contorno do texto "PAUSADO"
                        cv2.putText(annotated_frame, "PAUSADO",
                                    (10, 110), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
                        # Texto principal "PAUSADO"
                        cv2.putText(annotated_frame, "PAUSADO",
                                    (10, 110), FONT, FONT_SCALE_MEDIUM, YELLOW, FONT_THICKNESS, cv2.LINE_AA)


            # Instruções de Teclas no Canto Superior Direito (Branco com Contorno Preto)
            # Pressione 'Q' para Sair
            # Contorno
            cv2.putText(annotated_frame, "Pressione 'Q' para Sair",
                        (annotated_frame.shape[1] - 500, 30), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
            # Texto principal
            cv2.putText(annotated_frame, "Pressione 'Q' para Sair",
                        (annotated_frame.shape[1] - 500, 30), FONT, FONT_SCALE_MEDIUM, WHITE, FONT_THICKNESS, cv2.LINE_AA)

            # Pressione 'R' para Resetar
            # Contorno
            cv2.putText(annotated_frame, "Pressione 'R' para Resetar",
                        (annotated_frame.shape[1] - 500, 60), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
            # Texto principal
            cv2.putText(annotated_frame, "Pressione 'R' para Resetar",
                        (annotated_frame.shape[1] - 500, 60), FONT, FONT_SCALE_MEDIUM, WHITE, FONT_THICKNESS, cv2.LINE_AA)

            # Pressione 'P' para Pausar
            # Contorno
            cv2.putText(annotated_frame, "Pressione 'P' para Pausar", # Texto sem "/Retomar"
                        (annotated_frame.shape[1] - 500, 90), FONT, FONT_SCALE_MEDIUM, OUTLINE_COLOR, OUTLINE_THICKNESS, cv2.LINE_AA)
            # Texto principal
            cv2.putText(annotated_frame, "Pressione 'P' para Pausar",
                        (annotated_frame.shape[1] - 500, 90), FONT, FONT_SCALE_MEDIUM, WHITE, FONT_THICKNESS, cv2.LINE_AA)


            cv2.imshow(window_name, annotated_frame)

            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                print("Programa finalizado pelo usuário.")
                break
            elif key == ord('r'):
                reps = 0
                stage = None
                calibrating = True
                calibration_angles_min = []
                calibration_angles_max = []
                calibration_stage = "estendido"
                calibration_reps_done = 0
                flexed_angle_threshold = FLEXED_ANGLE_THRESHOLD_DEFAULT
                extended_angle_threshold = EXTENDED_ANGLE_THRESHOLD_DEFAULT
                paused = False
                print("Contagem e Calibração Reiniciadas!")
            elif key == ord('p'):
                paused = not paused
                if paused:
                    print("Contador Pausado.")
                else:
                    print("Contador Retomado.")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado durante a execução: {e}")
        print("Por favor, verifique se todas as dependências estão instaladas e o ambiente está configurado corretamente.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Recursos da webcam liberados e janelas fechadas.")

if __name__ == "__main__":
    main()