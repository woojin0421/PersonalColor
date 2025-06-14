import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import Label, Button, StringVar, Frame
from PIL import Image, ImageTk
import time
import webbrowser

# 이미지 저장 폴더 설정
BASE_FOLDER = "face_program"
IMAGE_FOLDER = "captured_images"
SAVE_PATH = os.path.join(BASE_FOLDER, IMAGE_FOLDER)

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

# 얼굴 검출 모델 로드
FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

if not os.path.exists(FACE_CASCADE_PATH):
    exit()

face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

# UI 창 생성
root = tk.Tk()
root.title("퍼스널 컬러 분석 프로그램")
root.geometry("700x600")

status_text = StringVar()
status_text.set("카메라가 준비되었습니다.")

frame_camera = Frame(root)
frame_loading = Frame(root)
frame_result = Frame(root)

label_camera = Label(frame_camera)
label_camera.pack()

button_take_photo = Button(frame_camera, text="📸 사진 촬영", command=lambda: capture_photo(), font=("Arial", 14))
button_take_photo.pack(pady=10)

frame_camera.pack()

label_loading = Label(frame_loading, text="🔄 분석 중... 잠시만 기다려주세요.", font=("Arial", 14))
label_loading.pack()

label_result = Label(frame_result, text="", font=("Arial", 14), wraplength=600, justify="center")
label_result.pack()

color_label = Label(frame_result, font=("Arial", 16), fg="white", width=40, height=2)
color_label.pack(pady=10)

button_retry = Button(frame_result, text="🔄 다시 촬영하기", command=lambda: switch_to_camera(), font=("Arial", 14))
button_retry.pack(pady=10)

button_search = Button(frame_result, text="🖼️ 관련 스타일링 보기", command=lambda: search_fashion(), font=("Arial", 14))
button_search.pack(pady=10)

camera = cv2.VideoCapture(0)

def update_camera():
    ret, frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)
        label_camera.config(image=img)
        label_camera.image = img
    root.after(10, update_camera)

def detect_tone(rgb_color):
    r, g, b = rgb_color
    if (r > g + 15) and (r > b + 15):
        return "가을 웜톤 🍂"
    elif (b > r + 15) and (b > g + 15):
        return "겨울 쿨톤 ❄️"
    else:
        return "중성톤 🌿"

def get_face_color(image_path):
    if not os.path.exists(image_path):
        return None

    image = cv2.imread(image_path)
    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    face_region = image[y:y+h, x:x+w]
    avg_color_bgr = np.average(face_region, axis=(0, 1))
    avg_color_rgb = (int(avg_color_bgr[2]), int(avg_color_bgr[1]), int(avg_color_bgr[0]))
    return avg_color_rgb

def switch_to_loading():
    frame_camera.pack_forget()
    frame_loading.pack()
    root.update()

def show_result(tone_result, skin_color):
    frame_loading.pack_forget()
    frame_result.pack()
    status_text.set(f"🌟 분석 결과: {tone_result}\nRGB: {skin_color}")

    if tone_result == "가을 웜톤 🍂":
        label_result.config(text="가을 웜톤 🍂\n\n차분하고 고혹적인 분위기입니다.\n베스트 컬러: 베이지, 브라운, 오렌지")
        color_label.config(text="🍂 가을 웜톤 추천 컬러", bg="#A0522D")
    elif tone_result == "겨울 쿨톤 ❄️":
        label_result.config(text="겨울 쿨톤 ❄️\n\n차갑고 도시적인 느낌입니다.\n베스트 컬러: 블루, 블랙, 네이비")
        color_label.config(text="❄️ 겨울 쿨톤 추천 컬러", bg="#4682B4")
    else:
        label_result.config(text="중성톤 🌿\n\n다양한 색을 소화합니다.\n베스트 컬러: 베이지, 그레이, 오트밀")
        color_label.config(text="🌿 중성톤 추천 컬러", bg="#808080")

    root.update()

def show_face_not_found():
    frame_loading.pack_forget()
    frame_result.pack()
    status_text.set("⚠️ 얼굴을 찾을 수 없습니다. 다시 촬영해주세요.")
    label_result.config(text="⚠️ 얼굴을 찾을 수 없습니다.\n얼굴이 명확히 보이도록 다시 촬영해주세요.")
    color_label.config(text="얼굴 인식 실패", bg="#FF0000")
    root.update()

def switch_to_camera():
    frame_result.pack_forget()
    frame_camera.pack()
    status_text.set("카메라가 준비되었습니다.")

def search_fashion():
    tone = status_text.get()
    if "가을 웜톤" in tone:
        webbrowser.open("https://www.google.com/search?q=가을웜톤+스타일링&tbm=isch")
    elif "겨울 쿨톤" in tone:
        webbrowser.open("https://www.google.com/search?q=겨울쿨톤+스타일링&tbm=isch")
    elif "중성톤" in tone:
        webbrowser.open("https://www.google.com/search?q=중성톤+스타일링&tbm=isch")

def capture_photo():
    switch_to_loading()
    time.sleep(1)

    ret, frame = camera.read()
    if ret:
        image_path = os.path.join(SAVE_PATH, "selfie.png")
        cv2.imwrite(image_path, frame)
        skin_color = get_face_color(image_path)
        if skin_color:
            tone_result = detect_tone(skin_color)
            show_result(tone_result, skin_color)
        else:
            show_face_not_found()

update_camera()
root.mainloop()
camera.release()
cv2.destroyAllWindows()