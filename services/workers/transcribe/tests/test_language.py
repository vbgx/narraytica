from __future__ import annotations

import sys
from pathlib import Path

# Make transcribe/src importable for tests
HERE = Path(__file__).resolve()
TRANSCRIBE_SRC = HERE.parents[1] / "src"
sys.path.insert(0, str(TRANSCRIBE_SRC))

from lang import detect_language, normalize_language  # noqa: E402


def test_normalize_language() -> None:
    assert normalize_language("fr") == "fr"
    assert normalize_language("FR") == "fr"
    assert normalize_language("fr-FR") == "fr"
    assert normalize_language("en_US") == "en"
    assert normalize_language("") is None


def test_detect_language_deterministic() -> None:
    fr = "Ceci est un test et ce n'est pas compliqué, avec des mots en français."
    en = "This is a test and it is not complicated, with common English words."
    de = "Das ist ein Test und das ist nicht kompliziert, mit deutschen Wörtern."
    es = "Esto es una prueba y no es complicado, con palabras en español."
    it = "Questo è un test e non è complicato, con parole in italiano."

    assert detect_language(fr) == "fr"
    assert detect_language(en) == "en"
    assert detect_language(de) == "de"
    assert detect_language(es) == "es"
    assert detect_language(it) == "it"
