"""Unit tests for odds conversion functions."""

import pytest
from sim.odds import american_to_implied_prob, normalize_probs


def test_american_to_implied_prob_negative():
    """Test conversion of negative American odds."""
    # -1200 should give ~0.923
    prob = american_to_implied_prob(-1200)
    assert abs(prob - 0.9230769230769231) < 1e-10


def test_american_to_implied_prob_positive():
    """Test conversion of positive American odds."""
    # +800 should give ~0.111
    prob = american_to_implied_prob(800)
    assert abs(prob - 0.1111111111111111) < 1e-10


def test_american_to_implied_prob_even():
    """Test conversion of even money."""
    prob = american_to_implied_prob(100)
    assert abs(prob - 0.5) < 1e-10


def test_normalize_probs():
    """Test probability normalization."""
    probs = {"A": 0.6, "B": 0.5}
    normalized = normalize_probs(probs)
    
    assert abs(normalized["A"] - 0.5454545454545454) < 1e-10
    assert abs(normalized["B"] - 0.45454545454545453) < 1e-10
    assert abs(sum(normalized.values()) - 1.0) < 1e-10


def test_normalize_probs_single():
    """Test normalization with single probability."""
    probs = {"A": 0.5}
    normalized = normalize_probs(probs)
    assert normalized["A"] == 1.0


def test_normalize_probs_zero_sum():
    """Test normalization raises error for zero sum."""
    probs = {"A": 0.0, "B": 0.0}
    with pytest.raises(ValueError, match="cannot be zero"):
        normalize_probs(probs)

