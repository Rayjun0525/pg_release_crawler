#!/usr/bin/env python3
import requests, csv, time, re, psycopg2
from bs4 import BeautifulSoup
from typing import Optional

def release_url(major: int, minor: int) -> str:
    return f"https://www.postgresql.org/docs/release/{major}.{minor}/"

def normalize_space(s: str) -> str:
    return " ".join((s or "").replace("\xa0", " ").split())

def fetch(url: str):
    try:
        r = requests.get(url, timeout=10)
        return r.status_code, r.text
    except requests.RequestException as e:
        return None, str(e)

def parse_release_page(html: str, fallback_title: str):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup.find("div", id="content") or soup
    release_date = ""
    for p in main.find_all("p"):
        txt = normalize_space(p.get_text())
        if txt.lower().startswith("release date:"):
            release_date = txt.split(":", 1)[-1].strip()
            break

    version_match = re.search(r"(\d+\.\d+)", fallback_title)
    version = version_match.group(1) if version_match else fallback_title

    results = []
    current_section = ""
    for el in main.find_all(["h3", "h4", "li", "p"]):
        if el.name in ["h3", "h4"]:
            current_section = el.get_text(strip=True)
        elif el.name in ["li", "p"]:
            text = normalize_space(el.get_text(" ", strip=True))
            if text and not text.lower().startswith("release date"):
                results.append({
                    "release_date": release_date,
                    "version": version,
                    "section": current_section,
                    "subsection": "",
                    "subsubsection": "",
                    "content": text
                })
    return results

def crawl_releases(start_major: int, end_major: Optional[int] = None):
    data = []
    major = start_major
    if end_major is None:
        end_major = start_major
    while major <= end_major:
        minor = 0
        misses = 0
        while True:
            url = release_url(major, minor)
            code, html = fetch(url)
            if code == 200:
                rows = parse_release_page(html, f"Release {major}.{minor}")
                data.extend(rows)
                misses = 0
            else:
                misses += 1
                if misses >= 3 and minor > 0:
                    break
            minor += 1
            if minor > 100:
                break
            time.sleep(0.5)
        major += 1
    return data

def save_and_load(data):
    csv_path = "/tmp/postgresql_release_notes.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["release_date", "version", "section", "subsection", "subsubsection", "content"])
        writer.writeheader()
        writer.writerows(data)
    print(f"CSV saved: {csv_path}")

    # PostgreSQL에 적재
    conn = psycopg2.connect("dbname=postgres user=postgres")
    cur = conn.cursor()
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        cur.copy_expert("""
            COPY postgresql_release_notes(release_date, version, section, subsection, subsubsection, content)
            FROM STDIN WITH CSV HEADER DELIMITER ',' NULL '';
        """, f)
    conn.commit()
    cur.close()
    conn.close()
    print("Data loaded into PostgreSQL successfully")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: pg_release_crawler.py <start_major> [end_major]")
        sys.exit(1)
    start_major = int(sys.argv[1])
    end_major = int(sys.argv[2]) if len(sys.argv) > 2 else None
    data = crawl_releases(start_major, end_major)
    if data:
        save_and_load(data)
    else:
        print("No data found.")
