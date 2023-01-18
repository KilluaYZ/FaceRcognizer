import face_recognition
import argparse
import cv2
import os
import flask
import numpy as np
import json
import db

class Face:
    this.face_img = None
    this.face_array = None
    this.face_json = None
    this.face_name = 'Unknown'
    this.x = None
    this.y = None
    this.h = None
    this.w = None
    this.is_new_face = False
    this.is_face = True

    def init_from_frame(self,frame,x,y,w,h):
        this.x = x
        this.y = y
        this.w = w
        this.h = h
        this.face_img = frame
        try:
            this.face_array = face_recognition.face_encodings(this.face_img)[0]
            this.face_json = json.dumps(this.face_array.tolist())
            this.face_name = 'Unknown'
        except(Exception as e):
            print(f'error occur in class Face init from frame')
            print(e)


    def init_from_name_array(self,face_name,face_array):
        this.face_name = face_name
        this.face_array = face_array

    def init_from_img(self,filename:str):
        try:
            this.face_img = face_recognition.load_image_file(filename)
            this.face_array = face_recognition.face_encodings(this.face_img)[0]
            this.face_json = json.dumps(this.face_array.tolist())
            this.face_name = 'Unknown'
        except(Exception as e):
            print(f'error occur in class Face init from img')
            print(e)

    @staticmethod
    def compare_faces(Face face1, Face face2):
        return face_recognition.compare_faces([face1.face_array],face2.face_array)[0]

    def compare_to_this_face(self,b:Face):
        return face_recognition.compare_faces([this.face_array],b.face_array)[0]

    def write_to_db(self):
        if(this.face_json is not None):
            try:
                conn = db.get_db()
                conn.execute(
                    'insert into faces(facename,facearray) values(%s,%s)',
                    (this.face_name,this.face_json)
                )
                conn.commit()
            except Exception as e:
                print('error occor in write_to_db while executing sql')
    def detect_face(self,all_faces_list):
        '''detect faces: 
            if face is in the db,the function will detect facename and set this.is_new_face = True
            otherwise the function will set this.is_new_face = False
        ''' 
        for face in all_faces_list:
            if(compare_to_this_face(face)):
                this.is_new_face = False
                this.face_name = face.face_name
                return

        #the face is not in db
        this.is_new_face = True
        this.face_name = 'Unknown'
        this.face_json = json.dump(this.face_array.tolist)



class Face_Recognizer:
    this.video_path = None
    this.new_face_list = []
    #12 frames only calculate once
    this.interval_cnt = 12
    this.face_detector = cv2.CascadeClassifier('opencv/haarcascade_frontalface_default.xml')
    this.faces_in_db = get_all_faces_in_db()

    def __init__(self,video_path:str):
        this.video_path = video_path

    def detect_faces(self,frame):
        #input a frame detect all faces in the frame
        res = []
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = this.face_detector.detectMultiScale(gray)
        for x,y,w,h in faces:
            tmp_face = Face()
            tmp_face.init_from_frame(frame,x,y,w,h)
            tmp_face.detect_face(this.faces_in_db)
            res.append(tmp_face)
        return res
    
    def get_all_faces_in_db(self):
        try:
            res = []
            conn = db.get_db()
            conn.execute('select * from faces')
            rows = conn.fetchall()
            #convert face sql data into Face class
            for row in rows:
                tmp_face = Face()
                tmp_face.init_from_name_array(row['facename'],row['facearray'])
                res.append(tmp_face)

            return res

    def add_new_faces(self,face_list):
        #add new face to this.new_face_list if the new face is not in the  this.new_face_list
        for face in face_list:
            if(face.is_new_face):
                flag = False
                for new_face in this.new_face_list:
                    if face.compare_to_this_face(new_face):
                        #the face is in the new_face_list
                        flag = True
                        break

                if not flag:
                    #the face is not in the new_face_list
                    this.new_face_list.append(face)
                    

    def process(self,preprocess=True):
        if this.video_path is not None:
            #read in video
            video_capture = cv2.VideoCapture()
            video_capture.open(this.viedo_path)
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            print(f'[DEBUG] fps={fps} frames={frames}')
            if preprocess:
                #preprocess will analayse the video throughly to get the unknown faces 
                print('[DEBUG] run preprocess')
                frame_step = fps
                cnt = 0
                for i in range(int(frames)):
                    ret, frame = video_capture.read()
                    if(cnt % frame_step == 0):
                        faces_list = detect_faces(frame)
                        add_new_faces(faces_list)
                    cnt += 1
            else:
                print('[DEBUG] run process')
                frame_step = this.interval_cnt
                cnt = 0
                faces_list = []
                for i in range(int(frames)):
                    ret, frame = video_capture.read()
                    if(cnt % frame_step == 0):
                        faces_list = detect_faces(frame)
                    for face in faces_list:
                        if face.is_face:
                            #print on the frame


                    cnt += 1

                    

                                    



   
