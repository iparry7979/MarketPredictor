from state.market_state import MarketState
from state.runner_state import RunnerState

def test_apply_market_definition_populates_metadata_and_runners():
    md = {
        "eventId": "123",
        "eventTypeId": "7",
        "marketType": "WIN",
        "numberOfWinners": 1,
        "marketTime": "2024-01-01T12:00:00Z",
        "runners": [
            {"id": 101, "name": "Horse A", "adjustmentFactor": 12.3},
            {"id": 102, "name": "Horse B", "adjustmentFactor": 8.7}
        ]
    }

    m = MarketState("1.234567")
    m.apply_market_definition(md)

    assert m.event_id == "123"
    assert m.event_type_id == "7"
    assert m.market_type == "WIN"
    assert m.number_of_winners == 1
    assert m.market_start_time == "2024-01-01T12:00:00Z"

    assert len(m.runners) == 2
    assert m.runners[101].name == "Horse A"
    assert m.runners[101].adjustment_factor == 12.3

def test_apply_market_delta_updates_runner_state():
    m = MarketState("1.234567")

    # Create runner first
    m.runners[101] = RunnerState(101)

    delta = {
        "id": "1.234567",
        "tv": 2000,
        "rc": [
            {"id": 101, "ltp": 5.2, "tv": 1000}
        ]
    }

    m.apply_market_delta(1700000000000, delta)

    assert m.total_matched == 2000
    assert m.timestamp == 1700000000000
    assert m.runners[101].ltp == 5.2
    assert m.runners[101].total_traded_volume == 1000
