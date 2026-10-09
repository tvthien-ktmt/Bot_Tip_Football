import pytest
import numpy as np
from backend.app.math.devig import devig_multiplicative, devig_power, devig_shin


def test_devig_sum_to_one():
    # Example 1X2 odds with ~5% margin: 2.10, 3.40, 3.50
    odds = [2.10, 3.40, 3.50]
    
    p_mult = devig_multiplicative(odds)
    p_pow = devig_power(odds)
    p_shin = devig_shin(odds)

    assert len(p_mult) == 3
    assert len(p_pow) == 3
    assert len(p_shin) == 3

    assert sum(p_mult) == pytest.approx(1.0, abs=1e-5)
    assert sum(p_pow) == pytest.approx(1.0, abs=1e-5)
    assert sum(p_shin) == pytest.approx(1.0, abs=1e-5)

    # In Shin and Power, the longshot has a slightly lower fair probability than pure multiplicative
    # (favorite-longshot bias adjustment)
    assert p_shin[0] >= p_mult[0] * 0.98
    assert p_shin[2] <= p_mult[2] * 1.02


def test_devig_even_match():
    # 50-50 market with 10% juice (1.90, 1.90)
    odds = [1.90, 1.90]
    p_shin = devig_shin(odds)
    p_mult = devig_multiplicative(odds)

    assert p_shin[0] == pytest.approx(0.5, abs=1e-4)
    assert p_shin[1] == pytest.approx(0.5, abs=1e-4)
    assert p_mult[0] == pytest.approx(0.5, abs=1e-4)
    assert p_mult[1] == pytest.approx(0.5, abs=1e-4)
