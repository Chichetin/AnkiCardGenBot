from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    qwen_api_key: str
    qwen_model: str
    qwen_base_url: str
    anki_connect_url: str



def load_settings() -> Settings:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    qwen_api_key = os.getenv("QWEN_API_KEY", "").strip()

    if not telegram_bot_token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment.")
    if not qwen_api_key:
        raise ValueError("Missing QWEN_API_KEY in environment.")

    return Settings(
        telegram_bot_token=telegram_bot_token,
        qwen_api_key=qwen_api_key,
        qwen_model=os.getenv("QWEN_MODEL", "qwen-plus").strip(),
        qwen_base_url=os.getenv(
            "QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        ).strip(),
        anki_connect_url=os.getenv("ANKI_CONNECT_URL", "http://127.0.0.1:8765").strip(),
    )

