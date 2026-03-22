# runner_state.py

class RunnerState:
    """
    Holds both static metadata and dynamic state for a single runner.
    """

    def __init__(
        self,
        selection_id: int,
        name: str = None,
        adjustment_factor: float = None,
        handicap: float = 0.0
    ):
        # -------- Static metadata (from marketDefinition) --------
        self.selection_id = selection_id
        self.name = name
        self.adjustment_factor = adjustment_factor
        self.handicap = handicap

        # -------- Dynamic state (from rc deltas) --------
        self.ltp = None                   # Last traded price
        self.total_traded_volume = 0.0    # 'tv'
        self.status = "ACTIVE"            # ACTIVE / REMOVED / WINNER / LOSER

        # Price ladders (lists of [price, size])
        self.atb = []   # Available to back
        self.atl = []   # Available to lay
        self.trd = []   # Traded volume ladder

    def apply_delta(self, rc: dict):
        """
        Applies a runner change (rc) delta to this runner's state.
        Only updates fields present in the delta.
        """

        if "ltp" in rc:
            self.ltp = rc["ltp"]

        if "tv" in rc:
            self.total_traded_volume = rc["tv"]

        if "atb" in rc:
            self.atb = rc["atb"]

        if "atl" in rc:
            self.atl = rc["atl"]

        if "trd" in rc:
            self.trd = rc["trd"]

        if "hc" in rc:
            self.handicap = rc["hc"]

        if "status" in rc:
            self.status = rc["status"]
