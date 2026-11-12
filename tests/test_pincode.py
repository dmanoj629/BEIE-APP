"""Unit tests for PIN code resolution and fallback."""

from beie.ingest.pincode import resolve_pincode


def test_valid_bengaluru_pincode():
    res = resolve_pincode("560001")
    assert res["status"] == "success"
    assert "Bengaluru" in res["district"] or "Bangalore" in res["district"]
    assert res["state"] == "Karnataka"


def test_valid_shivamogga_pincode():
    res = resolve_pincode("577427")
    assert res["status"] == "success"
    assert "Karnataka" in res["state"]
    assert "Shivamogga" in res["district"] or "Shimoga" in res["district"]


def test_invalid_length_pincode():
    res = resolve_pincode("123")
    assert res["status"] == "error"
    assert "6 digits" in res["message"]


def test_offline_fallback():
    # Test a prefix from offline dictionary
    res = resolve_pincode("580020")
    assert res["status"] == "success"
    assert "Hubli-Dharwad" in res["district"] or "Karnataka" in res["state"]
