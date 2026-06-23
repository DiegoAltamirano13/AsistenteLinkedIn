import os
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    # Secret key generada automáticamente (segura)
    app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
    CORS(app)
    from .routes import bp
    app.register_blueprint(bp)
    return app