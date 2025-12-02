# 자동 갱신 저장소 (Auto Update Store) 통합 가이드

이 프로젝트는 update2의 파일 업데이트 및 스케줄러 기능을 gemini-filesearch-ui 프로젝트에 통합한 것입니다.

## 주요 특징

- **로컬 파일 저장 없음**: 모든 데이터는 메모리에서 처리되어 바로 Gemini FileSearchStore에 업로드됩니다
- **자동 스케줄링**: 매주 지정된 요일과 시간에 자동으로 데이터를 갱신합니다
- **다양한 데이터 소스**: API, 캘린더, 웹 크롤링 등 다양한 소스에서 데이터를 수집합니다

## 프로젝트 구조

```
gemini-filesearch-ui/
├── config_data.py              # 설정 파일 (스토어 이름: '자동 갱신 저장소')
├── scheduler.py                # 자동 스케줄러
├── data_updater/               # 데이터 업데이트 모듈
│   ├── __init__.py
│   ├── api_updater.py         # API 데이터 수집 및 업로드
│   ├── calendar_updater.py    # 캘린더 데이터 크롤링 및 업로드
│   └── web_updater.py         # 웹 페이지 크롤링 및 업로드
└── DATA_UPDATER_README.md     # 이 파일
```

## 설치 요구사항

### Python 패키지

```bash
pip install schedule requests beautifulsoup4 selenium xmltodict python-dotenv google-genai
```

### Chrome WebDriver

캘린더 업데이터는 Selenium을 사용하므로 Chrome WebDriver가 필요합니다:

