"""Unit tests for data models."""

import pytest
from sim.model import OddsConfig, RoundDistribution, SimulationParams


def test_round_distribution_normalization():
    """Test that round distributions are normalized."""
    dist = RoundDistribution(
        joshua_ko_rounds=[0.2, 0.2, 0.2, 0.2, 0.1, 0.05, 0.03, 0.02],
        paul_ko_rounds=[0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.1, 0.1],
    )
    
    # Should be normalized to sum to 1.0
    assert abs(sum(dist.joshua_ko_rounds) - 1.0) < 1e-10
    assert abs(sum(dist.paul_ko_rounds) - 1.0) < 1e-10


def test_round_distribution_wrong_length():
    """Test that wrong length raises error."""
    with pytest.raises(ValueError, match="must have 8 values"):
        RoundDistribution(
            joshua_ko_rounds=[0.2, 0.2, 0.2, 0.2],
            paul_ko_rounds=[0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.1, 0.1],
        )


def test_round_distribution_negative():
    """Test that negative probabilities raise error."""
    with pytest.raises(ValueError, match="must be non-negative"):
        RoundDistribution(
            joshua_ko_rounds=[-0.1, 0.2, 0.2, 0.2, 0.1, 0.1, 0.05, 0.05],
            paul_ko_rounds=[0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.1, 0.1],
        )


def test_simulation_params():
    """Test simulation parameters creation."""
    odds = OddsConfig()
    round_dist = RoundDistribution(
        joshua_ko_rounds=[0.2] * 8,
        paul_ko_rounds=[0.125] * 8,
    )
    params = SimulationParams(
        odds=odds,
        round_dist=round_dist,
        seed=42,
    )
    
    assert params.seed == 42
    assert params.odds.total_rounds == 8

