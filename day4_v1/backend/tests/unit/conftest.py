import pytest

from backend.app.rag import vector_store


@pytest.fixture
def isolated_chroma(tmp_path, monkeypatch):
    """Points Chroma at a throwaway temp dir so vector-store tests don't
    collide with each other or with real dev data in backend/chroma_data.
    """
    monkeypatch.setattr(vector_store, "_client", None)
    import backend.app.config as config_module

    monkeypatch.setattr(config_module.settings, "chroma_persist_dir", str(tmp_path))
    vector_store.get_collection.cache_clear()
    yield
    vector_store.get_collection.cache_clear()
    vector_store._client = None
