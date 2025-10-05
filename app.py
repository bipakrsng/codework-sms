from flask import Flask
from backend.models.models import db,User,Role
from config import DevelopmentConfig
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from backend.api.api import api
from flask_cors import CORS
from backend.sockets.socket import socketio

import subprocess
#subprocess.Popen(['python','cleanup.py'])


migrate = Migrate()
datastore = SQLAlchemyUserDatastore(db,User,Role)

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app,db)
    api.init_app(app)
    app.security = Security(app,datastore)
    
    # Initialize socketio with the app
    socketio.init_app(app, cors_allowed_origins="*")

    with app.app_context():
        db.create_all()
        import backend.views.views
        import backend.sockets.handlers

    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)