import os
import json
import datetime
import pyarrow as pa
import pyarrow.parquet as pq

SNAPSHOT_SCHEMA = pa.schema([
    pa.field("timestamp",            pa.int64()),
    pa.field("market_id",            pa.string()),
    pa.field("event_id",             pa.string()),
    pa.field("event_type_id",        pa.string()),
    pa.field("market_type",          pa.string()),
    pa.field("number_of_winners",    pa.int64()),
    pa.field("in_play",              pa.bool_()),
    pa.field("market_status",        pa.string()),
    pa.field("market_total_matched", pa.float64()),
    pa.field("seconds_to_off",       pa.int64()),
    pa.field("selection_id",         pa.int64()),
    pa.field("runner_name",          pa.string()),
    pa.field("adjustment_factor",    pa.float64()),
    pa.field("handicap",             pa.float64()),
    pa.field("runner_status",        pa.string()),
    pa.field("ltp",                  pa.float64()),
    pa.field("total_traded_volume",  pa.float64()),
    pa.field("atb",                  pa.string()),
    pa.field("atl",                  pa.string()),
    pa.field("trd",                  pa.string()),
])


class SnapshotEmitter:
    """
    Receives per-market snapshots from SnapshotClock and streams them to
    Parquet files — one file per market.
    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self._writers = {}  # market_id -> pq.ParquetWriter

    def emit(self, snapshot_ts: int, market_state):
        """
        Called by SnapshotClock for every market at every 1-second tick.
        Builds one row per runner and writes to the market's Parquet file.
        """
        seconds_to_off = None
        if market_state.market_start_time:
            market_start_ms = _parse_market_time_to_ms(market_state.market_start_time)
            seconds_to_off = (market_start_ms - snapshot_ts) // 1000

        for runner in market_state.runners.values():
            row = {
                "timestamp":            snapshot_ts,
                "market_id":            market_state.market_id,
                "event_id":             market_state.event_id,
                "event_type_id":        market_state.event_type_id,
                "market_type":          market_state.market_type,
                "number_of_winners":    market_state.number_of_winners,
                "in_play":              market_state.in_play,
                "market_status":        market_state.status,
                "market_total_matched": market_state.total_matched,
                "seconds_to_off":       seconds_to_off,
                "selection_id":         runner.selection_id,
                "runner_name":          runner.name,
                "adjustment_factor":    runner.adjustment_factor,
                "handicap":             runner.handicap,
                "runner_status":        runner.status,
                "ltp":                  runner.ltp,
                "total_traded_volume":  runner.total_traded_volume,
                "atb":                  json.dumps(runner.atb),
                "atl":                  json.dumps(runner.atl),
                "trd":                  json.dumps(runner.trd),
            }
            self._process_row(market_state.market_id, row)

    def _process_row(self, market_id: str, row: dict):
        """
        Writes one row to the Parquet file for this market.
        Creates the ParquetWriter on first call for each market.
        """
        writer = self._get_or_create_writer(market_id)
        table = pa.Table.from_pydict(
            {k: [v] for k, v in row.items()},
            schema=SNAPSHOT_SCHEMA
        )
        writer.write_table(table)

    def _get_or_create_writer(self, market_id: str) -> pq.ParquetWriter:
        if market_id not in self._writers:
            os.makedirs(self.output_dir, exist_ok=True)
            filename = market_id.replace(".", "_") + ".parquet"
            path = os.path.join(self.output_dir, filename)
            self._writers[market_id] = pq.ParquetWriter(path, SNAPSHOT_SCHEMA)
        return self._writers[market_id]

    def close(self):
        """
        Flushes and closes all open ParquetWriters.
        Must be called after process_file() completes.
        """
        for writer in self._writers.values():
            writer.close()
        self._writers.clear()


def _parse_market_time_to_ms(market_time_str: str) -> int:
    dt = datetime.datetime.fromisoformat(market_time_str.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)
