import re
import time
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from google import genai
from concurrent.futures import ThreadPoolExecutor, as_completed

# config_data에서 설정 가져오기
import config_data

client = genai.Client(api_key=config_data.GOOGLE_API_KEY)


# =====================================================
# 1. Selenium 크롤러 (Headless 모드)
# =====================================================
def crawl_calendar_site(site_config, months_override=None):
    url = site_config["target_url"]
    selectors = site_config["selectors"]
    site_name = site_config.get("site_name", "Unknown_Site")

    months_to_collect = months_override if months_override else site_config.get("months_to_collect", 3)

    print(f"\n🚀 [{site_name}] 크롤링 시작 ({months_to_collect}개월)")

    # Headless 모드 옵션
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    all_events = []

    try:
        driver.get(url)
        time.sleep(3)

        for i in range(months_to_collect):
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, selectors['ym_display_id']))
                )
                ym_element = driver.find_element(By.ID, selectors['ym_display_id'])
                current_ym = ym_element.text.strip()
            except Exception as e:
                print(f"   [!] 월 정보 로딩 지연: {e}")
                current_ym = f"Unknown_Month_{i}"

            print(f"   Now Scanning: {current_ym} ...")

            rows = driver.find_elements(By.CSS_SELECTOR, selectors['row_container'])

            for row in rows:
                try:
                    title_el = row.find_element(By.CSS_SELECTOR, selectors['title'])
                    date_el = row.find_element(By.CSS_SELECTOR, selectors['date'])
                    try:
                        place = row.find_element(By.CSS_SELECTOR, selectors['place']).text.strip()
                    except:
                        place = "장소 미정"

                    event_data = {
                        "site": site_name,
                        "year_month": current_ym,
                        "title": title_el.text.strip(),
                        "period": date_el.text.strip(),
                        "place": place,
                        "link": title_el.get_attribute("href")
                    }
                    all_events.append(event_data)
                except:
                    continue

            if i == months_to_collect - 1:
                break

            try:
                next_btn = driver.find_element(By.CLASS_NAME, selectors['next_btn_class'])
                next_btn.click()

                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.ID, selectors['ym_display_id']).text != current_ym
                )
                time.sleep(1)
            except:
                print("   [Info] 다음 달 버튼 없음 또는 마지막 페이지")
                break

    except Exception as e:
        print(f"   [Error] 크롤링 중 치명적 오류: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

    print(f"   ✅ 수집 완료: 총 {len(all_events)}건")
    return all_events


# =====================================================
# 2. 월별 데이터를 메모리에서 그룹핑 (파일 저장 안 함)
# =====================================================
def group_events_by_month(events, site_name):
    """
    Returns: [(filename, content), ...]
    """
    if not events:
        return []

    # 월별 그룹핑
    events_by_ym = {}
    for evt in events:
        ym = evt['year_month']
        safe_ym = ym.replace('.', '_')

        if safe_ym not in events_by_ym:
            events_by_ym[safe_ym] = []
        events_by_ym[safe_ym].append(evt)

    chunks = []
    safe_site_name = re.sub(r'[^a-zA-Z0-9가-힣]', '', site_name)

    # 파일 콘텐츠 생성
    for ym, evts in events_by_ym.items():
        filename = f"{safe_site_name}_{ym}.md"

        md_content = [f"# {site_name} 일정 - {ym.replace('_', '.')}"]
        md_content.append(f"업데이트: {time.strftime('%Y-%m-%d %H:%M')}\n")

        for e in evts:
            block = (
                f"## {e['title']}\n"
                f"- **일시:** {e['period']}\n"
                f"- **장소:** {e['place']}\n"
                f"- **링크:** {e['link']}\n"
                f"---\n"
            )
            md_content.append(block)

        content = "\n".join(md_content)
        chunks.append((filename, content))
        print(f"   💾 준비됨: {filename}")

    return chunks


# =====================================================
# 3. 개별 파일 단위 업데이트
# =====================================================
def upload_single_chunk(filename: str, content: str, store_name: str) -> tuple[str, bool, str]:
    temp_file = None
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name

        # 업로드
        op = client.file_search_stores.upload_to_file_search_store(
            file=temp_file,
            file_search_store_name=store_name,
            config={"display_name": filename, "mime_type": "text/markdown"}
        )

        while not op.done:
            time.sleep(1)
            op = client.operations.get(op)

        return (filename, True, "")

    except Exception as e:
        return (filename, False, str(e))

    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass


def update_specific_files(store_name: str, chunks: list[tuple[str, str]]):
    """
    chunks: [(filename, content), ...]
    """
    if not chunks:
        return

    print(f"\n🔄 [Store Update] {len(chunks)}개 월별 파일 갱신 시작...")

    pager = client.file_search_stores.documents.list(parent=store_name)
    existing_docs = {d.display_name: d.name for d in pager}

    for filename, content in chunks:
        # 기존 파일 있으면 삭제
        if filename in existing_docs:
            doc_id = existing_docs[filename]
            print(f"   🗑️ 교체 중 (기존 삭제): {filename}")
            try:
                client.file_search_stores.documents.delete(
                    name=doc_id, config={"force": True}
                )
                time.sleep(1)
            except Exception as e:
                print(f"      ㄴ 삭제 실패: {e}")

        # 새 파일 업로드
        print(f"   📤 업로드: {filename}")
        d_name, ok, msg = upload_single_chunk(filename, content, store_name)
        if ok:
            print(f"      ✅ 완료")
        else:
            print(f"      ❌ 실패: {msg}")


# =====================================================
# 4. 메인 (자동화 모드 지원)
# =====================================================
def run_calendar_pipeline(auto_mode=None):
    store_name = config_data.AUTO_UPDATE_STORE_NAME

    print(f"=== 📅 Monthly Calendar Update ===")
    print(f"[✔] Target Store: {store_name}\n")

    if auto_mode:
        print(f"🤖 자동 모드(스케줄러)로 실행합니다: 옵션 {auto_mode}")
        choice = auto_mode
    else:
        print("1. ⚡ 최신 3개월 업데이트 (데일리)")
        print("2. 📚 전체 기간 업데이트")
        choice = input("선택 (1/2): ").strip()

    override_months = 3 if choice == '1' else None

    calendars = config_data.CALENDARS
    if not calendars:
        print("[❌] 설정 없음")
        return

    for site_conf in calendars:
        # 1. 크롤링 (Headless 모드로 실행됨)
        events = crawl_calendar_site(site_conf, months_override=override_months)

        if events:
            # 2. 월별 데이터를 메모리에서 그룹핑
            chunks = group_events_by_month(events, site_conf.get("site_name", "Unknown"))

            # 3. 생성된 청크들을 스토어에 업로드
            update_specific_files(store_name, chunks)
        else:
            print(f"   ⚠️ 데이터 없음")

    print("\n🎉 캘린더 업데이트 완료!")


if __name__ == "__main__":
    run_calendar_pipeline()
