"""Unit-Tests fuer die Normalisierungshilfsfunktionen in tools/_datalib.py."""

from __future__ import annotations

from _datalib import normalize_doi


def test_normalize_doi_unifies_all_common_prefix_forms():
    forms = [
        "doi:10.1000/example",
        "DOI: 10.1000/example",
        "https://doi.org/10.1000/example",
        "http://dx.doi.org/10.1000/example",
        "10.1000/example",
    ]
    normalized = {normalize_doi(form) for form in forms}
    assert normalized == {"10.1000/example"}, normalized
