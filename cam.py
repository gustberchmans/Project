import cv2
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import load_model
import mediapipe as mp
from collections import deque


model_path = './data/model.h5'
model = load_model(model_path)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.75)
mp_drawing = mp.solutions.drawing_utils


actions = np.array(['warm', 'koud', 'hallo', 'huis'])


sequence = deque(maxlen=15)  

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    
    num_hands = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
    cv2.putText(frame, f'Hands detected: {num_hands}', (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    if results.multi_hand_landmarks:
        
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        try:
            
            landmarks = []
            hand_landmarks = results.multi_hand_landmarks[0]  
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            
            input_data = np.array(landmarks).reshape(1, 1, 63)
            
            
            prediction = model.predict(input_data, verbose=0)[0]
            
            
            pred_pairs = [(actions[i], pred) for i, pred in enumerate(prediction)]
            pred_pairs.sort(key=lambda x: x[1], reverse=True)
            
            
            for i, (action, conf) in enumerate(pred_pairs):
                y_pos = 30 + (i * 30)  
                
                
                if conf > 0.7:
                    color = (0, 255, 0)  
                elif conf > 0.4:
                    color = (0, 255, 255)  
                else:
                    color = (0, 0, 255)  
                    
                cv2.putText(frame, f'{action}: {conf:.2f}', (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        except Exception as e:
            print(f"Error: {str(e)}")

    cv2.imshow('Hand Gesture Recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()