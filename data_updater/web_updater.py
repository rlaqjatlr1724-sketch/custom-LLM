import re
import json
import time
import os
import tempfile
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from google import genai
from concurrent.futures import ThreadPoolExecutor, as_completed

# config_data에서 설정 가져오기
import config_data

client = genai.Client(api_key=config_data.GOOGLE_API_KEY)


# =========================================
# 1. 공통 유틸
# =========================================
def get_soup(url: str):
    """URL → BeautifulSoup"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        if res.encoding and res.encoding.lower() == "iso-8859-1":
            res.encoding = res.apparent_encoding
        else:
            res.encoding = res.apparent_encoding
        return BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print(f"    [❌] 접속 실패 ({url}): {e}")
        return None


# =========================================
# 2. 표(JSON) 구조 변환
# =========================================
def table_to_structured_data(table_soup):
    """HTML 표를 JSON 구조(헤더 + 행 리스트)로 변환"""
    headers = [th.get_text(strip=True) for th in table_soup.find_all("th")]

    if not headers:
        first_tr = table_soup.find("tr")
        if first_tr:
            headers = [td.get_text(strip=True) for td in first_tr.find_all("td")]

    rows = []
    trs = table_soup.find_all("tr")

    start_idx = 0
    if table_soup.find("thead") or (trs and trs[0].find("th")):
        start_idx = 1

    for tr in trs[start_idx:]:
        tds = tr.find_all(["td", "th"])
        if not tds:
            continue

        row = {}
        for i, td in enumerate(tds):
            if i < len(headers):
                key = headers[i]
            else:
                key = f"col_{i}"

            cell_text = td.get_text(strip=True).replace("\n", " ")
            row[key] = cell_text

        if row:
            rows.append(row)

    return {"headers": headers, "rows": rows}


# =========================================
# 3. FAQ 포맷팅
# =========================================
def clean_faq_content(text: str) -> str:
    """Q/A 패턴을 마크다운 형식(**Q.** / **A.**)으로 정리"""
    lines = []
    current_q = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if re.match(r"^(Q[\\.:\\s]|Q$)", line):
            if current_q:
                lines.append(current_q)
            question = re.sub(r"^Q[\\s\\.:]*", "", line).strip()
            current_q = f"**Q. {question}**" if question else "**Q.**"
            continue

        if re.match(r"^(A[\\.:\\s]|A$)", line):
            answer = re.sub(r"^A[\\s\\.:]*", "", line).strip()
            if current_q:
                lines.append(current_q)
                current_q = None
            lines.append(f"**A. {answer}**" if answer else "**A.**")
            continue

        if current_q:
            lines.append(current_q)
            lines.append(f"**A. {line}**")
            current_q = None
        else:
            lines.append(line)

    if current_q:
        lines.append(current_q)

    return "\n".join(lines)


# =========================================
# 4. 청킹 유틸 (RAG 최적화)
# =========================================
def split_into_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def chunk_paragraphs(
    paragraphs,
    title: str = "",
    chunk_size: int = 500,
    overlap: int = 200,
):
    chunks: list[str] = []
    current: list[str] = []

    if title:
        current.extend([f"[TITLE] {title}"])

    for para in paragraphs:
        words = para.split()

        if len(words) > chunk_size:
            if current:
                chunks.append(" ".join(current))
                current = current[-overlap:] if len(current) > overlap else current

            for i in range(0, len(words), chunk_size - overlap):
                sub = words[i : i + chunk_size]
                chunks.append(" ".join(sub))

            continue

        if len(current) + len(words) > chunk_size:
            chunks.append(" ".join(current))
            if overlap > 0:
                current = current[-overlap:] if len(current) > overlap else current
            else:
                current = []

        current.extend(words)

    if current:
        chunks.append(" ".join(current))

    return chunks


def final_chunking(title: str, content: str) -> list[str]:
    paras = split_into_paragraphs(content)
    final_chunks = chunk_paragraphs(paras, title=title, chunk_size=500, overlap=200)
    return final_chunks


# =========================================
# 5. 상세 페이지 파싱 (표 → 본문 삽입 로직 적용)
# =========================================
def extract_content(url: str, config_item: dict | None = None):
    soup = get_soup(url)
    if not soup:
        return None

    # 글로벌 잡동사니 제거
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript", "form", "link", "meta"]):
        tag.decompose()

    target_element = soup

    # 특정 영역 선택 + 제거 selector 적용
    if config_item:
        selector = config_item.get("content_selector")
        if selector:
            found = soup.select_one(selector)
            if found:
                target_element = found

        removes = list(config_item.get("remove_selectors", []))
        removes.extend([".list_btn", ".btn_area", ".sns_share", ".prev_next", ".file_area", ".view_nav"])
        for rm_sel in removes:
            for tag in target_element.select(rm_sel):
                tag.decompose()

    # 표(Table)를 JSON 문자열로 변환하여 본문에 심기
    tables_to_inject: list[tuple[str, str]] = []

    for idx, table in enumerate(target_element.find_all("table")):
        placeholder = f"___TABLE_JSON_INJECT_{idx}___"
        try:
            tbl_dict = table_to_structured_data(table)

            if not tbl_dict['headers'] and not tbl_dict['rows']:
                table.decompose()
                continue

            json_str = json.dumps(tbl_dict, ensure_ascii=False, indent=2)
            formatted_table_str = f"\n\n[TABLE]\n{json_str}\n\n"

            tables_to_inject.append((placeholder, formatted_table_str))
            table.replace_with(soup.new_string(placeholder))

        except Exception:
            pass

    # 제목 추출
    title = "No Title"
    if soup.select_one(".subject"):
        title = soup.select_one(".subject").get_text().strip()
    elif soup.select_one("h3"):
        title = soup.select_one("h3").get_text().strip()
    elif soup.title:
        title = soup.title.get_text().strip()

    # 텍스트 추출 (Placeholder 포함된 상태)
    text = target_element.get_text(separator="\n")

    # Placeholder를 실제 JSON 문자열로 치환
    for placeholder, json_str in tables_to_inject:
        text = text.replace(placeholder, json_str)

    # 라인 정제
    lines: list[str] = []
    skip_keywords = ["본문으로 바로가기", "TOP", "List", "글자크기", "SNS공유", "인쇄", "닫기", "목록"]

    for line in text.splitlines():
        line = line.strip()
        if not line or line in skip_keywords:
            continue
        if line.startswith(("작성자", "작성일", "조회수")):
            continue
        lines.append(line)

    clean_body = "\n".join(lines)

    # FAQ 패턴 처리
    if ("Q" in clean_body and "A" in clean_body) or "faq" in url.lower():
        clean_body = clean_faq_content(clean_body)

    if len(clean_body) < 20:
        return None

    # 최종 청킹
    chunks = final_chunking(title, clean_body)

    return {
        "title": title,
        "url": url,
        "chunks": chunks,
        "crawled_at": time.strftime("%Y-%m-%d"),
        "chunk_count": len(chunks),
    }


# =========================================
# 6. 목록 페이지 크롤링
# =========================================
def crawl_list_page(list_url: str, link_pattern: str):
    soup = get_soup(list_url)
    if not soup:
        return []

    found_links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if link_pattern in href:
            full_url = urljoin(list_url, href)
            found_links.add(full_url)

    return list(found_links)


# =========================================
# 7. 메모리에서 콘텐츠 생성 (파일 저장 안 함)
# =========================================
def create_web_content_chunks(records: list[dict], basename: str, batch_size: int = 40) -> list[tuple[str, str]]:
    """
    Returns: [(filename, content), ...]
    """
    chunks = []

    for i in range(0, len(records), batch_size):
        subset = records[i : i + batch_size]
        md_lines: list[str] = []

        for item in subset:
            for chunk in item["chunks"]:
                md_lines.append("### Record")
                md_lines.append(f"**Title:** {item['title']}")
                md_lines.append(f"**Link:** {item['url']}")
                md_lines.append(f"**Date:** {item['crawled_at']} (수집일)")
                md_lines.append(f"**Chunk:**\n{chunk}")
                md_lines.append("\n---\n")

        part = i // batch_size + 1
        filename = f"{basename}_part{part}.md"
        content = "\n".join(md_lines)
        chunks.append((filename, content))

    return chunks


# =========================================
# 8. 업로드 및 스토어 동기화
# =========================================
def upload_single_chunk(filename: str, content: str, store_name: str) -> tuple[str, bool, str]:
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.md', delete=False) as f:
            f.write(content)
            temp_file = f.name

        op = client.file_search_stores.upload_to_file_search_store(
            file=temp_file,
            file_search_store_name=store_name,
            config={"display_name": filename, "mime_type": "text/markdown"},
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


def update_store_files(store_name: str, chunks: list[tuple[str, str]], base_name_pattern: str):
    print(f"   [Store Update] '{base_name_pattern}' 동기화 시작")

    pager = client.file_search_stores.documents.list(parent=store_name)
    docs_to_delete: list[str] = []

    try:
        all_docs = list(pager)
    except Exception:
        all_docs = []

    for doc in all_docs:
        d_name = getattr(doc, "display_name", "")
        if d_name.startswith(base_name_pattern + "_part"):
            docs_to_delete.append(doc.name)

    if docs_to_delete:
        print(f"   → 기존 파일 {len(docs_to_delete)}개 삭제 중...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            for d_id in docs_to_delete:
                executor.submit(
                    client.file_search_stores.documents.delete,
                    name=d_id,
                    config={"force": True},
                )
        time.sleep(2)

    print("   → 새 파일 업로드 중...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(upload_single_chunk, fn, ct, store_name) for fn, ct in chunks]
        for fut in as_completed(futures):
            name, ok, msg = fut.result()
            if ok:
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name} - {msg}")

    print("   [✔] 동기화 완료\n")


# =========================================
# 9. 메인 실행 (Auto Mode 지원)
# =========================================
def run_web_pipeline(auto_mode=None):
    store_name = config_data.AUTO_UPDATE_STORE_NAME
    web_urls = config_data.WEB_URLS

    if not web_urls:
        print("[ℹ] 크롤링할 URL이 없습니다.")
        return

    print(f"[✔] Target Store: {store_name}\n")

    if auto_mode:
        print(f"🤖 자동 모드(스케줄러)로 실행합니다: 옵션 {auto_mode}")
        mode = auto_mode
    else:
        print("1. 📅 Daily Update (최신글 위주)")
        print("2. 📚 Full Archive (전체 수집)")
        mode = input("실행 모드를 선택하세요 (1/2): ").strip()

    is_daily = (mode == "1")

    for item in web_urls:
        original_name = item.get("name", "noname")
        base_url = item.get("url")
        crawl_type = item.get("type", "single")
        link_pattern = item.get("link_pattern", "")
        pagination = item.get("pagination")

        if not base_url:
            continue

        # 모드에 따른 페이지 범위 및 파일명 설정
        if pagination:
            daily_limit = pagination.get("daily_limit", 5)
            full_end = pagination.get("end_page", 1)

            if is_daily:
                target_name = f"{original_name}_recent"
                p_start = 1
                p_end = daily_limit
            else:
                target_name = f"{original_name}_archive"
                p_start = daily_limit + 1
                p_end = full_end
        else:
            target_name = original_name
            p_start = 1
            p_end = 1

        print(f"=== Web Crawling: {target_name} (Page {p_start}~{p_end}) ===")
        crawled_data_list: list[dict] = []

        # [TYPE 1] 목록형 게시판 크롤링
        if crawl_type == "list" and link_pattern:
            if pagination:
                target_links = set()
                param = pagination.get("param", "nPage")

                for page_num in range(p_start, p_end + 1):
                    page_url = f"{base_url}&{param}={page_num}"
                    print(f"\r    Reading List... [Page {page_num}/{p_end}]", end="", flush=True)

                    links = crawl_list_page(page_url, link_pattern)
                    target_links.update(links)
                    time.sleep(0.3)

                print(f"\n    --> {len(target_links)}개 상세 링크 확보")
            else:
                target_links = set(crawl_list_page(base_url, link_pattern))

            detail_links = list(target_links)
            if detail_links:
                print(f"    2단계: 본문 크롤링 ({len(detail_links)}개)...")

                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_url = {
                        executor.submit(extract_content, link, item): link
                        for link in detail_links
                    }

                    count = 0
                    for future in as_completed(future_to_url):
                        result = future.result()
                        if result:
                            crawled_data_list.append(result)
                            count += 1
                            if count % 10 == 0:
                                print(f"\r    - 진행: {count}/{len(detail_links)}", end="", flush=True)
                print()

        # [TYPE 2] 단일 페이지 크롤링
        else:
            print("    단일 페이지 수집 중...")
            result = extract_content(base_url, item)
            if result:
                crawled_data_list.append(result)

        # 메모리에서 청크 생성 및 업로드
        if crawled_data_list:
            print(f"    → {len(crawled_data_list)}개 데이터 저장 및 동기화")
            try:
                chunks = create_web_content_chunks(crawled_data_list, basename=target_name)
                if chunks:
                    update_store_files(store_name, chunks, base_name_pattern=target_name)
            except Exception as e:
                print(f"    [❌] 에러 발생: {e}")
        else:
            print("    → 수집된 데이터가 없습니다.\n")

    print("🎉 Web Pipeline 완료")


if __name__ == "__main__":
    run_web_pipeline()
