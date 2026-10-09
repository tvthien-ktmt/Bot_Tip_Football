import pytest
from backend.app.math.tip_engine import TipEngine


def test_tip_engine_positive_edge():
    engine = TipEngine(min_edge=0.025, min_ev=0.030)
    
    # Model 55%, Market Fair 50%, Odds 2.00 -> Edge 5%, EV = 0.55*1 - 0.45 = +0.10 (+10%)
    res = engine.evaluate_market_selection(
        market="AH",
        selection="Arsenal -0.5",
        line=-0.5,
        odds=2.00,
        model_prob=0.55,
        fair_prob=0.50
    )
    assert res is not None
    assert res["confidence_grade"] in ("A", "B")
    assert res["edge"] == 0.05
    assert res["ev"] == 0.10
    assert res["stake_suggestion"] <= 0.02
    assert res["risk_warning"] is None


def test_tip_engine_no_edge():
    engine = TipEngine(min_edge=0.025, min_ev=0.030)
    
    # Model 51%, Fair 50%, Odds 1.95 -> Edge 1% (< 2.5%) -> Should be filtered out
    res = engine.evaluate_market_selection(
        market="1X2",
        selection="Home",
        line=None,
        odds=1.95,
        model_prob=0.51,
        fair_prob=0.50
    )
    assert res is None


def test_tip_engine_divergence_penalty():
    engine = TipEngine(min_edge=0.025, min_ev=0.030, max_divergence=0.12)
    
    # Model 65%, Market Fair 50% -> Divergence 15% (>12%)
    res = engine.evaluate_market_selection(
        market="OU",
        selection="Over 2.5",
        line=2.5,
        odds=2.00,
        model_prob=0.65,
        fair_prob=0.50
    )
    assert res is not None
    assert res["risk_warning"] is not None
    assert "Cảnh báo" in res["risk_warning"]
    # Due to penalty, confidence should be downgraded
    assert res["confidence_grade"] in ("C", "D")
