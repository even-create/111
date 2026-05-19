import re


SPACE_RE = re.compile(r"\s+")


def clean_text(text):
    if not text:
        return ""
    return SPACE_RE.sub(" ", text).strip()
