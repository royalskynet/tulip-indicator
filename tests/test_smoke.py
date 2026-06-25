"""Self-check: percentile, spread alignment, merge, CLI overrides, scoring."""
from tulip import fred, score
from tulip.cli import merge, parse_set

def test_percentile_high():
    s = [("d4",10),("d3",8),("d2",6),("d1",4)]  # latest=10 is max -> 100
    _, p = fred.percentile_high(s, window=4)
    assert p == 100.0, p

def test_percentile_mid():
    s = [("d4",6),("d3",10),("d2",8),("d1",4)]  # latest=6, <=6 count=2 of 4 -> 50
    _, p = fred.percentile_high(s, window=4)
    assert p == 50.0, p

def test_spread_align():
    hy = [("d2",10),("d1",8)]
    ig = [("d2",4),("d1",3)]   # spreads: 6, 5; latest 6 -> 100
    _, p = fred.spread_percentile(hy, ig, window=2)
    assert p == 100.0, p

def test_merge_overlay_wins():
    base = {"M1":{"a":10}}; overlay = {"M1":{"a":99,"b":1}}
    out = merge(base, overlay)
    assert out == {"M1":{"a":99,"b":1}}, out

def test_parse_set_none():
    o = parse_set(["M1.a=42","M2.b=none"])
    assert o == {"M1":{"a":42.0},"M2":{"b":None}}, o

def test_display_breakpoint():
    assert score.to_display(70) == 90.0
    assert score.to_display(0) == 0.0
    assert score.to_display(100) == 100.0

def test_band_lookup():
    assert score.band(89)[0] == "警戒/逐步退場"
    assert score.band(95)[0] == "進行中/太晚"

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print(f"✓ {name}")
    print("all good")
