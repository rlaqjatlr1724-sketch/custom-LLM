# Gemini File Search - 현대적인 파일 검색 웹 애플리케이션

Gemini API의 File Search 기능을 활용하여 로컬 파일을 업로드하고, 자연스러운 대화형 질문으로 파일 내용을 검색하는 웹 애플리케이션입니다.

## 주요 기능

✨ **파일 업로드**
- 드래그 앤 드롭으로 간편한 파일 업로드
- 다양한 파일 형식 지원 (PDF, Word, Excel, PowerPoint, TXT, CSV 등)
- 실시간 업로드 상태 표시

📁 **파일 관리**
- 업로드된 모든 파일 목록 표시
- 파일 정보 확인 (용량, 생성 날짜)
- 파일 삭제 기능

💾 **FileStore 관리**
- 현재 프로젝트의 FileStore 상태 확인
- 전체 파일 수 및 용량 통계

🔍 **Chat 검색**
- 자연스러운 질문으로 파일 내용 검색
- 여러 파일 동시 검색 지원
- Gemini AI의 고급 검색 알고리즘 활용

## 설치 및 실행

### 1. 필수 요구사항
- Python 3.9+
- Gemini API 키 ([Google AI Studio](https://aistudio.google.com/)에서 발급)

### 2. 설치

```bash
# 프로젝트 디렉토리로 이동
cd gemini_web_app

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 후 API 키 입력
# GEMINI_API_KEY=your_api_key_here
```

### 4. 실행

```bash
python run.py
```

웹 브라우저에서 `http://localhost:5000`으로 접속하세요.

## 프로젝트 구조

```
gemini_web_app/
├── app/
│   ├── __init__.py          # Flask 앱 초기화
│   ├── routes.py            # API 라우트
│   └── gemini_client.py     # Gemini API 클라이언트
├── static/
│   ├── css/
│   │   └── style.css        # 모던한 UI 스타일
│   └── js/
│       └── script.js        # 프론트엔드 로직
├── templates/
│   └── index.html           # 메인 HTML
├── requirements.txt         # Python 의존성
├── .env.example            # 환경 변수 템플릿
└── run.py                   # 애플리케이션 진입점
```

## API 엔드포인트

### 파일 관리
- `POST /api/files/upload` - 파일 업로드
- `GET /api/files/list` - 업로드된 파일 목록 조회
- `GET /api/files/<file_id>` - 파일 정보 조회
- `DELETE /api/files/<file_id>` - 파일 삭제

### 검색
- `POST /api/chat/search` - Chat 검색 수행

### FileStore
- `GET /api/stores` - FileStore 목록 조회

## 사용 방법

### 1. 파일 업로드
1. 사이드바에서 "파일 업로드" 탭 클릭
2. 업로드 영역에 파일을 드래그하거나 클릭하여 선택
3. 파일이 자동으로 업로드됩니다

### 2. 업로드된 파일 확인
1. 사이드바에서 "내 파일" 탭 클릭
2. 현재 저장소에 있는 모든 파일을 확인할 수 있습니다
3. 필요하면 파일을 삭제할 수 있습니다

### 3. FileStore 정보 확인
1. 사이드바에서 "FileStore" 탭 클릭
2. 전체 파일 수 및 용량 통계를 확인할 수 있습니다

### 4. Chat 검색
1. 사이드바에서 "Chat 검색" 탭 클릭
2. 검색할 파일을 선택합니다 (여러 개 선택 가능)
3. 질문을 입력하고 "검색" 버튼을 클릭합니다
4. Gemini AI가 파일 내용을 기반으로 답변합니다

## 기술 스택

**백엔드**
- Flask - 웹 프레임워크
- Google Generative AI - Gemini API 통합

**프론트엔드**
- HTML5 - 마크업
- CSS3 - 모던 UI/UX 디자인
- Vanilla JavaScript - 상호작용 로직

## 지원 파일 형식

- PDF
- Word (DOC, DOCX)
- Excel (XLS, XLSX)
- PowerPoint (PPT, PPTX)
- Text (TXT)
- CSV, JSON, XML, HTML

## 주의사항

- 각 파일은 최대 100MB까지 업로드 가능합니다
- Gemini API 사용 시 비용이 발생할 수 있습니다
- API 키는 절대 공개하지 마세요

## 라이선스

MIT License

## 문의

문제가 발생하거나 기능 개선 요청이 있으시면 이슈를 등록해주세요.
