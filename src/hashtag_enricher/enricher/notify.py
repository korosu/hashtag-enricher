"""notify.py — Telegram alerts for hashtag-enricher."""

from __future__ import annotations

from typing import Protocol

import httpx


class _TelegramSettings(Protocol):
    @property
    def telegram_token(self) -> str: ...
    @property
    def telegram_chat_id(self) -> str: ...
    @property
    def telegram_prefix(self) -> str: ...


def alert(msg: str, settings: _TelegramSettings) -> None:
    if not settings.telegram_token or not settings.telegram_chat_id:
        return
    text = f"[{settings.telegram_prefix}] {msg}" if settings.telegram_prefix else msg
    url = f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage"
    try:
        r = httpx.post(
            url,
            json={"chat_id": settings.telegram_chat_id, "text": text},
            timeout=10.0,
        )
        if not r.is_success:
            print(
                f"[{settings.telegram_prefix}] Telegram returned {r.status_code}: "
                f"{r.text.strip()[:200]}"
            )
    except Exception as exc:
        print(f"[{settings.telegram_prefix}] Telegram send failed: {exc}")
