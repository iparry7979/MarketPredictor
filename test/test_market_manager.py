import io
from engine.market_manager import MarketManager
from parse.historic_file_parser import open_raw_file

def test_market_manager_end_to_end(monkeypatch):
    # Fake Betfair stream with one marketDefinition and one delta
    fake_file = io.StringIO(
        '{"pt": 1000, "mc": [{"id": "1.234", "marketDefinition": {"eventId": "123", "eventTypeId": "7", "marketType": "WIN", "numberOfWinners": 1, "runners": [{"id": 101, "name": "Horse A", "adjustmentFactor": 12.3}]}}]}\n'
        '{"pt": 2000, "mc": [{"id": "1.234", "rc": [{"id": 101, "ltp": 5.0}]}]}\n'
    )

    # Monkeypatch open_raw_file to return our fake file
    monkeypatch.setattr("engine.market_manager.open_raw_file", lambda path: fake_file)

    mm = MarketManager()
    mm.process_file("dummy_path")

    market = mm.markets["1.234"]

    assert market.event_id == "123"
    assert market.market_type == "WIN"
    assert market.runners[101].name == "Horse A"
    assert market.runners[101].ltp == 5.0
