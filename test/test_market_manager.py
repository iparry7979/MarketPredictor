import io
from engine.market_manager import MarketManager

FAKE_DATA = (
    '{"pt": 1000, "mc": [{"id": "1.234", "marketDefinition": {"eventId": "123", "eventTypeId": "7", "marketType": "WIN", "numberOfWinners": 1, "runners": [{"id": 101, "name": "Horse A", "adjustmentFactor": 12.3}]}}]}\n'
    '{"pt": 2000, "mc": [{"id": "1.234", "rc": [{"id": 101, "ltp": 5.0}]}]}\n'
)

def test_market_manager_end_to_end(monkeypatch):
    # Return a fresh StringIO each call so both passes (definitions + deltas) see the full stream
    monkeypatch.setattr("parse.historic_file_parser.open_raw_file", lambda path: io.StringIO(FAKE_DATA))

    mm = MarketManager()
    mm.process_file("dummy_path")

    market = mm.markets["1.234"]

    assert market.event_id == "123"
    assert market.market_type == "WIN"
    assert market.runners[101].name == "Horse A"
    assert market.runners[101].ltp == 5.0
