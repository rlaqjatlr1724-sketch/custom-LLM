# config_data.py - 자동 갱신 저장소 설정
import os
from dotenv import load_dotenv

load_dotenv()

# Google API 키 (update2에서 사용하던 키)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    print("⚠️ Warning: GOOGLE_API_KEY environment variable is not set.")

# 자동 갱신 저장소 이름
AUTO_UPDATE_STORE_NAME = 'fileSearchStores/ne82eesbv4ye-cuqu49q14izt'

# API 데이터 소스 설정
APIS = [
    {
        "name": "book",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta2018/getKSCD0820181",
        "key_env": "BOOK_KEY"
    },
    {
        "name": "rose",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta/KSCrose",
        "key_env": "ROSE_KEY"
    },
    {
        "name": "photogallery",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta/KSCphot",
        "key_env": "PHOTO_KEY"
    },
    {
        "name": "perform",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta/KSCperf",
        "key_env": "PERFORM_KEY"
    },
    {
        "name": "olparknews",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta/KSCopno",
        "key_env": "OLPARKNEWS_KEY"
    },
    {
        "name": "video",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta/KSChong",
        "key_env": "VIDEO_KEY"
    },
    {
        "name": "notice",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta/KSCnoti",
        "key_env": "NOTICE_KEY"
    },
    {
        "name": "press",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta/KSCkrep",
        "key_env": "PRESS_KEY"
    },
    {
        "name": "course",
        "url": "https://api.kcisa.kr/openapi/service/rest/meta15/getKSCD0920",
        "key_env": "COURSE_KEY"
    }
]

# CSV 폴더 경로 (선택 사항)
CSV_FOLDER_PATH = None  # CSV 업데이트를 사용하지 않으려면 None으로 설정

# 캘린더 설정
CALENDARS = [
    {
        "site_name": "Concert",
        "target_url": "https://www.ksponco.or.kr/olympicpark/eventInfo/eventInfoListText?mid=a20301010200",
        "months_to_collect": 12,
        "selectors": {
            "row_container": "#rowSpace tr",
            "title": "a.title",
            "date": "span.date",
            "place": "td:nth-child(3)",
            "ym_display_id": "spanYmd",
            "next_btn_class": "btn_next"
        }
    }
]

# 웹 크롤링 설정
WEB_URLS = [
    {
        "name": "olparknewsweb",
        "url": "https://www.ksponco.or.kr/olympicpark/board.es?mid=a20601000000&bid=0045",
        "type": "list",
        "link_pattern": "act=view",
        "content_selector": ".board_view",
        "remove_selectors": [".view_btn", ".reply_area", ".prev_next"],
        "pagination": {
            "param": "nPage",
            "start_page": 1,
            "end_page": 135,
            "daily_limit": 3
        }
    },
    {
        "name": "faqlistweb",
        "url": "https://www.ksponco.or.kr/olympicpark/board.es?mid=a20710000000&bid=0048",
        "type": "single",
        "content_selector": ".list_faq",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "facilityweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20106010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "guideweb1",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20101000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "bicycleweb1",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20104020000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "9web1",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20107010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "lovetreeweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20108000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "parkingweb",
        "url": "https://www.ksponco.or.kr/olympicpark/parkingInfo?mid=a20111000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "howtocomeweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20109000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "poolweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20201020000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "sportscenterweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20201010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "walkweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20202000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "dailyhealthweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20203000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "ecologicalparkweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20401000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "grassweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20402000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "roseinfoweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20403010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "roseinfo2web",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20403020000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "roseinfo3web",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20403030000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "history1web",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20501010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "history2web",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20501030000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "history3web",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20502000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "history4web",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20503010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "history5web",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20503030000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "piinfoweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20605000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "concerthallweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301030800",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "seoulolympiccelweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20303010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "somaweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20303020000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "jogakweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20304010000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "tourprogramweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20305000000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "kspodomeweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301030800",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "tiketlinklivearenaweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301030900",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "olympichallweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301031000",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "wooriarthallweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301031100",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "museliveweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301031300",
        "type": "single",
        "content_selector": ".content_section",
        "remove_selectors": [".view_btn", ".print_btn"]
    },
    {
        "name": "etcweb",
        "url": "https://www.ksponco.or.kr/olympicpark/menu.es?mid=a20301031400",
        "type": "single",
        "content_selector": ".thumb_list.etc_concert",
        "remove_selectors": [".view_btn", ".print_btn", ".btn_link"]
    }
]

# 스케줄러 설정
SCHEDULER_DAY = "monday"  # 매주 월요일
SCHEDULER_TIME = "03:00"  # 새벽 3시
