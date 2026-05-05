import datetime

def emit_snapshot(snapshot_ts, market_state):
    if market_state.market_start_time:
        market_start_ms = parse_market_time_to_ms(market_state.market_start_time)
        seconds_to_off = (market_start_ms - snapshot_ts) // 1000
    else:
        seconds_to_off = None
    
    for runner_id, runner in market_state.runners.items():
        row = {
            "timestamp": snapshot_ts,
            "market_id": market_state.market_id,
            "event_id": market_state.event_id,
            "event_type_id": market_state.event_type_id,
            "market_type": market_state.market_type,
            "number_of_winners": market_state.number_of_winners,
            "in_play": market_state.in_play,
            "market_status": market_state.status,
            "market_total_matched": market_state.total_matched,
            "seconds_to_off": seconds_to_off,

            "selection_id": runner.selection_id,
            "runner_name": runner.name,
            "adjustment_factor": runner.adjustment_factor,
            "handicap": runner.handicap,
            "runner_status": runner.status,

            "ltp": runner.ltp,
            "total_traded_volume": runner.total_traded_volume,
            "atb": runner.atb,
            "atl": runner.atl,
            "trd": runner.trd,
        }

        # This is where we will later pass the row to your parquet writer. Not defined yet.
        process_snapshot_row(row)
        
def parse_market_time_to_ms(market_time_str):
    # Example: "2024-01-01T12:00:00Z"
    dt = datetime.datetime.fromisoformat(market_time_str.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)