# market_state.py

from runner_state import RunnerState

class MarketState:
    """
    Holds static metadata and dynamic state for a Betfair market.
    Applies market-level and runner-level deltas.
    """

    def __init__(self, market_id: str):
        self.market_id = market_id

        # -------- Static metadata (from marketDefinition) --------
        self.event_id = None
        self.event_type_id = None
        self.market_type = None
        self.number_of_winners = None
        self.market_start_time = None  # Useful for seconds_to_off later

        # -------- Dynamic state (from mc deltas) --------
        self.in_play = False
        self.status = "OPEN"
        self.total_matched = 0.0
        self.version = 0

        # Runner states: selection_id -> RunnerState
        self.runners = {}

        # Last timestamp applied
        self.timestamp = None

    def apply_market_delta(self, ts: int, mc: dict):
        """
        Applies a market change (mc) delta to the market state.
        """

        self.timestamp = ts

        # Market-level dynamic fields
        if "inPlay" in mc:
            self.in_play = mc["inPlay"]

        if "status" in mc:
            self.status = mc["status"]

        if "tv" in mc:
            self.total_matched = mc["tv"]

        if "id" in mc:
            self.version = mc["id"]

        # Runner-level deltas
        for rc in mc.get("rc", []):
            selection_id = rc["id"]

            # Create runner if first time seen
            if selection_id not in self.runners:
                self.runners[selection_id] = RunnerState(selection_id)

            # Apply delta to runner
            self.runners[selection_id].apply_delta(rc)
