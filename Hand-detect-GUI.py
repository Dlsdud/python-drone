import tkinter as tk # Tkinter
from PIL import ImageTk, Image # Pillow
import cv2 # OpenCV
import os

from djitellopy import Tello
import time

from cvzone.HandTrackingModule import HandDetector
import cvzone

cap = cv2.VideoCapture(0) # VideoCapture 객체 정의
detectorHand = HandDetector(maxHands=1)
gesture = ""

tello = Tello()
tello.connect()

# GUI 설계
win = tk.Tk() # 인스턴스 생성

win.title("DIT AI DRONE") # 제목 표시줄 추가
win.geometry("920x640+50+50") # 지오메트리: 너비x높이+x좌표+y좌표
win.resizable(False, False) # x축, y축 크기 조정 비활성화

# 라벨 추가
lbl = tk.Label(win, text="DIT AI Drone Controller", font='Helvetica 18 bold')
lbl.grid(row=0, column=0) # 라벨 행, 열 배치

# 프레임 추가
frm = tk.Frame(win, width=640, height=480) # 프레임 너비, 높이 설정
frm.grid(row=1, column=0) # 격자 행, 열 배치
frm.place(x=30, y=60)

# 라벨1 추가
lbl1 = tk.Label(frm, width=640, height=480)
lbl1.grid(row=0, column=0)
lbl1.place(x=30, y=6)

label0 = tk.Label(win, text="state: {}".format(tello.get_current_state()), fg='white', bg='black', font='Helvetica 11')
label0.place(x=0, y=590, width=165, height=50)
label1 = tk.Label(win, text='battery: {}'.format(tello.get_battery()), fg='white', bg='black', font='Helvetica 11')
label1.place(x=150, y=590, width=165, height=50)    # 현재 배터리 백분율 가져오기
label2 = tk.Label(win, text='temper: {}'.format(tello.get_temperature()), fg='white', bg='black', font='Helvetica 11')
label2.place(x=300, y=590, width=165, height=50)    # 평균 온도 얻기
label3 = tk.Label(win, text="height: {}".format(tello.get_height()), fg='white', bg='black', font='Helvetica 11')
label3.place(x=450, y=590, width=165, height=50)    # 현재 높이를 cm 단위로 가져오기
label4 = tk.Label(win, text="tof distance: {}".format(tello.get_distance_tof()), fg='white', bg='black', font='Helvetica 11')
label4.place(x=600, y=590, width=165, height=50)    # 현재 거리 값(cm) 가져오기
label5 = tk.Label(win, text="", fg='white', bg='black')
label5.place(x=750, y=590, width=170, height=50)

def video_play():
    ret, frame = cap.read() # 프레임이 올바르게 읽히면 ret은 True
    if not ret:
        cap.release() # 작업 완료 후 해제
        return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    ########################
    image = detectorHand.findHands(frame)
    lmList, bboxInfo = detectorHand.findPosition(image)

    # print(lmList)
    print("bboxInfo", bboxInfo)

    if lmList and detectorHand.handType() == "Right":

        handCenter = bboxInfo["center"]
        print("handCenter", handCenter)
        x, y, w, h = bboxInfo["bbox"]
        print("bb ", x, y, w, h)

        fingers = detectorHand.fingersUp()
        print(fingers)

        if fingers == [1, 0, 1, 0, 1]:  # TAKEOFF
            gesture = "TAKEOFF"
            tello.takeoff()
            time.sleep(3)
        elif fingers == [1, 1, 0, 1, 1]:
            gesture = "LAND"
            tello.land()
            time.sleep(3)
        elif fingers == [0, 0, 0, 1, 1]:
            gesture = "FORWARD"
            tello.move_forward(40)
        elif fingers == [0, 0, 0, 1, 1]:
            gesture = "BACK"
            tello.move_back(40)
        elif fingers == [0, 1, 0, 0, 0]:  # UP
            gesture = "UP"
            tello.move_up(40)
        elif fingers == [0, 1, 1, 0, 0]:  # DOWN
            gesture = "Down"
            tello.move_down(40)
        elif fingers == [0, 0, 0, 0, 1]:  # RIGHT
            gesture = "RIGHT"
            tello.move_right(40)
        elif fingers == [1, 0, 0, 0, 0]:  # LEFT
            gesture = "LEFT"
            tello.move_left(40)
        elif fingers == [0, 0, 1, 0, 0]:  # Middle
            gesture = "Emergency"
            tello.emergency()
        elif fingers == [1, 1, 0, 0, 1]:  # FLIP
            gesture = "FLIP"
            tello.flip()
        elif fingers == [0, 0, 0, 0, 0]:  # don't move
            gesture = "STOP"
        else:
            gesture = ""


        # cv2
        cvzone.cornerRect(image, bboxInfo["bbox"])
        cv2.rectangle(image, (x + 10, y), (x + 190, y - 60), (0, 255, 0), -1)
        cv2.putText(image, f'{gesture}',
                    (x + 50, y - 25),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2, cv2.LINE_AA)

    img = Image.fromarray(image) # Image 객체로 변환
    imgtk = ImageTk.PhotoImage(image=img) # ImageTk 객체로 변환
    # OpenCV 동영상
    lbl1.imgtk = imgtk
    lbl1.configure(image=imgtk)
    lbl1.after(10, video_play)

video_play()

win.mainloop() #GUI 시작