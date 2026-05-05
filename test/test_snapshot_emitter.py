import tempfile
import os
import pyarrow.parquet as pq
from output.snapshot_emitter import SnapshotEmitter, _parse_market_time_to_ms
from state.market_state import MarketState
from state.runner_state import RunnerState


def _make_market():
    """Helper: build a MarketState with 2 runners for testing."""
    m = MarketState("1.999")
    m.event_id = "555"
    m.event_type_id = "7"
    m.market_type = "WIN"
    m.number_of_winners = 1
    m.market_start_time = "2024-06-01T14:00:00Z"
    m.in_play = False
    m.status = "OPEN"
    m.total_matched = 5000.0

    r1 = RunnerState(selection_id=101, name="Horse A", adjustment_factor=12.3, handicap=0.0)
    r1.ltp = 3.5
    r1.total_traded_volume = 1000.0
    r1.atb = [[3.4, 50.0]]
    r1.atl = [[3.6, 30.0]]
    r1.trd = [[3.5, 100.0]]

    r2 = RunnerState(selection_id=102, name="Horse B", adjustment_factor=8.7, handicap=0.0)
    r2.ltp = 5.0
    r2.total_traded_volume = 800.0

    m.runners = {101: r1, 102: r2}
    return m


def test_emit_writes_one_row_per_runner():
    market = _make_market()

    with tempfile.TemporaryDirectory() as tmpdir:
        emitter = SnapshotEmitter(output_dir=tmpdir)
        emitter.emit(snapshot_ts=1000000, market_state=market)
        emitter.close()

        parquet_path = os.path.join(tmpdir, "1_999.parquet")
        assert os.path.exists(parquet_path), "Parquet file was not created"

        table = pq.read_table(parquet_path)
        assert table.num_rows == 2


def test_emit_correct_column_values():
    market = _make_market()

    with tempfile.TemporaryDirectory() as tmpdir:
        emitter = SnapshotEmitter(output_dir=tmpdir)
        emitter.emit(snapshot_ts=1000000, market_state=market)
        emitter.close()

        table = pq.read_table(os.path.join(tmpdir, "1_999.parquet"))

        # Find the row for runner 101
        selection_ids = table.column("selection_id").to_pylist()
        idx = selection_ids.index(101)

        assert table.column("market_id")[idx].as_py() == "1.999"
        assert table.column("event_id")[idx].as_py() == "555"
        assert table.column("market_type")[idx].as_py() == "WIN"
        assert table.column("ltp")[idx].as_py() == 3.5
        assert table.column("total_traded_volume")[idx].as_py() == 1000.0
        assert table.column("atb")[idx].as_py() == "[[3.4, 50.0]]"
        assert table.column("runner_name")[idx].as_py() == "Horse A"
        assert table.column("in_play")[idx].as_py() == False


def test_emit_seconds_to_off():
    """seconds_to_off should reflect the gap between snapshot_ts and market start."""
    market = _make_market()
    market_start_ms = _parse_market_time_to_ms(market.market_start_time)
    snapshot_ts = market_start_ms - 60_000  # 60 seconds before off

    with tempfile.TemporaryDirectory() as tmpdir:
        emitter = SnapshotEmitter(output_dir=tmpdir)
        emitter.emit(snapshot_ts=snapshot_ts, market_state=market)
        emitter.close()

        table = pq.read_table(os.path.join(tmpdir, "1_999.parquet"))
        assert all(v == 60 for v in table.column("seconds_to_off").to_pylist())


def test_multiple_snapshots_accumulate_rows():
    """Two emit() calls should produce 4 rows total (2 runners × 2 snapshots)."""
    market = _make_market()

    with tempfile.TemporaryDirectory() as tmpdir:
        emitter = SnapshotEmitter(output_dir=tmpdir)
        emitter.emit(snapshot_ts=1000000, market_state=market)
        emitter.emit(snapshot_ts=2000000, market_state=market)
        emitter.close()

        table = pq.read_table(os.path.join(tmpdir, "1_999.parquet"))
        assert table.num_rows == 4
