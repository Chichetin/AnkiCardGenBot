import pytest
import aiohttp
from aioresponses import aioresponses
from services.anki import AnkiService, AnkiError


ANKI_URL = "http://localhost:8765"


@pytest.fixture
def service():
    return AnkiService(base_url=ANKI_URL)


@pytest.mark.asyncio
async def test_get_decks_returns_deck_names(service):
    with aioresponses() as m:
        m.post(ANKI_URL, payload={"result": ["Default", "Spanish", "Japanese"], "error": None})

        decks = await service.get_decks()

    assert decks == ["Default", "Spanish", "Japanese"]


@pytest.mark.asyncio
async def test_get_decks_raises_when_anki_unavailable(service):
    with aioresponses() as m:
        m.post(ANKI_URL, exception=aiohttp.ClientConnectionError())

        with pytest.raises(AnkiError):
            await service.get_decks()


@pytest.mark.asyncio
async def test_add_note_succeeds(service):
    with aioresponses() as m:
        m.post(ANKI_URL, payload={"result": 1234567890, "error": None})

        await service.add_note("Default", "hello", "привет\nExample EN: Hello!\nExample RU: Привет!")


@pytest.mark.asyncio
async def test_add_note_raises_on_failure(service):
    with aioresponses() as m:
        m.post(ANKI_URL, payload={"result": None, "error": "deck not found"})

        with pytest.raises(AnkiError):
            await service.add_note("NonExistent", "hello", "привет")
