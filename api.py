import json
import re
import logging
from http.cookies import SimpleCookie
from typing import Dict, Optional, Any

import requests
from requests import Session, RequestException

from constants import (
    REQUEST_TIMEOUT,
    DEFAULT_USER_AGENT,
    BBS_BASE_URL,
    BBS_SIGN_URL,
    BBS_IS_SIGN_URL,
    BBS_USER_CENTER_URL,
    SIGN_STATUS_SIGNED,
    SIGN_SUCCESS_CODE
)
from exceptions import BBSAPIException, RegexMatchException, JSONParseException

logger = logging.getLogger(__name__)


class API:

    def __init__(self, cookie: str, user_agent: Optional[str] = None):
        if not cookie.strip():
            raise BBSAPIException("Cookie不能为空")

        self.cookie: Dict[str, str] = self.cookie_to_dict(cookie)
        self.uid: Optional[str] = None
        self.csrf_token: Optional[str] = None
        self.user_agent: str = user_agent or DEFAULT_USER_AGENT

        self.session: Session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.session.cookies.update(self.cookie)

    @property
    def user_task_url(self) -> str:
        if not self.uid:
            raise BBSAPIException("UID未初始化")
        return f"{BBS_BASE_URL}/user-tasks-{self.uid}-1.htm"

    @staticmethod
    def cookie_to_dict(cookie_str: str) -> dict:
        cookie = SimpleCookie()
        cookie.load(cookie_str)
        return {k: v.value for k, v in cookie.items()}

    def _request(self, method: str, url: str, **kwargs) -> Any:
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=REQUEST_TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            return response
        except RequestException as e:
            raise BBSAPIException(f"请求失败: {str(e)}") from e

    def get_uid(self) -> str:
        if self.uid:
            return self.uid

        logger.info("开始获取用户 UID...")
        response = self._request("GET", BBS_USER_CENTER_URL)
        response_str = response.text.strip()

        if not response_str:
            raise BBSAPIException("未获取到用户信息")

        match = re.search(r"var\s+uid\s*=\s*'(\d+)'\s*;", response_str)
        if not match:
            raise RegexMatchException(f"未匹配到UID, 响应内容摘要: {response_str[:200]}")

        self.uid = match.group(1)
        logger.info(f"获取 UID 成功")
        return self.uid

    def get_csrf_token(self) -> str:
        logger.info("开始获取 CSRF Token...")

        response = self._request("GET", self.user_task_url)
        response_str = response.text.strip()

        if not response_str:
            raise BBSAPIException("未获取到用户任务页面信息")

        match = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', response_str)
        if not match:
            raise RegexMatchException(f"未匹配到CSRF Token，响应内容摘要: {response_str[:200]}")

        self.csrf_token = match.group(1)
        logger.info("获取 CSRF Token 成功")
        return self.csrf_token

    def get_sign_status(self) -> bool:
        logger.info("开始检查签到状态...")

        response = self._request("GET", BBS_IS_SIGN_URL)

        try:
            result = response.json()
        except json.JSONDecodeError:
            raise JSONParseException(f"JSON解析错误, 响应内容摘要: {response.text[:200]}")

        is_signed = result.get("message") == SIGN_STATUS_SIGNED
        logger.info(f"签到状态检查完成: {'已签到' if is_signed else '未签到'}")
        return is_signed

    def do_sign(self) -> str:
        logger.info("开始执行签到操作...")

        if not self.csrf_token:
            raise BBSAPIException("CSRF Token未初始化，请先调用get_csrf_token()")

        data = {"csrf_token": self.csrf_token}
        response = self._request("POST", BBS_SIGN_URL, data=data)

        try:
            result = response.json()
        except json.JSONDecodeError:
            raise JSONParseException(f"JSON解析错误, 响应内容摘要: {response.text[:200]}")

        if result.get("code") == SIGN_SUCCESS_CODE:
            logger.info("签到成功")
            return f"签到成功，获得数量: {result.get('message', '未知数量')}"
        else:
            raise BBSAPIException(f"签到失败: {result.get('message', '未知错误')}")

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
