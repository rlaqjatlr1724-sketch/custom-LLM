import re
import time
import requests
import xmltodict
import os
import tempfile
from bs4 import BeautifulSoup
from google import genai
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# API 키는 config_data에서 가져옴
import config_data

client = genai.Client(api_key=config_data.GOOGLE_API_KEY)


# =========================================
# 1. 공용 유틸 (텍스트 정제/HTML 처리)
# =========================================
def clean_text(t: str) -> str:
    if not isinstance(t, str):
        t = str(t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def looks_like_html(s: str) -> bool:
    if not s or not isinstance(s, str):
        return False
    s_lower = s.lower()
    return any(tag in s_lower for tag in ["<p", "<br", "<div", "<span", "<table", "&lt;", "&gt;", "&amp;"])


def html_to_text(raw: str) -> str:
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return clean_text(soup.get_text(separator="\n"))


# =========================================
# 2. API 호출 (재시도 로직 포함)
# =========================================
def fetch_api(url: str, key: str | None, retries=3):
    params = {}
    if key and "serviceKey=" not in url:
        params["serviceKey"] = key

    for attempt in range(retries):
        try:
            res = requests.get(url, params=params, timeout=20)

            if res.status_code >= 500 or res.status_code == 429:
                print(f"     [⚠️] 서버 지연({res.status_code})... 재시도 {attempt+1}/{retries}")
                time.sleep(2)
                continue

            if 400 <= res.status_code < 500:
                print(f"     [❌] 요청 오류: {res.status_code} (키/URL 확인)")
                return None

            res.raise_for_status()

            ct = res.headers.get("Content-Type", "").lower()
            if "json" in ct:
                return res.json()
            if "xml" in ct or res.text.strip().startswith("<"):
                try:
                    return xmltodict.parse(res.text)
                except:
                    pass

            soup = BeautifulSoup(res.text, "html.parser")
            return soup.get_text(separator="\n", strip=True)

        except requests.exceptions.RequestException as e:
            print(f"     [⚠️] 연결 실패: {e}... 재시도 {attempt+1}/{retries}")
            time.sleep(2)

    print(f"     [❌] {retries}회 실패.")
    return None


# =========================================
# 3. 데이터 추출 관련 함수들
# =========================================
def extract_items(data):
    if isinstance(data, list):
        if all(isinstance(x, dict) for x in data): return data
        return data

    if isinstance(data, dict):
        candidates = []
        for v in data.values():
            r = extract_items(v)
            if isinstance(r, list): candidates.append(r)
        if candidates: return max(candidates, key=len)
    return None


def flatten_dict(obj, prefix="", out=None):
    if out is None: out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            flatten_dict(v, prefix + k + "_", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            flatten_dict(v, prefix + str(i) + "_", out)
    else:
        if obj not in [None, ""]:
            val = str(obj)
            if looks_like_html(val): val = html_to_text(val)
            out[prefix[:-1]] = clean_text(val)
    return out


def pick_title(flat: dict):
    for k, v in flat.items():
        if any(t in k.lower() for t in ["title", "name", "headline", "program"]): return v
    return None


def pick_date(flat: dict):
    for k, v in flat.items():
        if any(t in k.lower() for t in ["regdate", "date", "created", "updated", "start"]): return v
    return None


def pick_link(flat: dict):
    for k, v in flat.items():
        if any(t in k.lower() for t in ["url", "link", "href"]): return v
    return None


def pick_description(flat: dict):
    key_based = []
    for k, v in flat.items():
        if any(t in k.lower() for t in ["description", "desc", "content", "body", "summary", "info"]):
            key_based.append(v)
    if key_based:
        key_based.sort(key=len, reverse=True)
        return key_based[0]

    value_candidates = []
    for k, v in flat.items():
        if any(x in k.lower() for x in ["title", "name", "date", "id", "code", "url", "link"]): continue
        if len(v) >= 30: value_candidates.append(v)
    if value_candidates:
        value_candidates.sort(key=len, reverse=True)
        return value_candidates[0]
    return None


def parse_date_str(s: str):
    if not s: return datetime.min
    s = str(s).replace("/", "-").strip()
    if " " in s: s = s.split(" ")[0]
    for fmt in ["%Y-%m-%d", "%Y.%m.%d", "%Y%m%d"]:
        try: return datetime.strptime(s, fmt)
        except: continue
    return datetime.min


def sort_items_by_date(items):
    def key_fn(rec):
        flat = flatten_dict(rec)
        d = pick_date(flat)
        return parse_date_str(d or "")
    return sorted(items, key=key_fn, reverse=True)


def format_record(rec) -> str:
    flat = flatten_dict(rec)
    title = pick_title(flat)
    date = pick_date(flat)
    link = pick_link(flat)
    desc = pick_description(flat)

    lines = ["### Record"]
    if title: lines.append(f"**Title:** {title}")
    if date: lines.append(f"**Date:** {date}")
    if desc: lines.append(f"**Description:** {desc}")
    else: lines.append(f"**Description:** (내용 없음)")
    if link: lines.append(f"**Link:** {link}")

    lines.append("\n**Details:**")
    for k, v in flat.items():
        if v in [title, date, desc, link] or not v: continue
        lines.append(f"- {k}: {v}")
    return "\n".join(lines) + "\n\n---\n\n"


# =========================================
# 4. 메모리에서 청킹 (파일 저장 없음)
# =========================================
def create_chunks_in_memory(items, basename: str, batch_size: int = 100) -> list[tuple[str, str]]:
    """
    Returns: [(filename, content), ...]
    """
    chunks = []
    total_items = len(items)
    if total_items == 0:
        return []

    for i in range(0, total_items, batch_size):
        chunk_items = items[i : i + batch_size]
        chunk_text = "".join(format_record(it) for it in chunk_items)
        part_num = (i // batch_size) + 1

        filename = f"{basename}_part{part_num}.md"
        chunks.append((filename, chunk_text))

    return chunks


# =========================================
# 5. 임시 파일 업로드 (메모리 -> 임시 파일 -> 업로드 -> 삭제)
# =========================================
def upload_single_chunk(filename: str, content: str, store_name: str, max_wait: int = 120) -> tuple[str, bool, str]:
    """
    메모리에서 임시 파일로 저장 후 업로드, 업로드 후 임시 파일 삭제
    """
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
            config={
                "display_name": filename,
                "mime_type": "text/markdown"
            }
        )

        wait_sec = 0
        while not op.done:
            time.sleep(1)
            op = client.operations.get(op)
            wait_sec += 1
            if wait_sec > max_wait:
                return (filename, False, f"타임아웃 ({max_wait}초)")

        return (filename, True, "")

    except Exception as e:
        return (filename, False, str(e))

    finally:
        # 임시 파일 삭제
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass


def parallel_upload_chunks(chunks: list[tuple[str, str]], store_name: str, max_workers: int = 5):
    """
    chunks: [(filename, content), ...]
    """
    print(f"   → 새 파일 {len(chunks)}개 병렬 업로드 중...")

    success_count = 0
    failed_files = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {
            executor.submit(upload_single_chunk, fname, content, store_name): fname
            for fname, content in chunks
        }

        for future in as_completed(future_to_chunk):
            d_name, success, error_msg = future.result()

            if success:
                print(f"     ✅ {d_name}")
                success_count += 1
            else:
                print(f"     ❌ {d_name} - {error_msg}")
                failed_files.append((d_name, error_msg))

    print(f"   → 업로드 완료: 성공 {success_count}/{len(chunks)}")
    if failed_files:
        print(f"   ⚠️ 실패: {len(failed_files)}개")


# =========================================
# 6. FileSearchStore 업데이트
# =========================================
def update_store_files(store_name: str, chunks: list[tuple[str, str]], base_name_pattern: str):
    print(f"   [Store Update] '{base_name_pattern}' 동기화 시작")

    # 1) 기존 문서 검색 및 삭제
    pager = client.file_search_stores.documents.list(parent=store_name)

    docs_to_delete = []
    for doc in pager:
        d_name = getattr(doc, "display_name", "")
        if d_name.startswith(base_name_pattern + "_part"):
            docs_to_delete.append(doc.name)

    if docs_to_delete:
        print(f"   → 기존 파일 {len(docs_to_delete)}개 삭제 중...")
        for d_id in docs_to_delete:
            try:
                client.file_search_stores.documents.delete(name=d_id, config={"force": True})
            except Exception:
                pass
        time.sleep(2)

    # 2) 새 파일들 병렬 업로드
    parallel_upload_chunks(chunks, store_name, max_workers=5)

    print("   [✔] 동기화 완료\n")


# =========================================
# 7. 파이프라인 실행
# =========================================
def run_api_pipeline():
    store_name = config_data.AUTO_UPDATE_STORE_NAME
    apis = config_data.APIS

    print(f"[✔] Target Store: {store_name}\n")

    success_apis = []
    failed_apis = []

    for api in apis:
        name = api["name"]
        url = api["url"]
        key_env = api.get("key_env")
        key = os.getenv(key_env) if key_env else None

        print(f"=== API 처리: {name} ===")

        data = fetch_api(url, key)
        if data is None:
            failed_apis.append((name, "API 응답 실패"))
            print("   → 실패 (API Error)\n")
            continue

        items = extract_items(data) or [data]
        if isinstance(items, dict): items = [items]

        items_sorted = sort_items_by_date(items)
        print(f"   → {len(items_sorted)}개 아이템 추출됨")

        try:
            # 메모리에서 청킹 (파일 저장 안 함)
            chunks = create_chunks_in_memory(items_sorted, basename=name, batch_size=100)

            if chunks:
                update_store_files(store_name, chunks, base_name_pattern=name)
                success_apis.append(name)
            else:
                print("   → 저장할 데이터 없음\n")
        except Exception as e:
            failed_apis.append((name, str(e)))
            print(f"   → 처리 중 에러: {e}\n")

    print("\n====================")
    print("🎉 API 업데이트 완료")
    print("   성공:", success_apis)
    print("   실패:", [f[0] for f in failed_apis])
    print("====================")


if __name__ == "__main__":
    run_api_pipeline()
