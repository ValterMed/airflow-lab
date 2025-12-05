from app.main import to_ms

def test_to_ms_seconds_to_ms():
    s = 1729550000  # seconds
    ms = to_ms(s)
    assert ms == s * 1000

def test_to_ms_ms_passthrough():
    ms_in = 1729550000000
    ms = to_ms(ms_in)
    assert ms == ms_in
