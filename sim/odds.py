"""Odds conversion utilities."""

from typing import Dict


def american_to_implied_prob(odds: int) -> float:
    """
    Convert American odds to implied probability.
    
    Args:
        odds: American odds (e.g., -1200 or +800)
    
    Returns:
        Implied probability as a float between 0 and 1
    """
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def normalize_probs(probs: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize probabilities to sum to 1.0.
    
    Args:
        probs: Dictionary mapping outcome names to probabilities
    
    Returns:
        Dictionary with normalized probabilities
    
    Raises:
        ValueError: If sum of probabilities is zero
    """
    total = sum(probs.values())
    if total == 0:
        raise ValueError("Sum of probabilities cannot be zero")
    
    return {k: v / total for k, v in probs.items()}

