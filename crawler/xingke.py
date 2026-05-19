import time

import requests

from crawler.parser import detect_category, parse_year
from crawler.schools import SCHOOLS
from storage.db import save_post


DATA_URL = "https://xingkebaoyan.com/data.json"
LAW_KEYWORDS = ["法学", "法学院", "法律", "国际法", "知识产权", "涉外法治", "纪检监察"]
TARGET_CATEGORIES = ["夏令营", "预推免", "推免"]


def fetch_items():
    res = requests.get(
        DATA_URL,
        params={"t": int(time.time())},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15,
    )
    res.raise_for_status()
    data = res.json()
    return data.get("items", [])


def school_type_map():
    return {item["name"]: item["type"] for item in SCHOOLS}


def is_law_item(item):
    haystack = " ".join(
        str(item.get(key) or "")
        for key in ["category_tag", "subject", "major", "department", "title"]
    )
    return any(keyword in haystack for keyword in LAW_KEYWORDS)


def is_target_category(item):
    category = item.get("category") or detect_category(item.get("title") or "")
    title_category = detect_category(item.get("title") or "")
    haystack = f"{category} {title_category} {item.get('title') or ''}"
    return any(keyword in haystack for keyword in TARGET_CATEGORIES)


def normalize_item(item, school_types):
    title = item.get("title") or ""
    date = (item.get("signup_start") or item.get("created_at") or "")[:10]
    detected_category = detect_category(title)
    category = item.get("category") or detected_category
    if detected_category in TARGET_CATEGORIES and category not in TARGET_CATEGORIES:
        category = detected_category
    year = parse_year(title, item.get("event_start") or item.get("signup_end") or date)

    return {
        "school": item.get("school") or "",
        "school_type": school_types.get(item.get("school") or "", item.get("level") or ""),
        "title": title,
        "url": item.get("url") or f"https://xingkebaoyan.com/detail.html?id={item.get('id')}",
        "date": date,
        "category": "预推免" if "预推免" in category else category,
        "year": year,
        "department": item.get("department") or "",
        "province": item.get("province") or "",
        "subject": item.get("subject") or "",
        "major": item.get("major") or "",
        "level": item.get("level") or "",
        "signup_start": item.get("signup_start") or "",
        "signup_end": item.get("signup_end") or "",
        "signup_end_text": item.get("signup_end_text") or "",
        "event_time_text": item.get("event_time_text") or "",
        "source": "xingke",
        "external_id": str(item.get("id") or ""),
    }


def sync_law_items():
    school_types = school_type_map()
    saved_count = 0
    matched_count = 0

    for item in fetch_items():
        if not is_law_item(item):
            continue
        if not is_target_category(item):
            continue

        normalized = normalize_item(item, school_types)
        if not normalized["school"] or not normalized["title"] or not normalized["url"]:
            continue

        matched_count += 1
        if save_post(**normalized):
            saved_count += 1

    return {"matched": matched_count, "saved": saved_count}
