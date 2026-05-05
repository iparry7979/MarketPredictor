# market_manager.py

from state.market_state import MarketState
from parse.historic_file_parser import (
    raw_message_stream,
    market_definition_stream,
    market_change_stream,
    open_raw_file
)
from engine.snapshot_clock import SnapshotClock

class MarketManager:
    """
    Orchestrates the reconstruction of multiple markets from a raw Betfair file.
    Holds a dictionary of MarketState objects and routes deltas/definitions to them.
    """

    def __init__(self):
        # market_id -> MarketState
        self.markets = {}

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
        Single‑pass reconstruction loop.
        - Reads raw messages in timestamp order
        - Applies market definitions
        - Applies deltas
        - Ticks snapshot clock
        """
       
        for msg in raw_message_stream(path):
           ts = msg["pt"]

           # First pass: market definitions
           #for ts, market_id, md in market_definition_stream(path):
           # self.apply_market_definition(ts, market_id, md)
          
           for mc in msg.get("mc", []):
                if "marketDefinition" in mc:
                    self.apply_market_definition(ts, mc["id"], mc["marketDefinition"])

           # Second pass: market deltas
           #for ts, mc in market_change_stream(path):
           #  self.apply_market_delta(ts, mc)
          
           for mc in msg.get("mc", []):
                if "rc" in mc:
                    self.apply_market_delta(ts, mc)
                    
           SnapshotClock.tick(ts, self.markets, emit_callback)

           # After this, self.markets contains fully reconstructed markets
