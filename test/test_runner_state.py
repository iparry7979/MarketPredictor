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
    
def test_apply_delta():
    r = RunnerState(
        selection_id=101,
        name="Horse A",
        adjustment_factor=12.3,
        handicap=0.0
    )
    
    rc = {
        "ltp": 6.2,
        "tv": 13145.26,
        "atb":[
            [3.5, 124.5],
            [3.45, 166.6]],
        "atl":[
            [3.55, 255.12],
            [3.60, 0]],
        "trd":[
            [3.5, 1000],
            [3.55, 1]],
        "hc": 21.1,
        "status": "INACTIVE"}
    
    r.apply_delta(rc)
    
    print("ltp = ", r.ltp)
    
    assert(r.ltp==6.2)
    assert(r.total_traded_volume==13145.26)
    assert(r.atb == [[3.5, 124.5],[3.45,166.6]])
    assert(r.atl == [[3.55, 255.12],[3.6, 0]])
    assert(r.trd == [[3.5, 1000],[3.55, 1]])
    assert(r.handicap==21.1)
    assert(r.status=="INACTIVE")
    
def test_partial_delta():
    r = RunnerState(101)
    r.ltp = 10
    r.total_traded_volume = 500
    
    rc = {"id": 101, "ltp": 9.8}
    
    r.apply_delta(rc)
    
    assert(r.ltp == 9.8)
    assert(r.total_traded_volume == 500)
    
    
        
    
    