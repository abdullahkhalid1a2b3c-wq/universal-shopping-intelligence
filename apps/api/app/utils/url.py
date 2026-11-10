"""URL normalization utilities for e-commerce product links."""

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_TRACKING_PARAMS = frozenset(
    {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "fbclid",
        "gclid",
        "ref",
        "source",
        "_pos",
        "_sid",
        "_ss",
        "variant",
    }
)


def normalize_product_url(url: str) -> str:
    """Normalize a product URL for canonical matching.

    - Lowers scheme and host
    - Strips common marketing and tracking query parameters
    - Strips URL fragments (#)
    - Removes trailing slashes on paths
    """
    if not url:
        return ""

    parsed = urlparse(url.strip())
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()

    # Filter query parameters
    filtered_queries = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=False)
        if k.lower() not in _TRACKING_PARAMS
    ]
    query = urlencode(filtered_queries)

    # Normalize path
    path = parsed.path.rstrip("/") if len(parsed.path) > 1 else parsed.path

    return urlunparse((scheme, netloc, path, "", query, ""))

