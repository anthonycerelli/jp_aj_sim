"""Metrics and aggregation for simulation results."""

from typing import List, Dict
import pandas as pd
import numpy as np

from sim.model import FightResult


class SimulationMetrics:
    """Aggregates and computes statistics from simulation results."""
    
    def __init__(self):
        """Initialize empty metrics tracker."""
        self.results: List[FightResult] = []
        self.history: List[Dict] = []  # For convergence tracking
    
    def add_results(self, results: List[FightResult]):
        """Add new simulation results."""
        self.results.extend(results)
    
    def reset(self):
        """Reset all metrics."""
        self.results = []
        self.history = []
    
    def get_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame."""
        if not self.results:
            return pd.DataFrame(columns=["sim_id", "winner", "method", "round"])
        
        return pd.DataFrame([
            {
                "sim_id": r.sim_id,
                "winner": r.winner,
                "method": r.method,
                "round": r.round,
            }
            for r in self.results
        ])
    
    def get_summary_stats(self) -> Dict[str, float]:
        """
        Compute summary statistics.
        
        Returns:
            Dictionary with win percentages and method percentages
        """
        if not self.results:
            return {
                "total_sims": 0,
                "joshua_win_pct": 0.0,
                "paul_win_pct": 0.0,
                "draw_pct": 0.0,
                "joshua_ko_pct": 0.0,
                "joshua_decision_pct": 0.0,
                "paul_ko_pct": 0.0,
                "paul_decision_pct": 0.0,
            }
        
        total = len(self.results)
        df = self.get_dataframe()
        
        joshua_wins = len(df[df["winner"] == "Joshua"])
        paul_wins = len(df[df["winner"] == "Paul"])
        draws = len(df[df["winner"] == "Draw"])
        
        joshua_ko = len(df[(df["winner"] == "Joshua") & (df["method"] == "KO/TKO/DQ")])
        joshua_dec = len(df[(df["winner"] == "Joshua") & (df["method"] == "Decision")])
        paul_ko = len(df[(df["winner"] == "Paul") & (df["method"] == "KO/TKO/DQ")])
        paul_dec = len(df[(df["winner"] == "Paul") & (df["method"] == "Decision")])
        
        return {
            "total_sims": total,
            "joshua_win_pct": (joshua_wins / total) * 100,
            "paul_win_pct": (paul_wins / total) * 100,
            "draw_pct": (draws / total) * 100,
            "joshua_ko_pct": (joshua_ko / total) * 100,
            "joshua_decision_pct": (joshua_dec / total) * 100,
            "paul_ko_pct": (paul_ko / total) * 100,
            "paul_decision_pct": (paul_dec / total) * 100,
        }
    
    def get_outcome_distribution(self) -> Dict[str, int]:
        """Get count of each outcome type."""
        if not self.results:
            return {
                "Joshua KO/TKO/DQ": 0,
                "Joshua Decision": 0,
                "Paul KO/TKO/DQ": 0,
                "Paul Decision": 0,
                "Draw": 0,
            }
        
        df = self.get_dataframe()
        outcomes = []
        
        for _, row in df.iterrows():
            if row["winner"] == "Draw":
                outcomes.append("Draw")
            else:
                outcomes.append(f"{row['winner']} {row['method']}")
        
        outcome_counts = {
            "Joshua KO/TKO/DQ": outcomes.count("Joshua KO/TKO/DQ"),
            "Joshua Decision": outcomes.count("Joshua Decision"),
            "Paul KO/TKO/DQ": outcomes.count("Paul KO/TKO/DQ"),
            "Paul Decision": outcomes.count("Paul Decision"),
            "Draw": outcomes.count("Draw"),
        }
        
        return outcome_counts
    
    def get_ko_round_distribution(self) -> Dict[str, List[int]]:
        """
        Get KO round distribution for each fighter.
        
        Returns:
            Dictionary with "Joshua" and "Paul" keys, each containing
            a list of 8 counts (one per round)
        """
        if not self.results:
            return {
                "Joshua": [0] * 8,
                "Paul": [0] * 8,
            }
        
        df = self.get_dataframe()
        ko_df = df[df["method"] == "KO/TKO/DQ"]
        
        joshua_rounds = [0] * 8
        paul_rounds = [0] * 8
        
        for _, row in ko_df.iterrows():
            round_num = row["round"] - 1  # Convert to 0-indexed
            if 0 <= round_num < 8:
                if row["winner"] == "Joshua":
                    joshua_rounds[round_num] += 1
                elif row["winner"] == "Paul":
                    paul_rounds[round_num] += 1
        
        return {
            "Joshua": joshua_rounds,
            "Paul": paul_rounds,
        }
    
    def record_history(self, tick: int):
        """Record current metrics for convergence tracking."""
        stats = self.get_summary_stats()
        self.history.append({
            "tick": tick,
            "total_sims": stats["total_sims"],
            "joshua_win_pct": stats["joshua_win_pct"],
            "joshua_ko_pct": stats["joshua_ko_pct"],
        })
    
    def get_convergence_data(self) -> pd.DataFrame:
        """Get convergence history as DataFrame."""
        if not self.history:
            return pd.DataFrame(columns=["tick", "total_sims", "joshua_win_pct", "joshua_ko_pct"])
        return pd.DataFrame(self.history)

