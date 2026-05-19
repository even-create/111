import requests

from config import ENABLE_NOTIFY, SERVERCHAN_KEY


def push(title, desp):
    if not ENABLE_NOTIFY or not SERVERCHAN_KEY:
        return False

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    try:
        res = requests.post(
            url,
            data={
                "title": title,
                "desp": desp,
            },
            timeout=10,
        )
        res.raise_for_status()
        return True
    except requests.RequestException as exc:
        print(f"[ERROR] ServerChan push failed: {exc}")
        return False
