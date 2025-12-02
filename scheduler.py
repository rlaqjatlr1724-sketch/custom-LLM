import schedule
import time
import datetime
import logging
import sys

# 데이터 업데이트 모듈 임포트
from data_updater import api_updater, calendar_updater, web_updater

# config_data에서 스케줄 설정 가져오기
import config_data

# 1. 로그 설정 (실행 기록을 scheduler.log 파일에 남깁니다)
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def run_weekly_job():
    """매주 실행될 통합 업데이트 작업"""
    start_time = datetime.datetime.now()
    print(f"\n" + "="*60)
    print(f"🚀 [Weekly Update] 스케줄러 작업 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    logging.info("Weekly Job Started")

    try:
        # [1] API 업데이트
        print("\n[1/3] API 데이터 동기화 중...")
        api_updater.run_api_pipeline()
        logging.info("API Update Completed")

        # [2] 캘린더/행사 업데이트 (옵션 '1' = 최신 3개월)
        print("\n[2/3] 캘린더 행사 정보 업데이트 중...")
        calendar_updater.run_calendar_pipeline(auto_mode="1")
        logging.info("Calendar Update Completed")

        # [3] 웹 크롤링 업데이트 (옵션 '1' = 최신 데이터 위주)
        print("\n[3/3] 웹 페이지 크롤링 중 (Recent Mode)...")
        web_updater.run_web_pipeline(auto_mode="1")
        logging.info("Web Update Completed")

    except Exception as e:
        error_msg = f"❌ 작업 중 치명적 오류 발생: {e}"
        print(error_msg)
        logging.error(error_msg)

    end_time = datetime.datetime.now()
    duration = end_time - start_time

    print("\n" + "="*60)
    print(f"🎉 [Weekly Update] 작업 완료!")
    print(f"   - 소요 시간: {duration}")
    print(f"   - 다음 실행: 매주 {config_data.SCHEDULER_DAY} {config_data.SCHEDULER_TIME}")
    print("="*60)
    logging.info(f"Job Finished. Duration: {duration}")


# ==========================================
# 🕒 스케줄 설정
# ==========================================

# config_data에서 스케줄 설정 가져오기
schedule_day = config_data.SCHEDULER_DAY.lower()  # "monday", "tuesday", 등
schedule_time = config_data.SCHEDULER_TIME  # "03:00"

# 요일별 스케줄 설정
day_mapping = {
    "monday": schedule.every().monday,
    "tuesday": schedule.every().tuesday,
    "wednesday": schedule.every().wednesday,
    "thursday": schedule.every().thursday,
    "friday": schedule.every().friday,
    "saturday": schedule.every().saturday,
    "sunday": schedule.every().sunday,
}

if schedule_day in day_mapping:
    day_mapping[schedule_day].at(schedule_time).do(run_weekly_job)
    print(f"🕒 주간 스케줄러가 시작되었습니다.")
    print(f"   - 실행 주기: 매주 {schedule_day.capitalize()} {schedule_time}")
    print(f"   - 타겟 스토어: {config_data.AUTO_UPDATE_STORE_NAME}")
    print(f"   - 로그 파일: scheduler.log")
    print(f"   - 중단 방법: Ctrl + C")
else:
    print(f"❌ 잘못된 요일 설정: {schedule_day}")
    print("   config_data.py의 SCHEDULER_DAY를 확인하세요 (monday, tuesday, ..., sunday)")
    sys.exit(1)

# (참고) 테스트를 위해 바로 한 번 돌려보고 싶으면 아래 주석을 풀고 실행하세요.
# run_weekly_job()

while True:
    schedule.run_pending()
    time.sleep(1)
