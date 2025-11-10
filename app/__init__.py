from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pathlib import Path
from app.logger import get_logger

load_dotenv()
logger = get_logger()

def create_app():
    logger.info('=' * 60)
    logger.info('Flask 애플리케이션 시작')
    logger.info('=' * 60)
    
    # 루트 디렉토리 경로 설정
    root_path = Path(__file__).parent.parent
    template_folder = root_path / 'templates'
    static_folder = root_path / 'static'

    logger.debug(f'루트 경로: {root_path}')
    logger.debug(f'템플릿 폴더: {template_folder}')
    logger.debug(f'정적 파일 폴더: {static_folder}')

    app = Flask(__name__, template_folder=str(template_folder), static_folder=str(static_folder))
    logger.info('Flask 앱 인스턴스 생성 완료')
    
    CORS(app)
    logger.info('CORS 활성화')

    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
    
    if app.config['GEMINI_API_KEY']:
        logger.info('Gemini API 키 로드 완료')
    else:
        logger.warning('Gemini API 키가 설정되지 않았습니다!')

    # 라우트 등록
    from app import routes
    app.register_blueprint(routes.bp)
    logger.info('API 라우트 등록 완료')

    logger.info('Flask 애플리케이션 초기화 완료')
    logger.info('=' * 60)
    
    return app
