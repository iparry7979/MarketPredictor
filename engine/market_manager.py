# market_manager.py

from state.market_state import MarketState
from parse.historic_file_parser import raw_message_stream
from engine.snapshot_clock import SnapshotClock


class MarketManager:
    """
    Orchestrates the reconstruction of multiple markets from a raw Betfair file.
    Holds a dictionary of MarketState objects and routes deltas/definitions to them.
    """

    def __init__(self):
        self.markets = {}                       # market_id -> MarketState
        self.snapshot_clock = SnapshotClock()   # drives 1-second snapshot emission

    # ---------------------------------------------------------
    # MARKET DEFINITION HANDLING
    # ---------------------------------------------------------
    def apply_market_definition(self, ts: int, market_id: str, md: dict):
        """
        Ensures a MarketState exists and applies the marketDefinition metadata.
        """
        market = self.markets.get(market_id)

        if market is None:
            market = MarketState(market_id)
            self.markets[market_id] = market

        market.apply_market_definition(md)

    # ---------------------------------------------------------
    # MARKET DELTA HANDLING
    # ---------------------------------------------------------
    def apply_market_delta(self, ts: int, mc: dict):
        """
        Applies a market change (mc) delta to the appropriate MarketState.
        """
        market_id = mc["id"]

        market = self.markets.get(market_id)

        # If we see a delta before a definition, create the market anyway
        if market is None:
            market = MarketState(market_id)
            self.markets[market_id] = market

        market.apply_market_delta(ts, mc)

    # ---------------------------------------------------------
    # MAIN RECONSTRUCTION LOOP
    # ---------------------------------------------------------
    def process_file(self, path: str, emit_callback):
        """
        Single-pass reconstruction loop.
        - Reads raw messages in timestamp order
        - Applies market definitions and deltas
        - Ticks the snapshot clock to emit 1-second snapshots
        """
        for msg in raw_message_stream(path):
            ts = msg["pt"]

            for mc in msg.get("mc", []):
                if "marketDefinition" in mc:
                    self.apply_market_definition(ts, mc["id"], mc["marketDefinition"])

            for mc in msg.get("mc", []):
                if "rc" in mc:
                    self.apply_market_delta(ts, mc)

            self.snapshot_clock.tick(ts, self.markets, emit_callback)
