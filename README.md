# Paul vs Joshua Monte Carlo Simulation

A real-time Monte Carlo simulation dashboard for predicting boxing match outcomes using odds-anchored probabilities.

## Features

- **Real-time Simulation**: Live-updating dashboard with vectorized batch processing
- **Odds-Anchored Probabilities**: Converts American odds to implied probabilities with vig removal
- **Configurable Parameters**: Adjustable odds, round distributions, and simulation settings
- **Rich Visualizations**: 
  - KPI metrics tiles
  - Outcome distribution charts
  - KO round histograms
  - Convergence tracking over time
  - Last 20 fights table
- **Export Functionality**: Download simulation results as CSV

## Requirements

- Python 3.11+
- macOS (tested on macOS)

## Installation

1. Clone or download this repository
2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

Activate the virtual environment (if not already activated):

```bash
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

Run the Streamlit dashboard:

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

### Dashboard Controls

**Sidebar:**
- **Simulation Settings**: Configure sims per tick, max sims, and speed throttle
- **Random Seed**: Set seed for reproducibility (use "Reseed" button to apply)
- **Odds Configuration**: Edit all betting odds (moneyline, method of victory, draw)
- **KO Round Distributions**: Adjust probability distributions for each round (1-8) for both fighters
- **Controls**: Start/Stop simulation, Reset results, Export CSV

**Main Panel:**
- Real-time KPI metrics
- Interactive charts (Plotly)
- Convergence tracking
- Recent fight results table
- Assumptions and configuration summary

### Default Configuration

- **Moneyline**: Joshua -1200, Paul +800
- **Joshua Methods**: KO -390, Decision +450
- **Paul Methods**: KO +1200, Decision +1300
- **Joshua KO Rounds**: Earlier-weighted distribution (higher probability in early rounds)
- **Paul KO Rounds**: Later-weighted distribution (higher probability in later rounds)
- **Total Rounds**: 8

## Running Tests

Activate the virtual environment, then run the test suite:

```bash
source venv/bin/activate  # On macOS/Linux
pytest tests/
```

## Project Structure

```
paulvsjoshua/
├── app.py                 # Streamlit dashboard entry point
├── sim/                   # Simulation package
│   ├── __init__.py
│   ├── odds.py           # Odds conversion and vig removal
│   ├── model.py          # Data models and validation
│   ├── engine.py         # Vectorized Monte Carlo engine
│   └── metrics.py         # Statistics and aggregation
├── tests/                 # Unit tests
│   ├── __init__.py
│   ├── test_odds.py
│   └── test_model.py
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## How It Works

1. **Odds Conversion**: American odds are converted to implied probabilities
2. **Vig Removal**: Probabilities are normalized to remove the bookmaker's margin
3. **Simulation**: 
   - Winner is selected based on moneyline probabilities
   - Method (KO/TKO/DQ vs Decision) is selected conditionally based on winner
   - Round is selected from distribution if KO outcome, otherwise round 8 for Decision
4. **Aggregation**: Results are aggregated and displayed in real-time

## Screen Recording

To record the dashboard:

1. **macOS Built-in**: Use QuickTime Player → File → New Screen Recording
2. **Third-party**: Use OBS Studio, ScreenFlow, or similar tools
3. Start the simulation and let it run to show convergence

## Notes

- The simulation is deterministic given the same seed and inputs
- Uses numpy's PCG64 random number generator for reproducibility
- Vectorized batch processing for efficiency (50k sims complete quickly)
- All probabilities are validated and normalized automatically

## Disclaimer

This is an odds-anchored Monte Carlo simulation. It is **not a prediction**. All outputs are driven by the input odds and assumptions. The simulation uses implied probabilities from betting odds with vig removed.

