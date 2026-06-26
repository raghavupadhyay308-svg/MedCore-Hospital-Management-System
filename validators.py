"""
validators.py
Small, dependency-free input validation helpers shared across the GUI.
"""
import re
import datetime

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9]{7,15}$")


def is_valid_email(s):
    return bool(s) and bool(EMAIL_RE.match(s.strip()))


def is_valid_phone(s):
    return bool(s) and bool(PHONE_RE.match(s.strip()))


def is_non_empty(s):
    return bool(s) and bool(s.strip())


def is_valid_age(age):
    try:
        a = int(age)
        return 0 < a < 130
    except (TypeError, ValueError):
        return False


def qdate_to_iso(qdate):
    """Convert a QDate to 'YYYY-MM-DD'."""
    return qdate.toString("yyyy-MM-dd")


def iso_to_display(iso_date):
    """Convert 'YYYY-MM-DD' to 'DD Mon YYYY' for friendlier display."""
    try:
        d = datetime.datetime.strptime(iso_date, "%Y-%m-%d")
        return d.strftime("%d %b %Y")
    except (ValueError, TypeError):
        return iso_date


def hour_label(h):
    """24h int -> '09:00 AM' style label."""
    try:
        h = int(h)
    except (TypeError, ValueError):
        return str(h)
    suffix = "AM" if h < 12 else "PM"
    hh = h % 12
    if hh == 0:
        hh = 12
    return f"{hh:02d}:00 {suffix}"
