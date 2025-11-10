from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

    # 라우트 등록
    from app import routes
    app.register_blueprint(routes.bp)

    return app
