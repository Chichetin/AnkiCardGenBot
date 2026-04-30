import pytest
from unittest.mock import AsyncMock, MagicMock
from models import CardData
from services.gigachat import GigaChatService, GigaChatError


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.achat = AsyncMock()
    return client


@pytest.fixture
def service(mock_client):
    return GigaChatService(client=mock_client)


@pytest.mark.asyncio
async def test_generate_card_returns_card_data(service, mock_client):
    mock_client.achat.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Translation: привет\nExample EN: Hello, world!\nExample RU: Привет, мир!"))]
    )

    card = await service.generate_card("hello")

    assert isinstance(card, CardData)
    assert card.front == "hello"
    assert card.back != ""


@pytest.mark.asyncio
async def test_generate_card_raises_on_api_failure(service, mock_client):
    mock_client.achat.side_effect = Exception("connection error")

    with pytest.raises(GigaChatError):
        await service.generate_card("hello")
