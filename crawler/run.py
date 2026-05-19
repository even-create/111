from crawler.base import fetch, normalize_link, parse_html
from crawler.parser import is_valid, parse_date
from crawler.schools import SCHOOLS
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

    for school in SCHOOLS:
        name = school["name"]

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

                saved = save_post(name, title, link, date)
                if not saved:
                    continue

                new_count += 1
                print(f"[NEW] {name} {title} {link}")
                push(
                    f"新保研通知：{name}",
                    f"{title}\n\n{link}",
                )

    print(f"crawler finished, new posts: {new_count}")
    return new_count
