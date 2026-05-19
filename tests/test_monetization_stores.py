import pytest

from igkit.monetization.deals import DealStore
from igkit.monetization.links import LinkRegistry


def test_link_registry_add_get_click(tmp_path):
    reg = LinkRegistry(tmp_path / "l.db")
    link = reg.add_link(
        "shop", "https://shop.example/p/1", link_type="product", campaign="spring"
    )
    assert link.slug == "shop"
    assert "utm_campaign=spring" in link.destination
    reg.record_click("shop")
    reg.record_click("shop")
    assert reg.get("shop").clicks == 2
    assert reg.export_bio()[0]["type"] == "product"
    reg.close()


def test_link_registry_rejects_bad_type(tmp_path):
    reg = LinkRegistry(tmp_path / "l.db")
    with pytest.raises(ValueError):
        reg.add_link("x", "https://e.example", link_type="bogus")
    reg.close()


def test_deal_pipeline_value(tmp_path):
    store = DealStore(tmp_path / "d.db")
    a = store.add("Acme", fee=1000.0)
    store.add("Beta", fee=500.0)
    store.set_stage(a, "paid")
    totals = store.pipeline_value()
    assert totals["paid"] == 1000.0
    assert totals["lead"] == 500.0
    with pytest.raises(ValueError):
        store.set_stage(a, "not-a-stage")
    store.close()


def test_brand_profile_stable_json(tmp_path):
    from igkit.content.models import BrandProfile

    p = tmp_path / "brand.json"
    p.write_text(
        '{"name":"N","niche":"fitness","audience":"runners","voice":"warm"}',
        encoding="utf-8",
    )
    brand = BrandProfile.load(p)
    # Deterministic: sorted keys, identical across calls.
    assert brand.stable_json() == brand.stable_json()
    assert brand.stable_json().index('"audience"') < brand.stable_json().index('"voice"')
