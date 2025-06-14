import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import Label, Button, StringVar, Frame
from PIL import Image, ImageTk
import time
import webbrowser

BASE_FOLDER = "face_program"
IMAGE_FOLDER = "images"
SAVE_PATH = os.path.join(BASE_FOLDER, IMAGE_FOLDER)

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

if not os.path.exists(FACE_CASCADE_PATH):
    exit()

face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

root = tk.Tk()
root.title("퍼스널 컬러 분석")
root.geometry("700x600")

status = StringVar()
status.set("카메라 준비 완료")

f_cam = Frame(root)
f_load = Frame(root)
f_res = Frame(root)

l_cam = Label(f_cam)
l_cam.pack()

btn_photo = Button(f_cam, text="📸 촬영", command=lambda: capture(), font=("Arial", 14))
btn_photo.pack(pady=10)

f_cam.pack()

l_load = Label(f_load, text="🔄 분석 중...", font=("Arial", 14))
l_load.pack()

l_res = Label(f_res, text="", font=("Arial", 14), wraplength=600, justify="center")
l_res.pack()

c_label = Label(f_res, font=("Arial", 16), fg="white", width=40, height=2)
c_label.pack(pady=10)

btn_retry = Button(f_res, text="🔄 재촬영", command=lambda: to_cam(), font=("Arial", 14))
btn_retry.pack(pady=10)

btn_style = Button(f_res, text="🖼️ 스타일링 보기", command=lambda: search(), font=("Arial", 14))
btn_style.pack(pady=10)

camera = cv2.VideoCapture(0)

def cam_update():
    ret, frame = camera.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        l_cam.config(image=img)
        l_cam.image = img
    root.after(10, cam_update)

def detect(rgb):
    r, g, b = rgb
    if r > g + 15 and r > b + 15:
        return "가을 웜톤 🍂"
    elif b > r + 15 and b > g + 15:
        return "겨울 쿨톤 ❄️"
    return "중성톤 🌿"

def face_color(path):
    if not os.path.exists(path):
        return None

    img = cv2.imread(path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    region = img[y:y+h, x:x+w]
    avg_bgr = np.average(region, axis=(0, 1))
    return int(avg_bgr[2]), int(avg_bgr[1]), int(avg_bgr[0])

def to_load():
    f_cam.pack_forget()
    f_load.pack()
    root.update()

def res(tone, color):
    f_load.pack_forget()
    f_res.pack()
    status.set(f"결과: {tone}\nRGB: {color}")

    if tone == "가을 웜톤 🍂":
        l_res.config(text="가을 웜톤 🍂\n\n베이지, 브라운, 오렌지 추천")
        c_label.config(text="🍂 가을 웜톤", bg="#A0522D")
    elif tone == "겨울 쿨톤 ❄️":
        l_res.config(text="겨울 쿨톤 ❄️\n\n블루, 블랙, 네이비 추천")
        c_label.config(text="❄️ 겨울 쿨톤", bg="#4682B4")
    else:
        l_res.config(text="중성톤 🌿\n\n베이지, 그레이 추천")
        c_label.config(text="🌿 중성톤", bg="#808080")

    root.update()

def no_face():
    f_load.pack_forget()
    f_res.pack()
    status.set("얼굴 인식 실패")
    l_res.config(text="얼굴이 없습니다. 다시 시도하세요.")
    c_label.config(text="실패", bg="#FF0000")
    root.update()

def to_cam():
    f_res.pack_forget()
    f_cam.pack()
    status.set("카메라 준비 완료")

def search():
    tone = status.get()
    if "가을 웜톤" in tone:
        webbrowser.open("https://www.google.com/search?q=가을웜톤+스타일링&tbm=isch")
    elif "겨울 쿨톤" in tone:
        webbrowser.open("https://www.google.com/search?q=겨울쿨톤+스타일링&tbm=isch")
    elif "중성톤" in tone:
        webbrowser.open("https://www.google.com/search?q=중성톤+스타일링&tbm=isch")

def capture():
    to_load()
    time.sleep(1)
    ret, frame = camera.read()
    if ret:
        path = os.path.join(SAVE_PATH, "selfie.png")
        cv2.imwrite(path, frame)
        color = face_color(path)
        if color:
            tone = detect(color)
            res(tone, color)
        else:
            no_face()

cam_update()
root.mainloop()
camera.release()
cv2.destroyAllWindows()
