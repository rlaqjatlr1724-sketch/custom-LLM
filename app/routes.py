from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import tempfile
from app.gemini_client import GeminiClient

bp = Blueprint('main', __name__)

# 허용되는 파일 확장자
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'xlsx', 'xls', 'ppt', 'pptx', 'csv', 'json', 'xml', 'html'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_mime_type(filename):
    """파일 확장자에 따른 MIME 타입 반환"""
    ext = filename.rsplit('.', 1)[1].lower()
    mime_types = {
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'csv': 'text/csv',
        'json': 'application/json',
        'xml': 'application/xml',
        'html': 'text/html',
    }
    return mime_types.get(ext, 'application/octet-stream')

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/files/upload', methods=['POST'])
def upload_file():
    """파일 업로드"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400

        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Gemini API를 통해 파일 업로드
            gemini = GeminiClient(current_app.config['GEMINI_API_KEY'])
            mime_type = get_mime_type(file.filename)
            result = gemini.upload_file(tmp_path, mime_type)

            if result['success']:
                return jsonify(result), 201
            else:
                return jsonify(result), 400
        finally:
            # 임시 파일 삭제
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/files/list', methods=['GET'])
def list_files():
    """업로드된 파일 목록 조회"""
    try:
        gemini = GeminiClient(current_app.config['GEMINI_API_KEY'])
        files = gemini.list_files_in_store()
        return jsonify({'success': True, 'files': files}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/files/<file_id>', methods=['GET'])
def get_file_info(file_id):
    """파일 정보 조회"""
    try:
        gemini = GeminiClient(current_app.config['GEMINI_API_KEY'])
        file_info = gemini.get_file_info(f"files/{file_id}")
        if 'error' in file_info:
            return jsonify({'success': False, 'error': file_info['error']}), 404
        return jsonify({'success': True, 'file': file_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """파일 삭제"""
    try:
        gemini = GeminiClient(current_app.config['GEMINI_API_KEY'])
        result = gemini.delete_file(f"files/{file_id}")
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/chat/search', methods=['POST'])
def chat_search():
    """Chat으로 파일 검색"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        file_ids = data.get('file_ids', [])

        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400

        if not file_ids:
            return jsonify({'success': False, 'error': 'No files selected for search'}), 400

        # file_ids를 "files/xxx" 형식으로 변환
        formatted_file_ids = [f"files/{fid}" if not fid.startswith('files/') else fid for fid in file_ids]

        gemini = GeminiClient(current_app.config['GEMINI_API_KEY'])
        result = gemini.search_with_chat(query, formatted_file_ids)

        return jsonify({'success': True, 'result': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/stores', methods=['GET'])
def get_stores():
    """FileStore 목록 조회"""
    try:
        gemini = GeminiClient(current_app.config['GEMINI_API_KEY'])
        stores = gemini.list_file_stores()
        return jsonify({'success': True, 'stores': stores}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
