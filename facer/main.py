from flask import Blueprint, flash, g, redirect, render_template, request, url_for, make_response
import json
from facer.db import get_db
from facer.module import Face, Face_Recognizer

bp = Blueprint('main',__name__)
upload_video_path = 'static/video/raw_video.mp4'
# upload_video_path = 'static/video/example-video.mp4'
download_video_path = 'static/video/processed_video.mp4'

@bp.route('/')
def index():
    src_video = upload_video_path
    tar_video = download_video_path
    return render_template('index.html',src_video=src_video,tar_video=tar_video)

@bp.route('/upload',methods=['GET','POST'])
def upload():
    if request.method== 'POST':
        f = request.files['file']
        f.save('facer/'+upload_video_path)
    return '<p>文件上传成功！</p>'

@bp.route('/download',methods=['GET'])
def download():
    pass

@bp.route('/process',methods=['GET'])
def process():
    print('[DEBUG] start to process') 
    fr = Face_Recognizer()
    print('[DEBUG] all faces in sql : ',fr.get_all_faces_in_db()) 
    fr.video_source_path = 'facer/'+upload_video_path
    fr.video_target_path = 'facer/'+download_video_path
    fr.process(preprocess=True)
    print("after process1")
    print("new_face_list_size = ",len(fr.new_face_list))
    if len(fr.new_face_list):
        #if there are new faces, we have got to add them into db
        #convert Face into dict
        new_face_list = []
        for new_face in fr.new_face_list:
            new_face_list.append(new_face.to_dict())
            
        return render_template('index.html',src_video=upload_video_path,new_face_list=new_face_list)
    
    fr.process(preprocess=False)
    
    return render_template('index.html',src_video=upload_video_path)


@bp.route('/addNewFace',methods=['POST'])
def add_new_face():
    # print('enter in addNewFace')
    face_json = request.form.get('face_json')
    face_name = request.form.get('new_face_name')
    is_face = request.form.get('is_face')
    if is_face == 'yes':
        is_face = True
    else:
        is_face = False
    
    print(f'[DEBUG] face_json = {face_json}, face_name = {face_name}, is_face = {is_face}')
    
    if(is_face):
        face = Face()
        face.face_name = face_name
        face.face_json = face_json
        face.write_to_db()
    # print('quit addNewFace')
    
    return '<p>添加成功！</p>'
