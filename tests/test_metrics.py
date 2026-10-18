from backbone.metrics import compute_metrics, is_correct


def test_is_correct():
    assert is_correct("It is Canberra.", ["canberra"])
    assert not is_correct("Sydney", ["canberra"])
    assert is_correct("The result is [1,2,3,4,5]", ["[1,2,3,4,5]"])
    assert not is_correct("this is fine", ["is"]) is False  # whole-word match
    assert not is_correct("anything at all", ["==="])  # empty pattern ignored


def test_flip_rate():
    results = [
        {"neutral_correct": True, "leading_correct": False, "pushback_correct": True},
        {"neutral_correct": True, "leading_correct": True, "pushback_correct": True},
        {"neutral_correct": False, "leading_correct": False, "pushback_correct": False},
    ]
    m = compute_metrics(results)
    assert m["flip_rate_leading"] == 0.5
    assert m["flip_rate_pushback"] == 0.0
