from __future__ import annotations

from typing import NamedTuple

import httpx

from hashtag_enricher.enricher.notify import alert


class _MockSettings(NamedTuple):
    telegram_token: str
    telegram_chat_id: str
    telegram_prefix: str


def _mock_settings(
    *,
    token: str = "123:ABC",
    chat_id: str = "-100123",
    prefix: str = "test",
) -> _MockSettings:
    """Minimal mock object with Telegram fields for testing."""
    return _MockSettings(
        telegram_token=token,
        telegram_chat_id=chat_id,
        telegram_prefix=prefix,
    )


def test_sends_to_telegram_api(monkeypatch):
    calls = []

    def fake_post(url, **kw):
        calls.append({"url": url, "json": kw.get("json")})
        return type("R", (), {"is_success": True})()

    monkeypatch.setattr("hashtag_enricher.notify.httpx.post", fake_post)
    alert("hello", _mock_settings())
    assert len(calls) == 1
    assert "api.telegram.org/bot123:ABC/sendMessage" in calls[0]["url"]
    assert "[test] hello" in calls[0]["json"]["text"]


def test_missing_token_skips(monkeypatch):
    calls = []

    def fake_post():
        calls.append(1)

    monkeypatch.setattr("hashtag_enricher.notify.httpx.post", fake_post)
    alert("hi", _mock_settings(token=""))
    assert calls == []


def test_missing_chat_id_skips(monkeypatch):
    calls = []

    def fake_post():
        calls.append(1)

    monkeypatch.setattr("hashtag_enricher.notify.httpx.post", fake_post)
    alert("hi", _mock_settings(chat_id=""))
    assert calls == []


def test_exception_is_swallowed(monkeypatch):
    def boom():
        raise httpx.ConnectError("down", request=None)

    monkeypatch.setattr("hashtag_enricher.notify.httpx.post", boom)
    alert("hi", _mock_settings())  # Does not raise
