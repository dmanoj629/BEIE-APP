"""Number verifier tests — hallucination detection."""

from beie.explain.verifier import verify_response


def test_all_numbers_grounded_passes():
    data = {"P50": 0.52, "P10": 0.21, "P90": 0.83}
    text = "The median impact is 0.52 percentage points."
    assert verify_response(text, data) is True


def test_hallucinated_number_fails():
    data = {"P50": 0.52, "P10": 0.21, "P90": 0.83}
    text = "The median impact is 1.75 percentage points."  # 1.75 not in data
    assert verify_response(text, data) is False


def test_ordinal_numbers_allowed():
    """Small integers 1–100 are allowed as ordinals."""
    data = {"P50": 5.5}
    text = "The 1st step caused a 5.5 point increase in 3 months."
    # 1, 3 are small ordinals; 5.5 is grounded
    assert verify_response(text, data) is True
