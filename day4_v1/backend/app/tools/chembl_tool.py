"""ChEMBL REST API lookup tool — compound/target/bioactivity data (drug-discovery domain)."""
from __future__ import annotations

import requests

from backend.app.tools.schemas import ChemblLookupInput

CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"

TOOL_SPEC = {
    "name": "chembl_lookup",
    "description": (
        "Look up a compound or biological target in ChEMBL. For compounds, "
        "returns ChEMBL ID, preferred name, and mechanism-of-action data. For "
        "targets, returns ChEMBL target ID, name, and organism."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Compound name, ChEMBL ID, or target name"},
            "kind": {"type": "string", "enum": ["compound", "target"], "default": "compound"},
        },
        "required": ["query"],
    },
}


def _search_compound(query: str) -> dict:
    resp = requests.get(
        f"{CHEMBL_BASE}/molecule/search",
        params={"q": query, "format": "json", "limit": 5},
        timeout=15,
    )
    resp.raise_for_status()
    molecules = resp.json().get("molecules", [])
    results = []
    for m in molecules:
        chembl_id = m.get("molecule_chembl_id")
        moa_results = []
        if chembl_id:
            moa_resp = requests.get(
                f"{CHEMBL_BASE}/mechanism",
                params={"molecule_chembl_id": chembl_id, "format": "json"},
                timeout=15,
            )
            if moa_resp.ok:
                moa_results = [
                    {
                        "mechanism_of_action": mech.get("mechanism_of_action"),
                        "target_chembl_id": mech.get("target_chembl_id"),
                        "action_type": mech.get("action_type"),
                    }
                    for mech in moa_resp.json().get("mechanisms", [])
                ]
        results.append(
            {
                "chembl_id": chembl_id,
                "pref_name": m.get("pref_name"),
                "max_phase": m.get("max_phase"),
                "molecule_type": m.get("molecule_type"),
                "mechanisms_of_action": moa_results,
            }
        )
    return {"results": results}


def _search_target(query: str) -> dict:
    resp = requests.get(
        f"{CHEMBL_BASE}/target/search",
        params={"q": query, "format": "json", "limit": 5},
        timeout=15,
    )
    resp.raise_for_status()
    targets = resp.json().get("targets", [])
    results = [
        {
            "target_chembl_id": t.get("target_chembl_id"),
            "pref_name": t.get("pref_name"),
            "organism": t.get("organism"),
            "target_type": t.get("target_type"),
        }
        for t in targets
    ]
    return {"results": results}


def chembl_lookup(input: ChemblLookupInput) -> dict:
    if input.kind == "target":
        return _search_target(input.query)
    return _search_compound(input.query)
