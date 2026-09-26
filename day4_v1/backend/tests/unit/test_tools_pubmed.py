import responses

from backend.app.tools.pubmed_tool import EUTILS_BASE, pubmed_search
from backend.app.tools.schemas import PubmedSearchInput


@responses.activate
def test_pubmed_search_parses_results():
    responses.get(
        f"{EUTILS_BASE}/esearch.fcgi",
        json={"esearchresult": {"idlist": ["111", "222"]}},
    )
    responses.get(
        f"{EUTILS_BASE}/esummary.fcgi",
        json={
            "result": {
                "111": {"title": "Paper One.", "fulljournalname": "J One", "pubdate": "2024"},
                "222": {"title": "Paper Two.", "fulljournalname": "J Two", "pubdate": "2023"},
            }
        },
    )
    responses.get(
        f"{EUTILS_BASE}/efetch.fcgi",
        body="Abstract for paper one.\n\n\nAbstract for paper two.",
    )

    result = pubmed_search(PubmedSearchInput(query="egfr inhibitors", max_results=2))

    assert len(result["results"]) == 2
    first = result["results"][0]
    assert first["pmid"] == "111"
    assert first["title"] == "Paper One"
    assert first["url"] == "https://pubmed.ncbi.nlm.nih.gov/111/"
    assert "Abstract for paper one" in first["abstract"]


@responses.activate
def test_pubmed_search_returns_empty_when_no_hits():
    responses.get(
        f"{EUTILS_BASE}/esearch.fcgi",
        json={"esearchresult": {"idlist": []}},
    )

    result = pubmed_search(PubmedSearchInput(query="a very obscure query", max_results=5))

    assert result == {"results": []}
