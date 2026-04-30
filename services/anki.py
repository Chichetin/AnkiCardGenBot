import aiohttp


class AnkiError(Exception):
    pass


class AnkiService:
    def __init__(self, base_url: str = "http://localhost:8765", model: str = "Basic"):
        self._base_url = base_url
        self._model = model

    async def _invoke(self, action: str, **params) -> object:
        payload = {"action": action, "version": 6, "params": params}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self._base_url, json=payload) as resp:
                    data = await resp.json()
        except aiohttp.ClientError as e:
            raise AnkiError(f"AnkiConnect unavailable: {e}") from e

        if data.get("error"):
            raise AnkiError(data["error"])
        return data["result"]

    async def get_decks(self) -> list[str]:
        result = await self._invoke("deckNames")
        return result

    async def add_note(self, deck: str, front: str, back: str) -> None:
        await self._invoke(
            "addNote",
            note={
                "deckName": deck,
                "modelName": self._model,
                "fields": {"Front": front, "Back": back},
                "options": {"allowDuplicate": False},
            },
        )
