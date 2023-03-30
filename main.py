import cv2
import numpy as np
import time
import pyautogui
import mouse
import mediapipe as mp

def fingersUp(landmarks):
    # Define constants for the landmark indices
    thumb_tip = 4
    index_tip = 8
    middle_tip = 12
    ring_tip = 16
    little_tip = 20

    # Get the coordinates of the thumb, index, middle, ring, and little finger tips
    thumb_tip_coords = landmarks.landmark[thumb_tip]
    index_tip_coords = landmarks.landmark[index_tip]
    middle_tip_coords = landmarks.landmark[middle_tip]
    ring_tip_coords = landmarks.landmark[ring_tip]
    little_tip_coords = landmarks.landmark[little_tip]

    # Check whether each finger is up or down
    thumb_up = thumb_tip_coords.y < landmarks.landmark[thumb_tip - 1].y
    index_up = index_tip_coords.y < landmarks.landmark[index_tip - 2].y
    middle_up = middle_tip_coords.y < landmarks.landmark[middle_tip - 2].y
    ring_up = ring_tip_coords.y < landmarks.landmark[ring_tip - 2].y
    little_up = little_tip_coords.y < landmarks.landmark[little_tip - 2].y

    # Return a list indicating which fingers are up
    return [thumb_up, index_up, middle_up, ring_up, little_up]

clocx=0
xlocy=0
plocx=0
plocy=0
pTime=0
w=640
h=480
ws=1366
hs=768
frameR=100
smoothening=.5
cap=cv2.VideoCapture(0)
cap.set(3,w)
cap.set(4,h)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
while True:
    _, image = cap.read()
    image=cv2.flip(image,180)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 1- Find hand landmarks
    results=hands.process(image)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks and connections on image
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    # 2- Get the tip of index and middle fingers
            index_tip=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            x1, y1 = index_tip.x * w, index_tip.y * h
            x2, y2 = middle_tip.x * w, middle_tip.y * h

    # 3- Check which fingers are up
            up = fingersUp(hand_landmarks)
            cv2.rectangle(image, (frameR, frameR), (w - frameR, h - frameR), (255, 0, 0), 2)
            # 4- Only index and middle finger: Moving Mode
            if ((up[1] == True) & (up[2] == False)) | ((up[1] == True) & (up[2] == True)):

                # 5- Convert coordinates

                x3=np.interp(x1,(frameR,w-frameR),(0,ws))
                y3=np.interp(y1,(frameR,h-frameR),(0,hs))

    # 6- Smoothing values
                clocx=(smoothening*plocx)+((1-smoothening)*x3)
                clocy=(smoothening*plocy)+((1-smoothening)*y3)
    # 7- Move Mouse
                try:
                    pyautogui.moveTo(clocx,clocy,duration=0.2)
                    plocx,plocy=clocx,clocy
                except:
                    print("Go to boundary")
                cv2.circle(image,(int(x1),int(y1)),15,(255,0,0),cv2.FILLED)
    # 8- Both index and middle are up: Clicking Mode
            if (up[1] == True) & (up[2] == True):
                # 9- Find distance b/w fingures
                distance=np.sqrt((x2-x1)**2+(y2-y1)**2)
                # 10- Click mouse if distance short
                if distance<25:
                    cv2.circle(image, (int(x1), int(y1)), 15, (0,255, 0), cv2.FILLED)
                    mouse.click('left')
                    mouse.click('left')
    # 11- Frame Rate
    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime
    cv2.putText(image,str(int(fps)),(20,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
    # 12- Display
    cv2.imshow("Mouse Controller",image)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break