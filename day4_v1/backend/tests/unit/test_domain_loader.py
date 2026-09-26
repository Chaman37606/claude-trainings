import pytest

from backend.app.domains.loader import (
    DomainNotFoundError,
    list_domain_names,
    load_domain,
)


def test_list_domain_names_includes_expected_domains():
    names = list_domain_names()
    assert "general_biomedical" in names
    assert "drug_discovery" in names


def test_load_general_biomedical_domain():
    domain = load_domain("general_biomedical")
    assert domain.name == "general_biomedical"
    assert "pubmed_search" in domain.allowed_tools
    assert domain.extraction_schema is None


def test_load_drug_discovery_domain_has_extraction_schema():
    domain = load_domain("drug_discovery")
    assert domain.extraction_schema is not None
    assert domain.extraction_schema["additionalProperties"] is False
    assert "chembl_lookup" in domain.allowed_tools


def test_unknown_domain_raises():
    with pytest.raises(DomainNotFoundError):
        load_domain("not_a_real_domain")
