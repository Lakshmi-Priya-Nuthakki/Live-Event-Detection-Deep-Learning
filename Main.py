import cv2
import mediapipe as mp
import numpy as np
import time
import sqlite3
import logging
import os
from gtts import gTTS
import playsound

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def show_fps(frame, prev_frame_time, new_frame_time):
    new_frame_time = time.time()
    
    fps = 1/(new_frame_time-prev_frame_time)
    
    prev_frame_time = new_frame_time
    
    fps = str(int(fps))
    
    cv2.putText(frame, fps+" FPS", (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3, cv2.LINE_AA)
    
    return  prev_frame_time, new_frame_time

def fall_detect(frame, current_keypoints, threshold, fall_time_start):
    mail_title = "Fall Detection"
    
    if current_keypoints[0].visibility >= threshold and (current_keypoints[26].visibility >= threshold or current_keypoints[25].visibility  >= threshold):  
        try:
            if abs(current_keypoints[0].y - current_keypoints[26].y) <0.05 or abs(current_keypoints[0].y - current_keypoints[25].y) <0.05:
                cv2.putText(frame, "FALL DETECTED", (2, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
                if  fall_time_start == 0: 
                    date = loggingg(warning_name="FALL DETECTED")
                    date = take_ss(frame, date, warning_type= "Fall_Detected_")
                    mail_body = date
                    
                    # Speech conversion
                    text_to_speech = "Fall detected. Please check the area immediately."
                    tts = gTTS(text=text_to_speech, lang='en')
                    tts.save('fall_detected.mp3')
                    playsound.playsound('fall_detected.mp3')
                    
                    print("FALL DETECTED")
                    fall_time_start = time.time()
                else:
                    answ = time.time() - fall_time_start
                    if answ > 50:
                        fall_time_start = 0
                
                return fall_time_start
        except:
            print("Fall Detected")
    return fall_time_start

def forbidden_zone(frame, current_keypoints, threshold, forbidden_timer):

    mail_title = "Forbiden Zone"
    
    if current_keypoints[30].visibility >= threshold or current_keypoints[31].visibility  >= threshold: 
        try:
            if (int(current_keypoints[30].x * 1280) >= 1000 and int(current_keypoints[30].y * 720) >= 300) or (int(current_keypoints[31].x*1280) >= 1000 and int(current_keypoints[31].y*720) >= 300):
                cv2.line(frame, (1000, 300), (1000, 720), (0, 0, 255), 5)
                cv2.line(frame, (1000, 300), (1280, 300), (0, 0, 255), 5)
                cv2.putText(frame, "Forbidden Zone", (1010, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                
                if forbidden_timer == 0:
                
                    date = loggingg(warning_name="Entry into forbidden zone")
                    date = take_ss(frame, date, warning_type = "Forbidden_Zone_")
                    
                    mail_body = date
                    
                    #auto_mail(date, mail_title , mail_body, email_sender, email_password, email_receiver)
                    print("Entry into forbidden zone")
                    forbidden_timer = time.time()
                    
                else:
                    answ = time.time() - forbidden_timer
                    if answ > 50:
                        forbidden_timer = 0
                        
                return forbidden_timer
        except:
            print("Some problem")
    return forbidden_timer

def take_ss(frame ,date, warning_type):
    cv2.imwrite("images/"+warning_type+date+".jpg" ,frame)
    return warning_type+date

def loggingg(warning_name):
    logging.getLogger().warning(warning_name)
    with open('logfile.txt') as f:
        lines = f.readlines()[-1][:19].replace(' ', '_')
        lines = lines.replace(':', '-')
        return lines
def video_write(frame):
    videoo.write(frame)

def auto_mail(date, mail_title, mail_body, email_sender, email_password, email_receiver ):
    
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    import smtplib
    import os

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(email_sender, email_password)
    
    msg = MIMEMultipart()
    
    msg['Subject'] = mail_title
    msg.attach(MIMEText(mail_body))
    
    img_data = open("images/"+date+".jpg", 'rb').read()
    msg.attach(MIMEImage(img_data, 
                         name=os.path.basename(date+".jpg")))

    smtp.sendmail(from_addr = email_sender,
                  to_addrs = [email_receiver], msg = msg.as_string())
    smtp.quit()

cap = cv2.VideoCapture("queda.mp4")

prev_frame_time = 0
new_frame_time = 0

logging.basicConfig(filename="logfile.txt",format="%(asctime)s %(message)s",filemode="w",level=logging.WARNING)

width = int(cap.get(3))
height = int(cap.get(4))

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
videoo = cv2.VideoWriter('video.mp4', fourcc, 20.0, (width, height))

fall_time_start = 0
forbidden_timer = 0
## Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.3, min_tracking_confidence=0.3) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        
        # Recolor image to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False
      
        # Make detection
        results = pose.process(frame)
    
        # Recolor back to BGR
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        cv2.line(frame, (1000, 300), (1000, 720), (0, 255, 0), 5)
        cv2.line(frame, (1000, 300), (1280, 300), (0, 255, 0), 5)
        cv2.putText(frame, "Forbidden Zone", (1010, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        
        # Render detections
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2) 
                                 )               
        
        prev_frame_time, new_frame_time = show_fps(frame, prev_frame_time, new_frame_time)
        
        try:
            current_keypoints = results.pose_landmarks.landmark
            threshold = 0.3
            fall_time_start = fall_detect(frame, current_keypoints, threshold, fall_time_start)
            forbidden_timer = forbidden_zone(frame, current_keypoints, threshold, forbidden_timer)
        except:
            pass
        
        video_write(frame)
        cv2.imshow('Mediapipe Feed', frame)       
            
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    videoo.release()
    cv2.destroyAllWindows()
