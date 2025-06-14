# import time
# import requests
# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import base64

# def get_user_input():
#     print("\n=== Переводчик текста в язык жестов ===")
#     text = input("Введите текст для перевода: ").title().strip()
    
#     save_path = input("Введите путь для сохранения видео (по умолчанию: C:\\Users\\sanch\\Downloads\\videos\\sign_video.webm): ")
#     return text, save_path if save_path else (f"C:\\Users\\sanch\\Downloads\\videos\\{"".join(text.split(" "))}.webm")

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# def wait_for_video(driver, timeout=30):
#     print("[*] Ожидаю генерацию видео...")
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         try:
#             # Ждем появления видео элемента
#             video_element = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "video"))
#             )
            
#             # Проверяем, что видео загружено
#             if video_element.get_attribute("src"):
#                 print("[+] Видео элемент найден")
#                 return video_element
                
#         except Exception as e:
#             print(f"[*] Ожидание видео... ({int(time.time() - start_time)} сек)")
#             time.sleep(1)
    
#     raise TimeoutException("Видео не было сгенерировано в течение 30 секунд")

# def download_video(driver, video_element, save_path):
#     try:
#         print("[*] Начинаю загрузку видео...")
        
#         # JavaScript для получения blob данных
#         js_script = """
#         return new Promise((resolve, reject) => {
#             const video = arguments[0];
#             const xhr = new XMLHttpRequest();
#             xhr.open('GET', video.src, true);
#             xhr.responseType = 'blob';
            
#             xhr.onload = function() {
#                 if (xhr.status === 200) {
#                     const reader = new FileReader();
#                     reader.onloadend = function() {
#                         resolve(reader.result);
#                     };
#                     reader.readAsDataURL(xhr.response);
#                 } else {
#                     reject('Ошибка загрузки видео');
#                 }
#             };
            
#             xhr.onerror = function() {
#                 reject('Ошибка сети');
#             };
            
#             xhr.send();
#         });
#         """
        
#         # Получаем base64 данные
#         print("[*] Получаю данные видео...")
#         base64_data = driver.execute_script(js_script, video_element)
#         if not base64_data:
#             raise Exception("Не удалось получить данные видео")
            
#         # Удаляем префикс data:video/webm;base64,
#         base64_data = base64_data.split(',')[1]
        
#         # Декодируем и сохраняем
#         print("[*] Сохраняю видео...")
#         video_data = base64.b64decode(base64_data)
        
#         # Создаем директорию если её нет
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
#         # Сохраняем файл
#         with open(save_path, 'wb') as f:
#             f.write(video_data)
            
#         if os.path.getsize(save_path) > 0:
#             print(f"[+] Видео успешно сохранено в {save_path}")
#             return True
#         else:
#             print("[!] Ошибка: Файл пустой")
#             return False
            
#     except Exception as e:
#         print(f"[!] Ошибка при скачивании видео: {str(e)}")
#         return False

# def main():
#     try:
#         text, save_path = get_user_input()
        
#         print("[*] Запускаю браузер...")
#         driver = setup_driver()
        
#         print("[*] Открываю сайт...")
#         driver.get("https://sign.mt")
        
#         print("[*] Ввожу текст...")
#         textarea = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "desktop"))
#         )
#         textarea.clear()
#         textarea.send_keys(text)
        
#         # Ждем генерации видео
#         video_element = wait_for_video(driver)
        
#         if video_element:
#             if download_video(driver, video_element, save_path):
#                 print("[+] Процесс успешно завершен")
#             else:
#                 print("[!] Не удалось скачать видео")
#         else:
#             print("[!] Не удалось получить видео элемент")
            
#     except Exception as e:
#         print(f"[!] Произошла ошибка: {str(e)}")
#     finally:
#         if 'driver' in locals():
#             driver.quit()
#         print("[*] Скрипт завершён.")

# if __name__ == "__main__":
#     main()


# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from pydantic import BaseModel
# import os
# import time
# import base64
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# import uvicorn
# import logging

# app = FastAPI()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class TextInput(BaseModel):
#     text: str
#     save_path: str = "C:\\Users\\TM\Desktop\\Хакатоны\\Project2\\video_data\\" + f"{''.join(text.split(' '))}.webm"

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--headless")  # Безголовый режим для сервера
#     return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# def wait_for_video(driver, timeout=30):
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         try:
#             video_element = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "video"))
#             )
#             if video_element.get_attribute("src"):
#                 logger.info("Видео элемент найден")
#                 return video_element
#         except Exception as e:
#             logger.info(f"Ожидание видео... ({int(time.time() - start_time)} сек)")
#             time.sleep(1)
#     raise TimeoutException("Видео не было сгенерировано в течение 30 секунд")

