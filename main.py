from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    # 환경 변수 또는 기본값으로 Debug 모드 설정
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)
