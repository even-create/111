from crawler.base import fetch, normalize_link, parse_html
from crawler.parser import detect_category, is_valid, parse_date, parse_year
from crawler.schools import SCHOOLS
from crawler.xingke import sync_law_items
from notify.serverchan import push
from storage.db import init_db, save_post
from utils.text import clean_text


def iter_links(soup, base_url):
    for a in soup.find_all("a"):
        title = clean_text(a.get_text(" ", strip=True))
        link = a.get("href")

        if not title or not link:
            continue

        yield title, normalize_link(base_url, link), parse_date(a.parent.get_text(" ", strip=True))


def run():
    init_db()
    new_count = 0
    sync_result = {"matched": 0, "saved": 0}

    try:
        sync_result = sync_law_items()
        new_count += sync_result["saved"]
        print(f"[XINGKE] matched: {sync_result['matched']}, new: {sync_result['saved']}")
    except Exception as exc:
        print(f"[ERROR] xingke sync failed: {exc}")

    for school in SCHOOLS:
        name = school["name"]
        school_type = school["type"]

        for url in school["urls"]:
            try:
                html = fetch(url)
                soup = parse_html(html)
            except Exception as exc:
                print(f"[ERROR] {name} fetch failed: {url} ({exc})")
                continue

            for title, link, date in iter_links(soup, url):
                if not is_valid(title):
                    continue

                category = detect_category(title)
                year = parse_year(title, date)
                saved = save_post(
                    school=name,
                    school_type=school_type,
                    title=title,
                    url=link,
                    date=date,
                    category=category,
                    year=year,
                    source="school",
                )
                if not saved:
                    continue

                new_count += 1
                print(f"[NEW] {name} {title} {link}")
                push(
                    f"新保研通知：{name}",
                    f"{category}｜{title}\n\n{link}",
                )

    print(f"crawler finished, new posts: {new_count}")
    return new_count
