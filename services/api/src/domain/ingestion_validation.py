from __future__ import annotations

from urllib.parse import urlparse, urlunparse

from fastapi import HTTPException, status


def normalize_url(url) -> str:
    s = str(url)
    p = urlparse(s)
    scheme = (p.scheme or "https").lower()
    netloc = p.netloc.lower()
    path = p.path or ""
    q = p.query or ""
    return urlunparse((scheme, netloc, path.rstrip("/"), "", q, ""))


def validate_source_fields(source) -> None:
    kind = getattr(source, "kind", None)
    url = getattr(source, "url", None)
    upload_ref = getattr(source, "upload_ref", None)

    if kind in ("youtube", "external_url"):
        if not url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="source.url is required for youtube/external_url",
            )
    elif kind == "upload":
        if not upload_ref:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="source.upload_ref is required for upload",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid source.kind",
        )
