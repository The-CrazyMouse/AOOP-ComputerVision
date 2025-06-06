import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import messagebox

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255)]
color_index = 0
draw_color = colors[color_index]

last_color_change = 0
color_cooldown = 1

canvas = None
prev_x, prev_y = None, None
thickness = 5
eraser_thickness = 40

joinha_start_time = None
joinha_hold_time = 0.1

# Flags de controle
popup_result = None
popup_type = None  # "save" ou "exit"
popup_lock = threading.Lock()

def ask_yes_no(title, message):
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno(title, message)
    root.destroy()
    return result

def popup_thread(tipo):
    global popup_result, popup_type
    if tipo == "save":
        result = ask_yes_no("Salvar desenho", "Deseja salvar o desenho?")
    elif tipo == "exit":
        result = ask_yes_no("Sair", "Quer mesmo sair do programa?")
    else:
        return
    with popup_lock:
        popup_result = result
        popup_type = tipo

# Inicializa câmera
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

exit_confirmed = False
popup_active = False

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

    # Enquanto espera confirmação do popup
    if popup_active:
        cv2.putText(frame, "Aguardando confirmação...", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        combined = cv2.addWeighted(frame, 1, canvas, 0.6, 0)
        cv2.imshow("StreamCam - Pressione 'q' ou ESC para sair", combined)
        key = cv2.waitKey(1)

        # Verifica se o popup já respondeu
        with popup_lock:
            if popup_result is not None and popup_type is not None:
                if popup_type == "save":
                    if popup_result:
                        filename = f"desenho_{int(time.time())}.png"
                        cv2.imwrite(filename, canvas)
                        print(f"[INFO] Desenho salvo como {filename}")
                elif popup_type == "exit":
                    if popup_result:
                        exit_confirmed = True
                popup_result = None
                popup_type = None
                popup_active = False
        if exit_confirmed:
            break
        continue

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

        # Joinha para sair
        if fingers == [1, 0, 0, 0, 0]:
            if joinha_start_time is None:
                joinha_start_time = time.time()
            else:
                elapsed = time.time() - joinha_start_time
                if elapsed >= joinha_hold_time and not popup_active:
                    popup_active = True
                    threading.Thread(target=popup_thread, args=("exit",), daemon=True).start()
        else:
            joinha_start_time = None

        # Um dedo: desenhar
        if fingers == [0, 1, 0, 0, 0]:
            if prev_x is not None and prev_y is not None:
                cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), draw_color, thickness)
            prev_x, prev_y = index_x, index_y
            cv2.putText(frame, "Desenhando", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, draw_color, 2)

        # Dois dedos: apagar
        elif fingers == [0, 1, 1, 0, 0]:
            if prev_x is not None and prev_y is not None:
                cv2.line(canvas, (prev_x, prev_y), (index_x, index_y), (0, 0, 0), eraser_thickness)
            prev_x, prev_y = index_x, index_y
            cv2.putText(frame, "Apagando", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Três dedos: mudar cor
        elif fingers == [0, 1, 1, 1, 0]:
            if time.time() - last_color_change > color_cooldown:
                color_index = (color_index + 1) % len(colors)
                draw_color = colors[color_index]
                last_color_change = time.time()
            cv2.putText(frame, "Mudando cor", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, draw_color, 2)

        # Todos os dedos: salvar
        elif fingers == [1, 1, 1, 1, 1] and not popup_active:
            popup_active = True
            threading.Thread(target=popup_thread, args=("save",), daemon=True).start()
            prev_x, prev_y = None, None
        else:
            prev_x, prev_y = None, None
    else:
        prev_x, prev_y = None, None
        joinha_start_time = None

    combined = cv2.addWeighted(frame, 1, canvas, 0.6, 0)
    cv2.imshow("StreamCam - Pressione 'q' ou ESC para sair", combined)

    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
        break
    if cv2.getWindowProperty("StreamCam - Pressione 'q' ou ESC para sair", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
