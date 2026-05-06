from collections import deque


class WordQueue:
    def __init__(self):
        self._items: deque[str] = deque()

    def push(self, word: str) -> None:
        self._items.append(word)

    def pop(self) -> str | None:
        if not self._items:
            return None
        return self._items.popleft()

    def size(self) -> int:
        return len(self._items)
