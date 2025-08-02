# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import os

# === GitHub 이슈 assignees, mentions ===
github_assignees = ["Koony2510"]
github_mentions = ["Koony2510"]

def create_github_issue(title, body):
    github_repo = os.getenv("GITHUB_REPOSITORY")
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_repo or not github_token:
        print("⚠️ GITHUB_REPOSITORY 또는 GITHUB_TOKEN 환경변수가 설정되어 있지 않습니다.")
        return False

    api_url = f"https://api.github.com/repos/{github_repo}/issues"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    mention_text = " ".join([f"@{user}" for user in github_mentions])
    full_body = f"{mention_text}\n\n{body}"

    payload = {
        "title": title,
        "body": full_body,
        "assignees": github_assignees
    }

    # JSON 전송 시 requests가 내부적으로 UTF-8 인코딩
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 201:
        print("📌 GitHub 이슈가 성공적으로 생성되었습니다.")
        return True
    else:
        print(f"⚠️ GitHub 이슈 생성 실패: {response.status_code} - {response.text}")
        return False

def parse_date_jp(text):
    try:
        dt = datetime.strptime(text, "%Y/%m/%d").date()
        return dt
    except:
        return None

def main():
    # 매번 오늘 날짜로 바꿔도 됨 = date.today()
    target_date = date(2025,7,31)

    url = "https://www.ohtashp.com/topics/takarakuji/loto6/"
    res = requests.get(url)
    res.encoding = 'utf-8'  # 명시적으로 UTF-8로 설정
    soup = BeautifulSoup(res.text, 'html.parser')

    table = soup.find("table", class_="table")
    if not table:
        print("❌ 당첨 번호 테이블을 찾지 못했습니다.")
        return

    rows = table.find_all("tr")
    found_data = None

    for row in rows[2:]:
        cols = row.find_all(["td", "th"])
        if len(cols) < 12:
            continue

        round_num = cols[0].get_text(strip=True)
        draw_date_str = cols[1].get_text(strip=True)
        draw_date = parse_date_jp(draw_date_str)
        carryover_str = cols[-1].get_text(strip=True)

        if draw_date == target_date:
            found_data = {
                "round": round_num,
                "date": draw_date,
                "carryover": carryover_str
            }
            break

    if not found_data:
        print(f"📅 {target_date}에 해당하는 추첨 데이터가 없습니다. 작업 종료.")
        return

    if found_data["carryover"] != "0円":
        title = f"ロト6 {found_data['round']} ({found_data['carryover']}) キャリーオーバー発生"
        body = title
        create_github_issue(title, body)
    else:
        print("캐리오버 없음. 이슈 생성하지 않음.")

if __name__ == "__main__":
    main()
