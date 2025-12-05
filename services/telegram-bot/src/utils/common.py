import re


HH_RESUME_ID_RE = re.compile(r"https?://(?:[\w-]+\.)?hh\.ru/resume/([A-Za-z0-9]+)")


def is_link(text: str) -> bool:
    url_regex = re.compile(r"(https?://\S+)")

    return bool(url_regex.search(text))


def extract_hh_resume_id(text: str) -> str | None:
    match = HH_RESUME_ID_RE.search(text)
    if not match:
        return None

    return match.group(1)
