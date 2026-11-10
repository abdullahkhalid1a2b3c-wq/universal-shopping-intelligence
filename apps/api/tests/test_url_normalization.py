"""Unit tests for URL normalization matching extension tests."""

import pytest
from app.utils.url import normalize_product_url

TEST_CASES = [
    (
        "https://outfitters.com.pk/products/classic-tee/?utm_source=facebook&utm_medium=cpc&variant=12345#reviews",
        "https://outfitters.com.pk/products/classic-tee",
    ),
    (
        "HTTP://KHAADI.COM/products/kurta-01/?fbclid=XYZ&color=blue",
        "http://khaadi.com/products/kurta-01?color=blue",
    ),
    (
        "https://sapphireonline.pk/products/shirt/",
        "https://sapphireonline.pk/products/shirt",
    ),
    (
        "https://breakout.com.pk/?ref=home",
        "https://breakout.com.pk/",
    ),
    (
        "https://diners.com.pk/products/suit-99?gclid=abc&source=instagram&_pos=1&_sid=2&_ss=r&size=38",
        "https://diners.com.pk/products/suit-99?size=38",
    ),
    ("", ""),
]


@pytest.mark.parametrize("raw_url,expected", TEST_CASES)
def test_normalize_product_url(raw_url: str, expected: str):
    assert normalize_product_url(raw_url) == expected
