from backend.app.rag.chunker import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_short_text_returns_single_chunk():
    chunks = chunk_text("hello world", chunk_size=800, overlap=120)
    assert len(chunks) == 1
    assert chunks[0].text == "hello world"


def test_long_text_splits_with_overlap():
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=800, overlap=120)
    assert len(chunks) > 1
    # consecutive chunks overlap: end of chunk i should reappear at the start of chunk i+1
    assert chunks[0].text[-120:] == chunks[1].text[:120]


def test_overlap_must_be_smaller_than_chunk_size():
    import pytest

    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, overlap=100)
