import os 
from flask import Flask
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'facer.sqlite')
    )
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return '<p>hello world</p>'

    from . import db
    db.init_app(app)

    app.add_url_rule('/',endpoint='index') 
    return app
