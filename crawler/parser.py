from utils.text import clean_text


KEYWORDS = ["夏令营", "推免", "推荐免试", "招生", "优秀大学生", "保研", "免试研究生"]
EXCLUDE_KEYWORDS = ["就业", "招聘", "招标", "采购", "讲座", "论坛", "会议"]


def is_valid(title):
    title = clean_text(title)
    if not title:
        return False
    if any(k in title for k in EXCLUDE_KEYWORDS):
        return False
    return any(k in title for k in KEYWORDS)


def parse_date(text):
    text = clean_text(text)
    # Minimal placeholder: many school list pages put dates outside <a>.
    # Keep empty when no date is reliably available.
    return ""
