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
            print(f'error occur in class Face init')
            print(e)

    @staticmethod
    def compare_faces(Face face1, Face face2):
        return face_recognition.compare_faces([face1.face_array],face2.face_array)[0]

    def compare_to_this_face(self,Face b):
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



class Face_Recognizer:
    this.video_path = None
    this.new_face_list = []
    

    def __init__(self,video_path:str):
        this.video_path = video_path

    def process(self):
        


   
