from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from models import CardData

PROMPT_TEMPLATE = """You are a language learning assistant.
For the given word or phrase, provide:
1. Russian translation
2. One example sentence in the original language
3. The same example sentence translated to Russian

Respond strictly in this format:
Translation: <translation>
Example EN: <example in original language>
Example RU: <example in Russian>

Word/phrase: {word}"""


class GigaChatError(Exception):
    pass


class GigaChatService:
    def __init__(self, client: GigaChat):
        self._client = client

    async def generate_card(self, word: str) -> CardData:
        try:
            response = await self._client.achat(
                Chat(
                    messages=[
                        Messages(
                            role=MessagesRole.USER,
                            content=PROMPT_TEMPLATE.format(word=word),
                        )
                    ]
                )
            )
            back = response.choices[0].message.content.strip()
            return CardData(front=word, back=back)
        except Exception as e:
            raise GigaChatError(f"Failed to generate card: {e}") from e
