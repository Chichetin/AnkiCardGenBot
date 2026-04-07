from __future__ import annotations

from dataclasses import dataclass

from openai import AsyncOpenAI


@dataclass
class CardData:
    word: str
    translation_ru: str
    description: str


class QwenCardGenerator:
    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def _ask(self, system_prompt: str, user_prompt: str, max_tokens: int = 250) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content or ""
        return content.strip()

    async def translate_to_russian(self, word: str) -> str:
        return await self._ask(
            system_prompt=(
                "You are a precise bilingual dictionary assistant. "
                "Translate input to Russian and return only the best translation, no extra text."
            ),
            user_prompt=f"Translate to Russian: {word}",
            max_tokens=40,
        )

    async def build_description(self, word: str, translation_ru: str) -> str:
        return await self._ask(
            system_prompt=(
                "You create concise learner-friendly vocabulary notes for Anki. "
                "Keep response under 120 words."
            ),
            user_prompt=(
                f"Word: {word}\n"
                f"Russian translation: {translation_ru}\n"
                "Create: part of speech, short meaning, and one English example sentence "
                "with Russian translation."
            ),
            max_tokens=220,
        )

    async def generate_card(self, word: str) -> CardData:
        translation = await self.translate_to_russian(word)
        description = await self.build_description(word, translation)

        return CardData(word=word, translation_ru=translation, description=description)

