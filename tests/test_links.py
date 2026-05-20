from urllib.parse import parse_qs, urlparse

import pytest

from igkit.monetization.links import build_utm_url, render_link_in_bio


def test_build_utm_url_adds_params():
    url = build_utm_url(
        "https://shop.example/p/1", campaign="launch", content="reel1"
    )
    q = parse_qs(urlparse(url).query)
    assert q["utm_source"] == ["instagram"]
    assert q["utm_medium"] == ["social"]
    assert q["utm_campaign"] == ["launch"]
    assert q["utm_content"] == ["reel1"]


def test_build_utm_url_preserves_existing_query():
    url = build_utm_url("https://x.example/?ref=abc", campaign="c")
    q = parse_qs(urlparse(url).query)
    assert q["ref"] == ["abc"]
    assert q["utm_campaign"] == ["c"]


def test_build_utm_url_rejects_relative():
    with pytest.raises(ValueError):
        build_utm_url("/not/absolute")


def test_render_link_in_bio_escapes_and_marks_sponsored():
    html_doc = render_link_in_bio(
        [{"title": "A & B", "url": "https://e.example/x?a=1&b=2", "type": "affiliate"}]
    )
    assert "A &amp; B" in html_doc
    assert 'rel="nofollow sponsored noopener"' in html_doc
    assert "&amp;b=2" in html_doc  # query ampersand escaped in HTML attribute
