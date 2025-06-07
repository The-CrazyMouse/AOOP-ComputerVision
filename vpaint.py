import cv2
import mediapipe as mp
import numpy as np
import time

# Inicializa MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Cores
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255)]
color_index = 0
draw_color = colors[color_index]

last_color_change = 0
color_cooldown = 1 

last_save_time = 0
save_cooldown = 2 

# Inicia câmera
cap = None
for i in range(3):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"[INFO] Câmera detectada no índice {i}")
        break
    cap.release()
else:
    print("[ERRO] Nenhuma câmera detectada.")
    exit(1)

canvas = None
prev_x, prev_y = None, None
thickness = 10
eraser_thickness = 40

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERRO] Falha ao capturar frame.")
        break

    frame = cv2.flip(frame, 1)

    if canvas is None:
        canvas = np.zeros_like(frame)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        landmarks = hand_landmarks.landmark
        h, w, _ = frame.shape
        index_x = int(landmarks[8].x * w)
        index_y = int(landmarks[8].y * h)

        fingers = []
        fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)
        tips = [8, 12, 16, 20]
        for tip in tips:
            fingers.append(1 if landmarks[tip].y < landmarks[tip - 2].y else 0)

        # Desenhar com 1 dedo
        if fingers == [0, 1, 0, 0, 0]:
            if prev_x is not None and prev_y is not None:
                cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), draw_color, thickness)
            prev_x, prev_y = index_x, index_y
            cv2.putText(frame, "A desenhar", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Apagar com 2 dedos
        elif fingers == [0, 1, 1, 0, 0]:
            if prev_x is not None and prev_y is not None:
                cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), (0, 0, 0), eraser_thickness)
            prev_x, prev_y = index_x, index_y
            cv2.putText(frame, "A apagar", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Mudar cor com 3 dedos
        elif fingers == [0, 1, 1, 1, 0]:
            if time.time() - last_color_change > color_cooldown:
                color_index = (color_index + 1) % len(colors)
                draw_color = colors[color_index]
                last_color_change = time.time()
            cv2.putText(frame, "A mudar de cor", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, draw_color, 2)

        # Salvar desenho com 5 dedos
        elif fingers == [1, 1, 1, 1, 1]:
            if time.time() - last_save_time > save_cooldown:
                timestamp = int(time.time())
                filename_canvas = f"desenho_{timestamp}.png"
                filename_combined = f"desenho_com_camera_{timestamp}.png"

                combined = cv2.addWeighted(frame, 1, canvas, 0.6, 0)

                cv2.imwrite(filename_canvas, canvas)
                cv2.imwrite(filename_combined, combined)

                print(f"[INFO] Desenho salvo como {filename_canvas} e {filename_combined}")
                last_save_time = time.time()

                prev_x, prev_y = None, None
                cv2.putText(frame, "Desenho guardado!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        else:
            prev_x, prev_y = None, None
    else:
        prev_x, prev_y = None, None

    combined = cv2.addWeighted(frame, 1, canvas, 0.6, 0)
    cv2.imshow("StreamCam - Pressione 'q' ou ESC para sair", combined)

    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:
        break

    if cv2.getWindowProperty("StreamCam - Pressione 'q' ou ESC para sair", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
