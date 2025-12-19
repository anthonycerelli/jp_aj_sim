"""Data models for simulation parameters and results."""

from dataclasses import dataclass
from typing import List


@dataclass
class OddsConfig:
    """Configuration for betting odds."""
    joshua_moneyline: int = -1200
    paul_moneyline: int = 800
    joshua_ko: int = -390
    joshua_decision: int = 450
    paul_ko: int = 1200
    paul_decision: int = 1300
    draw: int = 2500
    total_rounds: int = 8
    
    @property
    def joshua_moneyline_prob(self) -> float:
        """Implied probability for Joshua moneyline."""
        from sim.odds import american_to_implied_prob
        return american_to_implied_prob(self.joshua_moneyline)
    
    @property
    def paul_moneyline_prob(self) -> float:
        """Implied probability for Paul moneyline."""
        from sim.odds import american_to_implied_prob
        return american_to_implied_prob(self.paul_moneyline)


@dataclass
class RoundDistribution:
    """Distribution of KO probabilities across rounds."""
    joshua_ko_rounds: List[float]
    paul_ko_rounds: List[float]
    
    def __post_init__(self):
        """Normalize round distributions to sum to 1.0."""
        if len(self.joshua_ko_rounds) != 8:
            raise ValueError("joshua_ko_rounds must have 8 values")
        if len(self.paul_ko_rounds) != 8:
            raise ValueError("paul_ko_rounds must have 8 values")
        
        if any(p < 0 for p in self.joshua_ko_rounds):
            raise ValueError("joshua_ko_rounds must be non-negative")
        if any(p < 0 for p in self.paul_ko_rounds):
            raise ValueError("paul_ko_rounds must be non-negative")
        
        # Normalize to sum to 1.0
        joshua_sum = sum(self.joshua_ko_rounds)
        paul_sum = sum(self.paul_ko_rounds)
        
        if joshua_sum > 0:
            self.joshua_ko_rounds = [p / joshua_sum for p in self.joshua_ko_rounds]
        if paul_sum > 0:
            self.paul_ko_rounds = [p / paul_sum for p in self.paul_ko_rounds]


@dataclass
class SimulationParams:
    """Parameters for Monte Carlo simulation."""
    odds: OddsConfig
    round_dist: RoundDistribution
    seed: int = 42
    enable_draw: bool = False


@dataclass
class FightResult:
    """Result of a single simulated fight."""
    sim_id: int
    winner: str  # "Joshua", "Paul", or "Draw"
    method: str  # "KO/TKO/DQ" or "Decision"
    round: int  # 1-8 for KO, 9 for Decision

