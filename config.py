import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

from constants import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, LOG_ENCODING


class LogConfig:

    @staticmethod
    def setup_logging():
        """全局初始化日志（自动调用，无需手动执行）"""
        logging.basicConfig(
            level=LOG_LEVEL,
            format=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
            encoding=LOG_ENCODING
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    cookie: str = ""
    pushplus_token: Optional[str] = None


LogConfig.setup_logging()
logger = logging.getLogger(__name__)

settings = Settings()
if not settings.cookie.strip():
    raise ValueError("配置错误：请在 .env 文件或环境变量中填写 COOKIE")
logger.info("加载配置完成")