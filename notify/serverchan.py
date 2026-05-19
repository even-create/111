import requests

from config import ENABLE_NOTIFY, SERVERCHAN_KEY
from storage.db import get_notify_settings


def push(title, desp):
    settings = get_notify_settings()
    key = settings["serverchan_key"] or SERVERCHAN_KEY
    enabled = settings["enabled"] or ENABLE_NOTIFY

    if not enabled or not key:
        return False

    url = f"https://sctapi.ftqq.com/{key}.send"
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
