"""Monte Carlo simulation engine for boxing matches."""

import numpy as np
from typing import List

from sim.model import SimulationParams, FightResult, OddsConfig
from sim.odds import american_to_implied_prob, normalize_probs


class SimulationEngine:
    """Monte Carlo simulation engine for boxing match outcomes."""
    
    def __init__(self, params: SimulationParams):
        """
        Initialize simulation engine.
        
        Args:
            params: Simulation parameters including odds and round distributions
        """
        self.params = params
        self.rng = np.random.default_rng(params.seed)
        
        # Pre-compute probabilities
        self._compute_probabilities()
    
    def _compute_probabilities(self):
        """Pre-compute all outcome probabilities from odds."""
        odds = self.params.odds
        
        # Convert odds to probabilities
        probs = {
            "joshua_ko": american_to_implied_prob(odds.joshua_ko),
            "joshua_decision": american_to_implied_prob(odds.joshua_decision),
            "paul_ko": american_to_implied_prob(odds.paul_ko),
            "paul_decision": american_to_implied_prob(odds.paul_decision),
        }
        
        if self.params.enable_draw:
            probs["draw"] = american_to_implied_prob(odds.draw)
        
        # Normalize to remove vig
        self.normalized_probs = normalize_probs(probs)
        
        # Compute cumulative probabilities for sampling
        outcomes = ["joshua_ko", "joshua_decision", "paul_ko", "paul_decision"]
        if self.params.enable_draw:
            outcomes.append("draw")
        
        self.outcomes = outcomes
        self.cumulative_probs = np.cumsum([self.normalized_probs[outcome] for outcome in outcomes])
    
    def reseed(self, seed: int):
        """Reseed the random number generator."""
        self.rng = np.random.default_rng(seed)
        self.params.seed = seed
    
    def simulate_batch(self, count: int, start_id: int = 0) -> List[FightResult]:
        """
        Simulate a batch of fights.
        
        Args:
            count: Number of simulations to run
            start_id: Starting simulation ID
        
        Returns:
            List of FightResult objects
        """
        results = []
        
        # Sample outcomes
        outcome_samples = self.rng.random(count)
        outcome_indices = np.searchsorted(self.cumulative_probs, outcome_samples)
        
        for i in range(count):
            outcome_idx = outcome_indices[i]
            outcome = self.outcomes[outcome_idx]
            sim_id = start_id + i
            
            # Determine winner and method
            if outcome == "joshua_ko":
                winner = "Joshua"
                method = "KO/TKO/DQ"
                # Sample round from Joshua's KO distribution
                round_num = self._sample_round(self.params.round_dist.joshua_ko_rounds)
            elif outcome == "joshua_decision":
                winner = "Joshua"
                method = "Decision"
                round_num = 9  # Decision goes to scorecards
            elif outcome == "paul_ko":
                winner = "Paul"
                method = "KO/TKO/DQ"
                # Sample round from Paul's KO distribution
                round_num = self._sample_round(self.params.round_dist.paul_ko_rounds)
            elif outcome == "paul_decision":
                winner = "Paul"
                method = "Decision"
                round_num = 9  # Decision goes to scorecards
            else:  # draw
                winner = "Draw"
                method = "Decision"
                round_num = 9
            
            results.append(FightResult(
                sim_id=sim_id,
                winner=winner,
                method=method,
                round=round_num
            ))
        
        return results
    
    def _sample_round(self, round_probs: List[float]) -> int:
        """
        Sample a round from the given distribution.
        
        Args:
            round_probs: List of 8 probabilities (one per round)
        
        Returns:
            Round number (1-8)
        """
        # Use cumulative probabilities for efficient sampling
        cum_probs = np.cumsum(round_probs)
        sample = self.rng.random()
        round_idx = np.searchsorted(cum_probs, sample)
        return min(round_idx + 1, 8)  # Convert to 1-indexed, cap at 8

