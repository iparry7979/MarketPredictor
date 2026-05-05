class SnapshotClock:
    """
    Emits time-aligned snapshots at fixed intervals (e.g., every 1 second).
    The clock advances based on incoming Betfair timestamps.
    """

    def __init__(self, interval_ms=1000):
        self.interval_ms = interval_ms
        self.current_snapshot_ts = None  # next snapshot timestamp

    def initialise(self, first_ts):
        """
        Align the first snapshot to the next whole-second boundary.
        """
        # Round up to next second boundary
        remainder = first_ts % self.interval_ms
        if remainder == 0:
            self.current_snapshot_ts = first_ts
        else:
            self.current_snapshot_ts = first_ts + (self.interval_ms - remainder)

    def tick(self, ts, markets, emit_callback):
        """
        Called for every incoming Betfair message timestamp.
        Emits snapshots until the clock catches up to 'ts'.
        """

        # First message: initialise the clock
        if self.current_snapshot_ts is None:
            self.initialise(ts)

        # Emit snapshots until we reach or exceed the message timestamp
        while ts >= self.current_snapshot_ts:
            self.emit_snapshot(self.current_snapshot_ts, markets, emit_callback)
            self.current_snapshot_ts += self.interval_ms

    def emit_snapshot(self, snapshot_ts, markets, emit_callback):
        """
        Emits a snapshot for all markets at the given timestamp.
        Delegates actual writing to the provided callback.
        """
        for market_id, market in markets.items():
            emit_callback(snapshot_ts, market)