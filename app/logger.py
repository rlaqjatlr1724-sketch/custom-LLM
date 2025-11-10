import logging
import logging.handlers
from pathlib import Path
import os

# logs 디렉토리 생성
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# 로거 설정
logger = logging.getLogger('gemini_app')

# 이미 핸들러가 있으면 제거 (중복 방지)
if logger.hasHandlers():
    logger.handlers.clear()

logger.setLevel(logging.DEBUG)
logger.propagate = False  # 부모 로거로 전파 방지

# 파일 핸들러 (회전식 로그)
log_file = log_dir / 'app.log'
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 포매터
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 핸들러 추가
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger():
    return logger
