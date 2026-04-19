import json
import logging
from typing import Optional

import requests
from requests import RequestException

import api
from constants import (
    PUSHPLUS_URL,
    PUSHPLUS_TITLE,
    REQUEST_TIMEOUT,
)
from config import settings

logger = logging.getLogger(__name__)


class PushPlus:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.url = PUSHPLUS_URL
        self.timeout = REQUEST_TIMEOUT

    def send(self, title: str, message: str) -> None:
        if not self.token:
            logger.warning("未配置PushPlus Token，跳过推送")
            return

        logger.info("开始推送消息到 PushPlus...")
        data = {
            "token": self.token,
            "title": title,
            "content": message,
            "template": "txt"
        }

        try:
            response = requests.post(
                self.url,
                data=data,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 200:
                logger.error(f"PushPlus推送失败: {result.get('msg', '未知错误')}")
            else:
                logger.info("PushPlus推送成功")
        except RequestException as e:
            logger.error(f"PushPlus请求失败: {str(e)}")
        except json.JSONDecodeError:
            logger.error(f"PushPlus响应解析失败")


def main() -> None:
    logger.info("===== 签到脚本开始执行 =====")

    push_client = PushPlus(token=settings.pushplus_token)

    try:
        with api.API(cookie=settings.cookie) as api_client:
            api_client.get_uid()
            api_client.get_csrf_token()

            is_signed = api_client.get_sign_status()
            if is_signed:
                logger.info("用户已签到")
                push_client.send(title=PUSHPLUS_TITLE, message=f"用户{api_client.uid}已签到，无需重复操作")
                logger.info("===== 签到脚本执行完毕 =====")
                return

            sign_msg = api_client.do_sign()
            logger.info("签到成功")
            push_client.send(title=PUSHPLUS_TITLE, message=f"用户{api_client.uid} {sign_msg}")

    except api.RegexMatchException as e:
        error_msg = f"正则匹配失败: {str(e)}"
    except api.JSONParseException as e:
        error_msg = f"JSON解析失败: {str(e)}"
    except api.BBSAPIException as e:
        error_msg = f"API操作失败: {str(e)}"
    except Exception as e:
        error_msg = f"错误: {str(e)}"
    else:
        error_msg = ""

    if error_msg:
        logger.error(error_msg)
        push_client.send(title=f"{PUSHPLUS_TITLE} (失败)", message=error_msg)

    logger.info("===== 签到脚本执行完毕 =====")


if __name__ == "__main__":
    main()