1. Chrome 브라우저 버전 확인
2. [ChromeDriver 다운로드](https://chromedriver.chromium.org/downloads)
3. PATH에 추가하거나 프로젝트 폴더에 배치

## 환경 변수 설정 (.env 파일)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Google Gemini API 키
GOOGLE_API_KEY=your_google_api_key_here

# 각종 API 키들
BOOK_KEY=your_book_api_key
ROSE_KEY=your_rose_api_key
PHOTO_KEY=your_photo_api_key
POOL_KEY=your_pool_api_key
PERFORM_KEY=your_perform_api_key
OLPARKNEWS_KEY=your_olparknews_api_key
VIDEO_KEY=your_video_api_key
NOTICE_KEY=your_notice_api_key
PRESS_KEY=your_press_api_key
COURSE_KEY=your_course_api_key
```

## config_data.py 설정

`config_data.py` 파일에서 다음 설정들을 변경할 수 있습니다:

### 스토어 이름
```python
AUTO_UPDATE_STORE_NAME = '자동 갱신 저장소'
```

### 스케줄러 설정
```python
SCHEDULER_DAY = "monday"  # 실행 요일 (monday, tuesday, ..., sunday)
SCHEDULER_TIME = "03:00"  # 실행 시간 (24시간 형식)
```

### 데이터 소스 설정
- `APIS`: API 데이터 소스 목록
- `CALENDARS`: 캘린더 크롤링 설정
- `WEB_URLS`: 웹 페이지 크롤링 설정

## 사용 방법

### 1. 개별 모듈 실행

각 업데이터를 개별적으로 실행할 수 있습니다:

#### API 업데이터
```bash
python -m data_updater.api_updater
```

#### 캘린더 업데이터
```bash
python -m data_updater.calendar_updater
```
- 1: 최신 3개월 업데이트 (빠름)
- 2: 전체 기간 업데이트 (느림)

#### 웹 크롤링 업데이터
```bash
python -m data_updater.web_updater
```
- 1: Daily Update (최신글 위주)
- 2: Full Archive (전체 수집)

### 2. 자동 스케줄러 실행

매주 지정된 시간에 자동으로 모든 업데이트를 실행합니다:

```bash
python scheduler.py
```

**참고**:
- 스케줄러는 백그라운드에서 계속 실행됩니다
- 중단하려면 `Ctrl + C`를 누르세요
- 실행 로그는 `scheduler.log` 파일에 기록됩니다

### 3. 테스트 실행

스케줄러를 즉시 테스트하려면 `scheduler.py` 파일을 열고 다음 줄의 주석을 해제하세요:

```python
# run_weekly_job()  # 이 주석을 제거하면 즉시 실행됩니다
```

그 다음 실행:
```bash
python scheduler.py
```

## 작동 원리

### 1. API 업데이터 (`api_updater.py`)

- config_data.py의 APIS 목록에서 각 API를 호출합니다
- JSON/XML 응답을 파싱하여 구조화된 데이터로 변환합니다
- 데이터를 날짜순으로 정렬합니다
- 100개 항목씩 청킹하여 마크다운 파일로 변환합니다
- **메모리에서 임시 파일 생성 → 업로드 → 즉시 삭제** (로컬 저장 없음)

### 2. 캘린더 업데이터 (`calendar_updater.py`)

- Selenium을 사용하여 웹 페이지를 크롤링합니다
- Headless 모드로 실행되어 브라우저 창이 표시되지 않습니다
- 월별로 데이터를 그룹핑합니다
- 각 월별 데이터를 별도의 마크다운 파일로 변환합니다
- **메모리에서 임시 파일 생성 → 업로드 → 즉시 삭제**

### 3. 웹 업데이터 (`web_updater.py`)

- BeautifulSoup을 사용하여 웹 페이지를 파싱합니다
- HTML 표를 JSON 구조로 변환하여 본문에 삽입합니다
- FAQ 형식을 마크다운으로 변환합니다
- 텍스트를 청킹하여 RAG 최적화를 수행합니다
- **메모리에서 임시 파일 생성 → 업로드 → 즉시 삭제**

### 4. 스케줄러 (`scheduler.py`)

- `schedule` 라이브러리를 사용합니다
- config_data.py의 설정에 따라 자동으로 실행됩니다
- 세 가지 업데이터를 순차적으로 실행합니다
- 실행 로그를 `scheduler.log`에 기록합니다

## 로컬 파일 저장 제거

이 통합 버전은 **로컬 파일 저장을 완전히 제거**했습니다:

### 이전 방식 (update2):
1. 데이터 수집
2. 로컬 폴더에 .md 파일 저장
3. 파일을 읽어서 업로드
4. 파일이 로컬에 계속 남음

### 새로운 방식:
1. 데이터 수집
2. **메모리에서 청킹 및 포맷팅**
3. **임시 파일 생성 → 업로드 → 즉시 삭제**
4. 로컬에 파일이 남지 않음

### 장점:
- 디스크 공간 절약
- 파일 관리 불필요
- 보안 향상 (민감한 데이터가 로컬에 남지 않음)

## 문제 해결

### ChromeDriver 오류
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```
**해결**: ChromeDriver를 다운로드하여 PATH에 추가하거나 프로젝트 폴더에 배치하세요.

### API 키 오류
```
⚠️ Warning: GOOGLE_API_KEY environment variable is not set.
```
**해결**: `.env` 파일에 올바른 API 키를 추가하세요.

### 업로드 타임아웃
```
타임아웃 (120초)
```
**해결**: 네트워크 연결을 확인하거나 `max_wait` 값을 늘리세요.

### 503/429 에러
```
서버 지연(503)... 재시도
```
**해결**: API 서버가 일시적으로 과부하 상태입니다. 자동으로 재시도되므로 기다리세요.

## 주의사항

1. **API 제한**: 각 API는 요청 제한이 있을 수 있습니다. 과도한 요청을 피하세요.
2. **Chrome 버전**: ChromeDriver 버전은 Chrome 브라우저 버전과 일치해야 합니다.
3. **메모리 사용**: 대용량 데이터를 처리할 때는 메모리 사용량이 증가할 수 있습니다.
4. **네트워크 안정성**: 업로드 중 네트워크가 끊기면 일부 데이터가 누락될 수 있습니다.

## 로그 확인

스케줄러 실행 로그는 `scheduler.log` 파일에 기록됩니다:

```bash
cat scheduler.log
```

또는 Windows에서:
```cmd
type scheduler.log
```

## 추가 정보

- **기존 챗봇 기능**: 이 통합은 기존 gemini-filesearch-ui의 챗봇 기능에 영향을 주지 않습니다.
- **스토어 분리**: '자동 갱신 저장소'는 기존 챗봇 스토어와 별도로 관리됩니다.
- **병렬 처리**: 업로드는 ThreadPoolExecutor를 사용하여 병렬로 처리됩니다.

## 문의

문제가 발생하거나 질문이 있으면 프로젝트 관리자에게 문의하세요.
