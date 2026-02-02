# 🏟️ Olympic Park AI Chatbot & File Search System

**Language:** [English](README.md) | [한국어](README.ko.md)

A comprehensive AI-powered chatbot and document management system for Olympic Park, featuring Google Gemini File Search API integration, intelligent wayfinding, and automated data synchronization.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Data Updater System](#-data-updater-system)
- [Wayfinding System](#-wayfinding-system)
- [Screenshots](#-screenshots)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🤖 AI Chatbot ("백호돌이" - Baekhodolli)
- Powered by Google Gemini 2.5 Flash model
- Semantic document search using FileSearchStore API
- Multi-language support with automatic language detection
- Conversational context awareness with chat history
- Character-based responses (Olympic Park mascot personality)

### 📁 File Management
- **Temporary Storage**: Upload files via Files API (48-hour retention)
- **Permanent Storage**: Create and manage FileSearchStores
- **Document Operations**: Upload, import, preview, and delete files
- **Format Support**: PDF, TXT, DOC, DOCX, XLSX, XLS, PPT, PPTX, CSV, JSON, XML, HTML
- **CSV to JSON Conversion**: Automatic conversion for better searchability

### 🔍 Semantic Search
- Natural language queries across multiple FileStores
- Real-time search results with citation information
- Configurable active stores for targeted searches
- Grounding support for verified responses

### 🗺️ Wayfinding System
- Interactive map navigation for Olympic Park
- Shortest path calculation using Dijkstra's algorithm
- Facility search by name or category
- Coordinate-based routing (click-to-navigate)
- Real-time distance calculation (pixel to km conversion)
- Korean font support for map labels

### 🔄 Automated Data Synchronization
- **API Updater**: Fetch and sync data from external APIs
- **Calendar Updater**: Crawl event calendars (Selenium-based)
- **Web Updater**: Scrape and index web content
- **Scheduler**: Weekly automated updates with configurable timing
- **Memory-based Processing**: No local file storage required

### 🎨 Modern UI
- Responsive design (desktop, tablet, mobile)
- Intuitive tab-based navigation
- Drag-and-drop file uploads
- Real-time status updates
- Admin panel for store management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │   Chat UI   │  │ File Upload │  │ FileStore   │  │  Wayfinding │ │
│  │             │  │             │  │ Management  │  │     Map     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬─────┘ │
└─────────┼────────────────┼────────────────┼────────────────┼───────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Flask Backend (routes.py)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ /api/chat   │  │ /api/files  │  │ /api/stores │  │/api/wayfind│ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬─────┘ │
└─────────┼────────────────┼────────────────┼────────────────┼───────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Core Services                                │
│  ┌─────────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   GeminiClient      │  │  WayfindingService│  │    SQLite DB    │ │
│  │  (gemini_client.py) │  │  (wayfinding.py)  │  │    (db.py)      │ │
│  └──────────┬──────────┘  └────────┬─────────┘  └────────┬────────┘ │
└─────────────┼───────────────────────┼────────────────────┼──────────┘
              │                       │                    │
              ▼                       ▼                    ▼
┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐
│  Google Gemini API  │  │   Map Data (GeoJSON) │  │  Local SQLite    │
│  - FileSearchStore  │  │   - roads.geojson    │  │  - Mappings      │
│  - Files API        │  │   - facilities.json  │  │  - Config        │
│  - Models API       │  │   - map images       │  │                  │
└─────────────────────┘  └──────────────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Data Updater System (scheduler.py)                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  api_updater.py │  │calendar_updater │  │   web_updater.py    │ │
│  │  (REST APIs)    │  │   (Selenium)    │  │   (BeautifulSoup)   │ │
│  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘ │
│           └────────────────────┴─────────────────────┘             │
│                               │                                     │
│                    ┌──────────▼──────────┐                         │
│                    │   FileSearchStore   │                         │
│                    │   (Auto-sync)       │                         │
│                    └─────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | Flask 3.1+ with Flask-CORS |
| AI/ML | Google Gemini API (google-genai SDK) |
| Database | SQLite3 |
| Graph Processing | NetworkX |
| Spatial Analysis | SciPy (KDTree) |
| Visualization | Matplotlib |
| Web Scraping | BeautifulSoup4, Selenium |
| Task Scheduling | schedule |

### Frontend
| Component | Technology |
|-----------|------------|
| Markup | HTML5 |
| Styling | CSS3 (Responsive) |
| Scripting | Vanilla JavaScript (ES6+) |
| UI Pattern | Tab-based SPA |

### External Services
- Google Gemini API (FileSearch, Models)
- KCISA Open APIs (Korean Cultural Information)
- Olympic Park Website (ksponco.or.kr)

---

## 📋 Prerequisites

### Required
- **Python 3.9+** (tested with 3.10, 3.11)
- **Google Cloud Project** with Gemini API enabled
- **Gemini API Key**

### Optional (for full functionality)
- **Chrome Browser** + **ChromeDriver** (for calendar/web crawling)
- **External API Keys** (KCISA APIs for content sync)

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install -y python3-dev libffi-dev

# macOS
brew install python@3.11

# Windows
# Install Python from python.org
```

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/custom-LLM.git
cd custom-LLM
```

### 2. Create Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

### 5. Run Application

```bash
# Development mode
python main.py

# Production mode
export FLASK_DEBUG=false
python main.py
```

Access the application at: `http://localhost:5001`

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# ===========================================
# Required: Google Gemini API
# ===========================================
GEMINI_API_KEY=your_gemini_api_key_here

# ===========================================
# Optional: External API Keys (for data sync)
# ===========================================
BOOK_KEY=your_book_api_key
ROSE_KEY=your_rose_api_key
PHOTO_KEY=your_photo_api_key
PERFORM_KEY=your_perform_api_key
OLPARKNEWS_KEY=your_olparknews_api_key
VIDEO_KEY=your_video_api_key
NOTICE_KEY=your_notice_api_key
PRESS_KEY=your_press_api_key
COURSE_KEY=your_course_api_key

# ===========================================
# Optional: Flask Configuration
# ===========================================
FLASK_DEBUG=false
```

### Application Settings (config.py)

```python
# Chatbot settings
FILE_STORE_NAME = '챗봇저장소'  # Default FileStore name
MODEL_NAME = "gemini-2.5-flash"  # Gemini model

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5

# Map settings
MAP_IMAGE_PATH = 'map/올공맵.png'
ROADS_GEOJSON_PATH = 'map/roads.geojson'
FACILITIES_JSON_PATH = 'map/olympic_facilities.json'

# Coordinate calibration (adjust if map doesn't align)
CALIB_X_OFFSET = 33.0
CALIB_Y_OFFSET = 33.0
CALIB_X_SCALE = 1.0
CALIB_Y_SCALE = 1.0
```

### Auto-Update Settings (config_data.py)

```python
# Target FileSearchStore for auto-updates
AUTO_UPDATE_STORE_NAME = 'fileSearchStores/your-store-id'

# Scheduler settings
SCHEDULER_DAY = "monday"  # Weekly execution day
SCHEDULER_TIME = "03:00"  # Execution time (24h format)

# API sources, calendars, web URLs configured here
```

---

## 📖 Usage

### Web Interface

#### Chat Tab
1. Navigate to the main page
2. Select FileStore(s) to search
3. Type your question in natural language
4. Receive AI-powered responses with citations

#### File Upload Tab
1. Click "파일 업로드" (File Upload)
2. Drag & drop files or click to select
3. Files are stored temporarily (48 hours)

#### FileStore Management Tab
1. Create new stores with custom names
2. Upload files directly to stores
3. Import from temporary storage
4. Monitor document status and storage usage

#### Wayfinding Tab
1. Select start and end locations
2. Or click directly on the map
3. View optimal route with distance

### Admin Interface

Access admin panel at: `http://localhost:5001/admin`

- Manage FileStores
- View document statistics
- Configure active stores
- Monitor system status

### Command Line Tools

#### Storage Manager

```bash
# Interactive management console
python manage_storage.py
```

Options:
1. List all FileSearchStores
2. List uploaded files
3. Delete stores
4. Delete files
5. Manage store documents

#### Data Updaters

```bash
# API data sync
python -m data_updater.api_updater

# Calendar event sync
python -m data_updater.calendar_updater

# Web content sync
python -m data_updater.web_updater

# Automated scheduler (runs in background)
python scheduler.py
```

---

## 📚 API Reference

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message and get AI response |
| GET | `/api/chat/history` | Get conversation history |

### File Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/files/upload` | Upload file to temporary storage |
| GET | `/api/files` | List all uploaded files |
| GET | `/api/files/<file_id>` | Get file details |
| DELETE | `/api/files/<file_id>` | Delete file |

### FileStore Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/stores/create` | Create new FileSearchStore |
| GET | `/api/stores` | List all stores |
| GET | `/api/stores/<store_id>` | Get store details |
| DELETE | `/api/stores/<store_id>` | Delete store |
| GET | `/api/stores/<store_id>/documents` | List store documents |
| POST | `/api/stores/<store_id>/upload` | Upload to store |
| POST | `/api/stores/<store_id>/import/<file_id>` | Import file to store |
| DELETE | `/api/stores/<store_id>/documents/<doc_id>` | Remove document |

### Configuration Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config/active-stores` | Get active FileStores |
| POST | `/api/config/active-stores` | Set active FileStores |

### Wayfinding Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wayfinding/facilities` | List all facilities |
| POST | `/api/wayfinding/find-path` | Find path by facility names |
| POST | `/api/wayfinding/find-path-coords` | Find path by coordinates |
| POST | `/api/wayfinding/nearest-facility` | Find nearest facility by category |

---

## 🔄 Data Updater System

The data updater system automatically synchronizes content from various sources to keep the AI knowledge base current.

### Components

| Component | Source | Method | Output |
|-----------|--------|--------|--------|
| api_updater.py | KCISA APIs | REST API calls | Markdown chunks |
| calendar_updater.py | Event websites | Selenium crawling | Monthly event files |
| web_updater.py | Web pages | BeautifulSoup | RAG-optimized chunks |

### Processing Flow

```
Data Source → Fetch → Parse → Chunk → Memory Buffer → Upload → FileSearchStore
                                          │
                                          └── No local file storage
```

### Running the Scheduler

```bash
# Start background scheduler
python scheduler.py

# Logs are written to scheduler.log
tail -f scheduler.log
```

### Manual Execution

```bash
# Test immediate execution (uncomment in scheduler.py)
# run_weekly_job()

# Or run individual updaters
python -m data_updater.api_updater
```

---

## 🗺️ Wayfinding System

### Map Data Structure

```
map/
├── 올공맵.png              # Base map image
├── roads.geojson          # Road network (graph edges)
└── olympic_facilities.json # Facility points (graph nodes)
```

### Algorithm

1. **Graph Construction**: Roads loaded as NetworkX graph
2. **Spatial Indexing**: KDTree for nearest-node queries
3. **Pathfinding**: Dijkstra's shortest path
4. **Visualization**: Matplotlib rendering with mascot markers
5. **Output**: Base64-encoded PNG image

### Calibration

If the map doesn't align correctly:

```python
# In config.py or wayfinding.py
CALIB_X_OFFSET = 33.0  # Horizontal shift (pixels)
CALIB_Y_OFFSET = 33.0  # Vertical shift (pixels)
CALIB_X_SCALE = 1.0    # Horizontal scale factor
CALIB_Y_SCALE = 1.0    # Vertical scale factor
```

---

## 📸 Screenshots

### File Upload
![File Upload](docs/images/file-upload.png)

### My Files
![My Files](docs/images/my-files.png)

### FileStore Management
![FileStore Management](docs/images/filestore-management.png)

### Chat Search
![Chat Search](docs/images/chat-search.png)

---

## ❓ Troubleshooting

### Common Issues

#### API Key Not Found
```
⚠️ Warning: GEMINI_API_KEY environment variable is not set.
```
**Solution**: Ensure `.env` file exists and contains valid `GEMINI_API_KEY`

#### ChromeDriver Error
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```
**Solution**: 
1. Download ChromeDriver matching your Chrome version
2. Add to PATH or place in project directory

#### Upload Timeout
```
타임아웃 (120초)
```
**Solution**: Check network connection or increase `max_wait` in updater code

#### 503/429 API Errors
```
서버 지연(503)... 재시도
```
**Solution**: API rate limited; automatic retry will handle this

#### Korean Font Issues (Maps)
```
Font family ['AppleGothic'] not found
```
**Solution**: Install Korean fonts:
```bash
# Ubuntu
sudo apt-get install fonts-nanum

# macOS (usually pre-installed)
# Windows (usually pre-installed with Malgun Gothic)
```

### Debug Mode

Enable detailed logging:

```bash
export FLASK_DEBUG=true
python main.py
```

Check `app/logger.py` for log configuration.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python
- Use meaningful variable/function names
- Add docstrings for public functions
- Keep functions focused and small

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Google Gemini API](https://ai.google.dev/) - AI capabilities
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [NetworkX](https://networkx.org/) - Graph algorithms
- [Seoul Olympic Memorial Organization](https://www.ksponco.or.kr/) - Olympic Park data

---

## 📞 Contact

For questions or support, please open an issue on GitHub or contact the project maintainers.

---

**Made with ❤️ for Olympic Park visitors**
