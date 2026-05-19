import re

from utils.text import clean_text


KEYWORDS = [
    "夏令营",
    "预推免",
    "推免",
    "推荐免试",
    "招生",
    "优秀大学生",
    "保研",
    "免试研究生",
    "接收免试",
]
EXCLUDE_KEYWORDS = ["就业", "招聘", "招标", "采购", "讲座", "论坛", "会议"]
DATE_PATTERNS = [
    re.compile(r"(20\d{2})[-./年](\d{1,2})[-./月](\d{1,2})日?"),
    re.compile(r"\[(20\d{2})-(\d{1,2})-(\d{1,2})\]"),
    re.compile(r"(20\d{2})(\d{2})(\d{2})"),
]


def is_valid(title):
    title = clean_text(title)
    if not title:
        return False
    if any(k in title for k in EXCLUDE_KEYWORDS):
        return False
    return any(k in title for k in KEYWORDS)


def parse_date(text):
    text = clean_text(text)
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        year, month, day = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    return ""


def parse_year(title, date=""):
    text = f"{date} {title}"
    match = re.search(r"(20\d{2})", text)
    return match.group(1) if match else ""


def detect_category(title):
    title = clean_text(title)
    if "夏令营" in title or "优秀大学生" in title:
        return "夏令营"
    if "预推免" in title:
        return "预推免"
    if any(k in title for k in ["推免", "推荐免试", "免试研究生", "接收免试", "保研"]):
        return "推免"
    if "招生" in title:
        return "招生"
    return "其他"
