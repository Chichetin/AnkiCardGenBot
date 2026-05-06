from services.word_queue import WordQueue


def test_pop_returns_pushed_words_in_fifo_order():
    q = WordQueue()
    q.push("hello")
    q.push("world")

    assert q.pop() == "hello"
    assert q.pop() == "world"


def test_pop_returns_none_when_empty():
    q = WordQueue()
    assert q.pop() is None


def test_size_reflects_current_count():
    q = WordQueue()
    assert q.size() == 0
    q.push("a")
    q.push("b")
    assert q.size() == 2
    q.pop()
    assert q.size() == 1