# def download_video(driver, video_element, save_path):
#     try:
#         js_script = """
#         return new Promise((resolve, reject) => {
#             const video = arguments[0];
#             const xhr = new XMLHttpRequest();
#             xhr.open('GET', video.src, true);
#             xhr.responseType = 'blob';
#             xhr.onload = function() {
#                 if (xhr.status === 200) {
#                     const reader = new FileReader();
#                     reader.onloadend = function() {
#                         resolve(reader.result);
#                     };
#                     reader.readAsDataURL(xhr.response);
#                 } else {
#                     reject('Ошибка загрузки видео');
#                 }
#             };
#             xhr.onerror = function() {
#                 reject('Ошибка сети');
#             };
#             xhr.send();
#         });
#         """
        
#         base64_data = driver.execute_script(js_script, video_element)
#         if not base64_data:
#             raise Exception("Не удалось получить данные видео")
            
#         base64_data = base64_data.split(',')[1]
#         video_data = base64.b64decode(base64_data)
        
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
#         with open(save_path, 'wb') as f:
#             f.write(video_data)
            
#         if os.path.getsize(save_path) > 0:
#             logger.info(f"Видео успешно сохранено в {save_path}")
#             return True
#         else:
#             logger.error("Ошибка: Файл пустой")
#             return False
            
#     except Exception as e:
#         logger.error(f"Ошибка при скачивании видео: {str(e)}")
#         return False

# @app.post("/generate-video")
# async def generate_video(input_data: TextInput):
#     try:
#         text = input_data.text.title().strip()
#         save_path = input_data.save_path if input_data.save_path else f"videos/{''.join(text.split())}.webm"
        
#         logger.info("Запускаю браузер...")
#         driver = setup_driver()
        
#         try:
#             logger.info("Открываю сайт...")
#             driver.get("https://sign.mt")
            
#             logger.info("Ввожу текст...")
#             textarea = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "desktop"))
#             )
#             textarea.clear()
#             textarea.send_keys(text)
            
#             video_element = wait_for_video(driver)
            
#             if video_element and download_video(driver, video_element, save_path):
#                 return FileResponse(save_path, media_type="video/webm", filename=os.path.basename(save_path))
#             else:
#                 raise HTTPException(status_code=500, detail="Не удалось скачать видео")
                
#         finally:
#             driver.quit()
            
#     except Exception as e:
#         logger.error(f"Произошла ошибка: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time
import base64
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  # Безголовый режим для сервера
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_for_video(driver, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            video_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            if video_element.get_attribute("src"):
                logger.info("Видео элемент найден")
                return video_element
        except Exception:
            logger.info(f"Ожидание видео... ({int(time.time() - start_time)} сек)")
            time.sleep(1)
    raise TimeoutException("Видео не было сгенерировано в течение 30 секунд")

def download_video(driver, video_element, save_path):
    try:
        js_script = """
        return new Promise((resolve, reject) => {
            const video = arguments[0];
            const xhr = new XMLHttpRequest();
            xhr.open('GET', video.src, true);
            xhr.responseType = 'blob';
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const reader = new FileReader();
                    reader.onloadend = function() {
                        resolve(reader.result);
                    };
                    reader.readAsDataURL(xhr.response);
                } else {
                    reject('Ошибка загрузки видео');
                }
            };
            xhr.onerror = function() {
                reject('Ошибка сети');
            };
            xhr.send();
        });
        """
        
        base64_data = driver.execute_script(js_script, video_element)
        if not base64_data:
            raise Exception("Не удалось получить данные видео")
            
        base64_data = base64_data.split(',')[1]
        video_data = base64.b64decode(base64_data)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(video_data)
            
        if os.path.getsize(save_path) > 0:
            logger.info(f"Видео успешно сохранено в {save_path}")
            return True
        else:
            logger.error("Ошибка: Файл пустой")
            return False
    except Exception as e:
        logger.error(f"Ошибка при скачивании видео: {str(e)}")
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    video_url = None
    
    if request.method == "POST":
        text = request.form.get("text", "").title().strip()
        if not text:
            error = "Введите текст для перевода!"
        else:
            try:
                save_path = f"C:\\Users\\TM\\Desktop\\Хакатоны\\Project2\\Sign-er\\sign_processing\\static\\videos\\{''.join(text.split())}.webm"
                logger.info("Запускаю браузер...")
                driver = setup_driver()
                
                try:
                    logger.info("Открываю сайт...")
                    driver.get("https://sign.mt")
                    
                    logger.info("Ввожу текст...")
                    textarea = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "desktop"))
                    )
                    textarea.clear()
                    textarea.send_keys(text)
                    
                    video_element = wait_for_video(driver)
                    
                    if video_element and download_video(driver, video_element, save_path):
                        video_url = f"C:\\Users\\TM\\Desktop\\Хакатоны\\Project2\\Sign-er\\sign_processing\\static\\video\\{''.join(text.split())}.webm"
                    else:
                        error = "Не удалось сгенерировать или скачать видео"
                        
                finally:
                    driver.quit()
                    
            except Exception as e:
                error = f"Произошла ошибка: {str(e)}"
    
    return render_template("index.html", error=error, video_url=video_url)

if __name__ == "__main__":
    os.makedirs("static/videos", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)