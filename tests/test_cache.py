from backbone.cache import DiskCache


def test_key_is_stable_and_sensitive(tmp_path):
    c = DiskCache(tmp_path)
    m = [{"role": "user", "content": "hi"}]
    k1 = c.make_key("a", m, {"t": 0})
    assert k1 == c.make_key("a", m, {"t": 0})
    assert k1 != c.make_key("b", m, {"t": 0})
    assert k1 != c.make_key("a", m, {"t": 1})


def test_get_set_roundtrip(tmp_path):
    c = DiskCache(tmp_path)
    assert c.get("missing") is None
    c.set("k", "hello")
    assert c.get("k") == "hello"
