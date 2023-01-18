from flask import Blueprint, flash, g redirect, render_template, request, url_for

from facer.db import get_db
from facer.module import Face, Face_Recognizer

bp = Blueprint('app',__name__)
upload_video_path = 'raw_video.mp4'
download_video_path = 'processed_video.mp4'

@bp.route('/')
def index():
    return render_template('app/index.html')

@bp.route('/upload',methods='POST')
def upload():
    pass

@bp.route('/download',methods='GET')
def download():
    pass

@bp.route('/process',methods='GET')
def process():
    fr = Face_Recognizer(upload_video_path)
    fr.video_path = upload_video_path
    fr.video_target_path = download_video_path
    fr.process(preprocess=True)
    if len(fr.new_face_list):
        #if there are new faces, we have got to add them into db
        return render_template('app/index.html')
    fr.process(preprocess=False)
    
    return render_template('app/index.html')
    
    
