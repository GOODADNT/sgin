import base64
import logging
from typing import Final

REQUEST_TIMEOUT: Final[int] = 10
DEFAULT_USER_AGENT: Final[str] = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0'
)

SIGN_STATUS_SIGNED: Final[str] = "已签到"
SIGN_SUCCESS_CODE: Final[int] = 0

BBS_BASE_URL_ENCODED: Final[str] = "aHR0cHM6Ly9iYnMua2FueHVlLmNvbQ=="
BBS_USER_CENTER_URL_ENCODED: Final[str] = "aHR0cHM6Ly9wYXNzcG9ydC5rYW54dWUuY29tL3VzZXItY2VudGVyLmh0bQ=="
BBS_SIGN_URL_ENCODED: Final[str] = "dXNlci1zaWduaW4uaHRt"
BBS_IS_SIGN_URL_ENCODED: Final[str] = "dXNlci1pc19zaWduaW4uaHRt"


def decode_base64_url(encoded_str: str) -> str:
    return base64.b64decode(encoded_str).decode("utf-8")


BBS_BASE_URL: Final[str] = decode_base64_url(BBS_BASE_URL_ENCODED)
BBS_SIGN_URL: Final[str] = f"{BBS_BASE_URL}/{decode_base64_url(BBS_SIGN_URL_ENCODED)}"
BBS_IS_SIGN_URL: Final[str] = f"{BBS_BASE_URL}/{decode_base64_url(BBS_IS_SIGN_URL_ENCODED)}"
BBS_USER_CENTER_URL: Final[str] = decode_base64_url(BBS_USER_CENTER_URL_ENCODED)

PUSHPLUS_URL: Final[str] = "https://www.pushplus.plus/send"
PUSHPLUS_TITLE: Final[str] = "论坛签到结果"

LOG_LEVEL: Final[int] = logging.INFO
LOG_FORMAT: Final[str] = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
LOG_ENCODING: Final[str] = "utf-8"
