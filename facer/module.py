import face_recognition

import cv2
import os
import numpy as np
import json
import facer.db as db
import hashlib

class Face:
    def __init__(self):
        self.face_img = None
        self.face_array = None
        self.face_json = None
        self.face_name = 'Unknown'
        self.x = None
        self.y = None
        self.h = None
        self.w = None
        self.is_new_face = False
        self.is_face = True
        self.face_img_path = None

    def init_from_frame(self,frame,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.face_img = frame

        tmp_face_array = face_recognition.face_encodings(self.face_img)
        if(len(tmp_face_array) == 0):
            self.is_face = False
            self.face_name = 'Unknown'
        else:
            # print(f'[DEBUG] init_from_frame::face_array = {self.face_array[0]}')
            self.face_array = tmp_face_array[0]
            self.face_json = json.dumps(self.face_array.tolist())
            self.face_name = 'Unknown'
        


    def init_from_name_array(self,face_name,face_array):
        self.face_name = face_name
        self.face_array = face_array

    def init_from_img(self,filename:str):
        try:
            self.face_img = face_recognition.load_image_file(filename)
            self.face_array = face_recognition.face_encodings(self.face_img)[0]
            self.face_json = json.dumps(self.face_array.tolist())
            self.face_name = 'Unknown'
        except Exception as e:
            print(f'error occur in class Face init from img')
            print(e)

    @staticmethod
    def compare_faces(face1 ,face2):
        return face_recognition.compare_faces([face1.face_array],face2.face_array)[0]

    def compare_to_this_face(self,b):
        return face_recognition.compare_faces([b.face_array],self.face_array)[0]

    def compare_to_faces_list(self,faces_list):
        faces_array_list = list(map(lambda x : x.face_array,faces_list))
        # print(f'[DEBUG] faces_array_list = {faces_array_list}')
        return face_recognition.compare_faces(faces_array_list,self.face_array)

    def to_dict(self):
        res = {}
        res['face_name'] = self.face_name
        res['is_face'] = self.is_face
        res['face_img_path'] = self.face_img_path
        res['face_json'] = self.face_json
        return res
        

    def write_to_db(self):
        if(self.face_json is not None):
            try:
                conn = db.get_db()
                conn.execute(
                    'insert into faces(facename,facearray) values(?,?)',
                    (self.face_name,self.face_json)
                )
                conn.commit()
            except Exception as e:
                print('error occor in write_to_db while executing sql')
                print(e)
    
    def detect_face(self,all_faces_list):
        '''detect faces: 
            if face is in the db,the function will detect facename and set self.is_new_face = True
            otherwise the function will set self.is_new_face = False
        ''' 
        if(self.is_face):
            # for face in all_faces_list:
            #     if(self.compare_to_this_face(face)):
            #         self.is_new_face = False
            #         self.face_name = face.face_name
            #         return

            face_comparsion_res = self.compare_to_faces_list(all_faces_list)
            for i in range(len(face_comparsion_res)):
                if face_comparsion_res[i]:
                    self.face_name = all_faces_list[i].face_name
                    self.is_face = True
                    self.is_new_face = False
                    return
            #the face is not in db
            self.is_new_face = True
            self.face_name = 'Unknown'
            # print(f'[DEBUG] in Face::detect_face()  typeof(face_array){type(self.face_array)}, face_array = {self.face_array}')
            # if isinstance(self.face_array,list):
            #     self.face_json = json.dumps(self.face_array[0].tolist())
            # else:
            #     self.face_json = json.dumps(self.face_array.tolist())
            self.face_json = json.dumps(self.face_array.tolist())
            



class Face_Recognizer:
    def __init__(self):
        self.video_source_path = None
        self.video_target_path = None
        self.new_face_list = []
        #12 frames only calculate once
        self.interval_cnt = 5
        self.face_detector = cv2.CascadeClassifier('opencv/haarcascade_frontalface_default.xml')
        self.faces_in_db = self.get_all_faces_in_db()

    def detect_faces(self,frame):
        #input a frame detect all faces in the frame
        res = []
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray)
        for x,y,w,h in faces:
            tmp_face = Face()
            tmp_face_frame = frame[y:y+h,x:x+w]
            tmp_face.init_from_frame(tmp_face_frame,x,y,w,h)
            if(tmp_face.is_face):
                tmp_face.detect_face(self.faces_in_db)
                res.append(tmp_face)
        return res
    
    def get_all_faces_in_db(self):
        try:
            res = []
            conn = db.get_db()
            rows = conn.execute('select * from faces').fetchall()
            #convert face sql data into Face class
            for row in rows:
                tmp_face = Face()
                tmp_face.init_from_name_array(row['facename'],list(json.loads(row['facearray'])))
                res.append(tmp_face)
        except Exception as e:
            print(e)
        
        return res

    def add_new_faces(self,face_list:list):
        #add new face to self.new_face_list if the new face is not in the  self.new_face_list
        for face in face_list:
            if(face.is_new_face):
                flag = False
                for new_face in self.new_face_list:
                    if face.compare_to_this_face(new_face):
                        #the face is in the new_face_list
                        flag = True
                        break

                if not flag:
                    #the face is not in the new_face_list
                    hash_name = hashlib.sha1(os.urandom(24)).hexdigest()
                    face.face_img_path = f'static/img/{hash_name}.jpg'
                    self.new_face_list.append(face)
                    #write to local
                    cv2.imwrite('facer/'+face.face_img_path,face.face_img)
                    
    def process(self,preprocess=True):
        if self.video_source_path is not None:
            #read in video
            video_capture = cv2.VideoCapture()
            video_capture.open(self.video_source_path)
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            print(f'[DEBUG] fps={fps} frames={frames}')
            if preprocess:
                #preprocess will analayse the video throughly to get the unknown faces 
                print('[DEBUG] run preprocess')
                frame_step = fps
                cnt = 0
                for i in range(int(frames)):
                    ret, frame = video_capture.read()
                    if(cnt % frame_step == 0):
                        faces_list = self.detect_faces(frame)
                        self.add_new_faces(faces_list)
                    cnt += 1
            else:
                print('[DEBUG] run process')
                video_writer = cv2.VideoWriter(self.video_target_path,cv2.VideoWriter_fourcc(*'mp4v'),fps,size)
                frame_step = self.interval_cnt
                cnt = 0
                faces_list = []
                for i in range(int(frames)):
                    ret, frame = video_capture.read()
                    if(cnt % frame_step == 0):
                        faces_list = self.detect_faces(frame)
                    for face in faces_list:
                        if face.is_face:
                            #print on the frame
                            text_x = face.x
                            text_y = face.y - 20
                            if text_y < 0 :
                                text_y = 0
                            cv2.putText(frame,face.face_name,(text_x,text_y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)
                            cv2.rectangle(frame,(face.x,face.y),(face.x+face.w,face.y+face.h),(0,255,0),2)
                    video_writer.write(frame)
                    cnt += 1
   
