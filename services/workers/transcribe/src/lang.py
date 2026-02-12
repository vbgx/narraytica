from __future__ import annotations

import re
from typing import Any

_LANG_RE = re.compile(r"^[a-zA-Z]{2,3}([_-][a-zA-Z]{2})?$")


def normalize_language(lang: str | None) -> str | None:
    if not lang:
        return None
    x = lang.strip().replace("_", "-")
    if not x:
        return None

    if not _LANG_RE.match(x):
        x = x.split("-")[0]

    x = x.lower()
    if len(x) < 2:
        return None
    return x[:2]


def extract_language_hint(payload: dict[str, Any] | None) -> str | None:
    """
    Best-effort extraction of language hint from job payload.
    Backward-compatible key scan.
    """
    if not payload:
        return None

    candidates: list[Any] = [
        payload.get("language"),
        payload.get("language_hint"),
        (payload.get("metadata") or {}).get("language"),
        (payload.get("video") or {}).get("language"),
        (payload.get("source") or {}).get("language"),
    ]
    for c in candidates:
        if isinstance(c, str):
            norm = normalize_language(c)
            if norm:
                return norm
    return None


def _tokens(text: str) -> list[str]:
    # Unicode letters only; excludes digits/underscores.
    return re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)


def detect_language(text: str | None) -> str:
    """
    Deterministic, dependency-free heuristic detection.
    Returns a 2-letter code.

    Strategy:
      - tokenize (Unicode letters)
      - score by small high-signal stopword sets per language
      - stable tie-breaker by fixed language order
    """
    if not text:
        return "en"

    tokens = _tokens(text)
    if not tokens:
        return "en"

    stop: dict[str, set[str]] = {
        # Major Western
        "en": {
            "the",
            "and",
            "is",
            "are",
            "to",
            "of",
            "in",
            "for",
            "that",
            "this",
            "with",
            "on",
            "not",
            "you",
            "it",
            "as",
            "be",
        },
        "fr": {
            "le",
            "la",
            "les",
            "des",
            "un",
            "une",
            "et",
            "est",
            "pour",
            "dans",
            "que",
            "qui",
            "avec",
            "sur",
            "pas",
            "plus",
            "ce",
            "ça",
        },
        "de": {
            "der",
            "die",
            "das",
            "und",
            "ist",
            "für",
            "nicht",
            "mit",
            "auf",
            "ein",
            "eine",
            "dass",
            "zu",
            "im",
            "in",
        },
        "es": {
            "el",
            "la",
            "los",
            "las",
            "y",
            "es",
            "para",
            "en",
            "que",
            "con",
            "no",
            "más",
            "por",
            "una",
            "un",
            "esto",
        },
        "it": {
            "il",
            "lo",
            "la",
            "gli",
            "le",
            "e",
            "è",
            "per",
            "che",
            "con",
            "non",
            "più",
            "una",
            "un",
            "nel",
        },
        "pt": {
            "o",
            "a",
            "os",
            "as",
            "e",
            "é",
            "para",
            "em",
            "que",
            "com",
            "não",
            "mais",
            "por",
            "uma",
            "um",
        },
        "nl": {
            "de",
            "het",
            "een",
            "en",
            "is",
            "voor",
            "in",
            "met",
            "niet",
            "op",
            "dat",
            "dit",
            "van",
        },
        # Nordics
        "sv": {
            "och",
            "att",
            "det",
            "som",
            "är",
            "för",
            "med",
            "inte",
            "på",
            "en",
            "ett",
        },
        "no": {
            "og",
            "å",
            "det",
            "som",
            "er",
            "for",
            "med",
            "ikke",
            "på",
            "en",
            "et",
        },
        "da": {
            "og",
            "at",
            "det",
            "som",
            "er",
            "for",
            "med",
            "ikke",
            "på",
            "en",
            "et",
        },
        "fi": {
            "ja",
            "on",
            "että",
            "se",
            "kun",
            "tai",
            "ei",
            "olen",
            "ovat",
            "mitä",
        },
        "is": {
            "og",
            "að",
            "það",
            "sem",
            "er",
            "fyrir",
            "með",
            "ekki",
            "á",
        },
        # Baltics
        "et": {"ja", "on", "et", "see", "kui", "ei", "mis", "või"},
        "lv": {"un", "ir", "ka", "tas", "ar", "ne", "vai", "par"},
        "lt": {"ir", "kad", "tai", "su", "ne", "ar", "į", "už"},
        # Slavic (Latin)
        "pl": {"i", "że", "to", "na", "w", "z", "nie", "jest", "dla"},
        "cs": {"a", "že", "to", "na", "v", "s", "se", "není", "pro"},
        "sk": {"a", "že", "to", "na", "v", "s", "sa", "nie", "pre"},
        "sl": {"in", "je", "da", "na", "v", "z", "se", "ni", "za"},
        "hr": {"i", "je", "da", "na", "u", "s", "se", "nije", "za"},
        "bs": {"i", "je", "da", "na", "u", "s", "se", "nije", "za"},
        "sr": {"i", "je", "da", "na", "u", "s", "se", "nije", "za"},
        # Balkans / East
        "ro": {"și", "este", "în", "la", "cu", "nu", "pentru", "că", "din"},
        "hu": {"és", "hogy", "nem", "van", "egy", "a", "az", "mert", "mint"},
        "bg": {"и", "е", "да", "на", "в", "с", "не", "за", "като"},
        "mk": {"и", "е", "да", "на", "во", "со", "не", "за", "како"},
        "sq": {"dhe", "është", "në", "me", "jo", "për", "që", "nga"},
        "el": {"και", "είναι", "το", "η", "να", "με", "σε", "για", "όχι"},
        "tr": {"ve", "bir", "bu", "için", "ile", "değil", "çok", "ama", "da"},
        # Iberian regional
        "ca": {"i", "és", "per", "amb", "no", "que", "en", "el", "la"},
        "eu": {"eta", "da", "ez", "bat", "hau", "zeren", "arekin", "den"},
        "gl": {"e", "é", "para", "con", "non", "que", "en", "o", "a"},
        # Celtic + Maltese
        "ga": {"agus", "atá", "ní", "ar", "go", "le", "an", "na"},
        "cy": {"a", "yn", "i", "y", "o", "ar", "nid", "gyda", "mae"},
        "mt": {"u", "huwa", "li", "fil", "ma", "għal", "ta", "għand", "biex"},
        # Cyrillic-heavy (still Europe)
        "uk": {"і", "в", "на", "що", "не", "це", "як", "з", "для"},
        "ru": {"и", "в", "на", "что", "не", "это", "как", "с", "для"},
        "be": {"і", "ў", "на", "што", "не", "гэта", "як", "з", "для"},
    }

    scores = {k: 0 for k in stop}
    for t in tokens:
        for lang, words in stop.items():
            if t in words:
                scores[lang] += 1

    # Stable tie-breaker (priority order)
    order = [
        "fr",
        "en",
        "de",
        "es",
        "it",
        "pt",
        "nl",
        "sv",
        "no",
        "da",
        "fi",
        "is",
        "et",
        "lv",
        "lt",
        "pl",
        "cs",
        "sk",
        "sl",
        "hr",
        "bs",
        "sr",
        "ro",
        "hu",
        "bg",
        "mk",
        "sq",
        "el",
        "tr",
        "ca",
        "eu",
        "gl",
        "ga",
        "cy",
        "mt",
        "uk",
        "ru",
        "be",
    ]
    # If everything is 0, default to English
    if all(v == 0 for v in scores.values()):
        return "en"

    return max(order, key=lambda k: scores.get(k, 0))
