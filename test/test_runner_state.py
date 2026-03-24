from state.runner_state import RunnerState

def test_runner_state_metadata():
    r = RunnerState(
        selection_id=101,
        name="Horse A",
        adjustment_factor=12.3,
        handicap=0.0
    )

    assert(r.selection_id==101)
    assert(r.name=="Horse A")
    assert(r.adjustment_factor==12.3)
    assert(r.handicap==0.0)