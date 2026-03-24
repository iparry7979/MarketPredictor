# market_manager.py

from market_state import MarketState
from raw_parser import (
    raw_message_stream,
    market_definition_stream,
    market_change_stream
)

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
    def process_file(self, path: str):
        """
        Processes a raw Betfair file and updates all MarketState objects.
        This is the main entry point for reconstruction.
        """

        # First pass: market definitions
        for ts, market_id, md in market_definition_stream(path):
            self.apply_market_definition(ts, market_id, md)

        # Second pass: market deltas
        for ts, mc in market_change_stream(path):
            self.apply_market_delta(ts, mc)

        # After this, self.markets contains fully reconstructed markets
