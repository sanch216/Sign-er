import cv2
from ultralytics import YOLO
import numpy as np
from gtts import gTTS
import os
import time
import pygame
import threading
import sys
import tempfile

print("Starting program...")

# Инициализация pygame для воспроизведения звука
try:
    pygame.mixer.init()
    print("Pygame initialized successfully")
except Exception as e:
    print(f"Error initializing pygame: {e}")
    sys.exit(1)

# Загружаем модель YOLOv8
try:
    model = YOLO('yolov8n.pt')
    print("YOLO model loaded successfully")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    sys.exit(1)

# Подключаем камеру
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    sys.exit(1)

print("Camera opened successfully")

# Предполагаемые параметры камеры (можно откалибровать)
KNOWN_WIDTH = 0.5  # предполагаемая ширина объекта в метрах
FOCAL_LENGTH = 500  # примерное фокусное расстояние в пикселях

# Словарь для отслеживания объектов
tracked_objects = {}  # {object_id: (label, last_seen_time)}
last_speak_time = 0
SPEAK_COOLDOWN = 1  # Задержка между озвучиваниями в секундах
OBJECT_TIMEOUT = 2  # Время в секундах, после которого объект считается новым

def calculate_distance(pixel_width):
    """Рассчитывает расстояние до объекта в метрах"""
    return (KNOWN_WIDTH * FOCAL_LENGTH) / pixel_width

def play_sound_async(file_path):
    """Воспроизводит звук в фоновом режиме"""
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error playing sound: {e}")

def speak_object(label, distance):
    """Озвучивает обнаруженный объект"""
    global last_speak_time
    current_time = time.time()
    
    # Проверяем, прошло ли достаточно времени с последнего озвучивания
    if current_time - last_speak_time < SPEAK_COOLDOWN:
        return
        
    try:
        text = f"New {label} detected at distance {distance:.1f} meters"
        print(f"Speaking: {text}")
        
        # Создаем временный файл в системной временной директории
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Создаем и сохраняем аудио
        tts = gTTS(text=text, lang='en')
        tts.save(temp_path)
        
        # Воспроизводим звук в отдельном потоке
        threading.Thread(target=play_sound_async, args=(temp_path,), daemon=True).start()
        
        # Удаляем временный файл после небольшой задержки
        def delete_file():
            time.sleep(2)  # Увеличиваем время ожидания до 2 секунд
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        threading.Thread(target=delete_file, daemon=True).start()
        last_speak_time = current_time
    except Exception as e:
        print(f"Error in speak_object: {e}")

print("Press 'ESC' to exit the program")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not get frame")
            break

        # Получаем предсказания модели
        results = model(frame, stream=True)
        current_time = time.time()

        # Создаем множество текущих объектов
        current_objects = set()

        # Отображаем найденные объекты
        for r in results:
            boxes = r.boxes
            for box in boxes:
                try:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # координаты
                    conf = float(box.conf[0])              # уверенность
                    cls = int(box.cls[0])                  # класс

                    # Рассчитываем расстояние
                    pixel_width = x2 - x1
                    distance = calculate_distance(pixel_width)

                    label = model.names[cls]
                    
                    # Создаем уникальный идентификатор объекта
                    object_id = f"{label}_{x1}_{y1}"
                    current_objects.add(object_id)
                    
                    # Проверяем, является ли объект новым
                    if conf > 0.5:  # Проверяем уверенность
                        if object_id not in tracked_objects:
                            # Новый объект
                            speak_object(label, distance)
                            tracked_objects[object_id] = (label, current_time)
                        else:
                            # Обновляем время последнего обнаружения
                            tracked_objects[object_id] = (label, current_time)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} {conf:.2f} {distance:.2f}m", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                except Exception as e:
                    print(f"Error processing box: {e}")
                    continue

        # Удаляем объекты, которые не были обнаружены в текущем кадре
        tracked_objects = {obj_id: (label, time) for obj_id, (label, time) in tracked_objects.items() 
                         if obj_id in current_objects}

        cv2.imshow("YOLOv8 - Object Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Нажми Esc чтобы выйти
            print("ESC pressed, exiting...")
            break

except Exception as e:
    print(f"Main loop error: {e}")
finally:
    print("Cleaning up...")
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    print("Program finished")
