from __future__ import annotations

import asyncio
import json
import urllib.request
from dataclasses import dataclass
from typing import Any


class AnkiConnectError(RuntimeError):
    pass


@dataclass
class AnkiConnectClient:
    url: str

    async def invoke(self, action: str, **params: Any) -> Any:
        return await asyncio.to_thread(self._invoke_blocking, action, params)

    def _invoke_blocking(self, action: str, params: dict[str, Any]) -> Any:
        body = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
        request = urllib.request.Request(
            self.url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise AnkiConnectError(
                "Could not reach AnkiConnect. Ensure Anki is open and AnkiConnect is installed."
            ) from exc

        if payload.get("error"):
            raise AnkiConnectError(str(payload["error"]))

        return payload.get("result")

    async def deck_names(self) -> list[str]:
        result = await self.invoke("deckNames")
        return sorted(result or [])

    async def add_basic_note(self, deck_name: str, front: str, back: str, tags: list[str] | None = None) -> int:
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": front, "Back": back},
            "options": {"allowDuplicate": False},
            "tags": tags or ["telegram", "qwen"],
        }
        result = await self.invoke("addNote", note=note)
        if result is None:
            raise AnkiConnectError("Anki rejected the note. It may be a duplicate.")
        return int(result)

    async def sync(self) -> None:
        await self.invoke("sync")

