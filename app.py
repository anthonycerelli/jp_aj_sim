"""Streamlit dashboard for Monte Carlo boxing simulation."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List
import time

from sim.model import SimulationParams, OddsConfig, RoundDistribution
from sim.engine import SimulationEngine
from sim.metrics import SimulationMetrics


# Page configuration
st.set_page_config(
    page_title="Paul vs Joshua Monte Carlo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "engine" not in st.session_state:
    st.session_state.engine = None
if "metrics" not in st.session_state:
    st.session_state.metrics = SimulationMetrics()
if "running" not in st.session_state:
    st.session_state.running = False
if "sim_id_counter" not in st.session_state:
    st.session_state.sim_id_counter = 0
if "tick_counter" not in st.session_state:
    st.session_state.tick_counter = 0
if "revealed_count" not in st.session_state:
    st.session_state.revealed_count = 0

# Color scheme: Joshua = blue, Paul = red (non-aggressive)
JOSHUA_COLOR = "#4A90E2"  # Soft blue
JOSHUA_COLOR_LIGHT = "#A8D0F0"  # Light blue
PAUL_COLOR = "#E24A4A"  # Soft red
PAUL_COLOR_LIGHT = "#F0A8A8"  # Light red


def create_engine_from_sidebar() -> SimulationEngine:
    """Create simulation engine from sidebar inputs."""
    # Get values from session state with defaults
    odds = OddsConfig(
        joshua_moneyline=st.session_state.get("joshua_ml", -1200),
        paul_moneyline=st.session_state.get("paul_ml", 800),
        joshua_ko=st.session_state.get("joshua_ko", -390),
        joshua_decision=st.session_state.get("joshua_dec", 450),
        paul_ko=st.session_state.get("paul_ko", 1200),
        paul_decision=st.session_state.get("paul_dec", 1300),
        draw=st.session_state.get("draw_odds", 2500),
        total_rounds=8,
    )
    
    round_dist = RoundDistribution(
        joshua_ko_rounds=[
            st.session_state.get("joshua_r1", 0.22),
            st.session_state.get("joshua_r2", 0.20),
            st.session_state.get("joshua_r3", 0.16),
            st.session_state.get("joshua_r4", 0.12),
            st.session_state.get("joshua_r5", 0.10),
            st.session_state.get("joshua_r6", 0.08),
            st.session_state.get("joshua_r7", 0.07),
            st.session_state.get("joshua_r8", 0.05),
        ],
        paul_ko_rounds=[
            st.session_state.get("paul_r1", 0.06),
            st.session_state.get("paul_r2", 0.07),
            st.session_state.get("paul_r3", 0.10),
            st.session_state.get("paul_r4", 0.12),
            st.session_state.get("paul_r5", 0.16),
            st.session_state.get("paul_r6", 0.18),
            st.session_state.get("paul_r7", 0.17),
            st.session_state.get("paul_r8", 0.14),
        ],
    )
    
    params = SimulationParams(
        odds=odds,
        round_dist=round_dist,
        seed=st.session_state.get("seed", 42),
        enable_draw=st.session_state.get("enable_draw", False),
    )
    
    return SimulationEngine(params)


# Sidebar
with st.sidebar:
    st.header("Simulation Controls")
    
    # Simulation parameters
    st.subheader("Simulation Settings")
    sims_per_tick = st.number_input(
        "Sims per tick",
        min_value=1,
        max_value=10000,
        value=100,
        step=50,
        key="sims_per_tick",
    )
    max_sims = st.number_input(
        "Max sims",
        min_value=100,
        max_value=1000000,
        value=50000,
        step=1000,
        key="max_sims",
    )
    sleep_seconds = st.number_input(
        "Speed throttle (seconds)",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        step=0.01,
        format="%.2f",
        key="sleep_seconds",
    )
    
    # Random seed
    st.subheader("Random Seed")
    seed = st.number_input(
        "Seed",
        min_value=0,
        value=42,
        key="seed",
    )
    if st.button("Reseed", key="reseed_btn"):
        if st.session_state.engine:
            st.session_state.engine.reseed(seed)
    
    # Odds configuration
    st.subheader("Odds Configuration")
    st.number_input(
        "Joshua Moneyline",
        value=-1200,
        key="joshua_ml",
    )
    st.number_input(
        "Paul Moneyline",
        value=800,
        key="paul_ml",
    )
    
    st.number_input(
        "Joshua KO/TKO/DQ",
        value=-390,
        key="joshua_ko",
    )
    st.number_input(
        "Joshua Decision",
        value=450,
        key="joshua_dec",
    )
    
    st.number_input(
        "Paul KO/TKO/DQ",
        value=1200,
        key="paul_ko",
    )
    st.number_input(
        "Paul Decision",
        value=1300,
        key="paul_dec",
    )
    
    st.checkbox("Enable Draw", value=False, key="enable_draw")
    if st.session_state.enable_draw:
        st.number_input(
            "Draw Odds",
            value=2500,
            key="draw_odds",
        )
    else:
        if "draw_odds" not in st.session_state:
            st.session_state.draw_odds = 2500
    
    # Round distributions
    st.subheader("KO Round Distributions")
    st.write("**Joshua KO Rounds** (earlier-weighted)")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("R1", value=0.22, key="joshua_r1", format="%.3f")
        st.number_input("R2", value=0.20, key="joshua_r2", format="%.3f")
        st.number_input("R3", value=0.16, key="joshua_r3", format="%.3f")
        st.number_input("R4", value=0.12, key="joshua_r4", format="%.3f")
    with col2:
        st.number_input("R5", value=0.10, key="joshua_r5", format="%.3f")
        st.number_input("R6", value=0.08, key="joshua_r6", format="%.3f")
        st.number_input("R7", value=0.07, key="joshua_r7", format="%.3f")
        st.number_input("R8", value=0.05, key="joshua_r8", format="%.3f")
    
    st.write("**Paul KO Rounds** (later-weighted)")
    col3, col4 = st.columns(2)
    with col3:
        st.number_input("R1", value=0.06, key="paul_r1", format="%.3f")
        st.number_input("R2", value=0.07, key="paul_r2", format="%.3f")
        st.number_input("R3", value=0.10, key="paul_r3", format="%.3f")
        st.number_input("R4", value=0.12, key="paul_r4", format="%.3f")
    with col4:
        st.number_input("R5", value=0.16, key="paul_r5", format="%.3f")
        st.number_input("R6", value=0.18, key="paul_r6", format="%.3f")
        st.number_input("R7", value=0.17, key="paul_r7", format="%.3f")
        st.number_input("R8", value=0.14, key="paul_r8", format="%.3f")
    
    # Control buttons
    st.subheader("Controls")
    col_start, col_stop = st.columns(2)
    with col_start:
        start_clicked = st.button("Start", key="start_btn", use_container_width=True)
        if start_clicked:
            try:
                engine = create_engine_from_sidebar()
                st.session_state.engine = engine
                st.session_state.running = True
                st.session_state.sim_id_counter = 0
                st.session_state.tick_counter = 0
                st.session_state.revealed_count = 0
                st.session_state.metrics.reset()
                st.success("Simulation started! Running...")
                # Force immediate rerun
                st.rerun()
            except Exception as e:
                import traceback
                error_msg = f"Error initializing engine: {e}"
                st.error(error_msg)
                st.code(traceback.format_exc())
                # Print to console for debugging
                print(f"START BUTTON ERROR: {error_msg}")
                print(traceback.format_exc())
    
    with col_stop:
        if st.button("Stop", key="stop_btn", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    
    if st.button("Reset", key="reset_btn", use_container_width=True):
        st.session_state.metrics.reset()
        st.session_state.running = False
        st.session_state.sim_id_counter = 0
        st.session_state.tick_counter = 0
        st.session_state.revealed_count = 0
        # Clear any stale download button references
        if "download_csv" in st.session_state:
            del st.session_state.download_csv
        st.rerun()
    
    # Batch reveal controls
    st.subheader("Reveal Results")
    total_results = len(st.session_state.metrics.results)
    revealed = st.session_state.get("revealed_count", 0)
    
    if total_results > 0:
        st.caption(f"Revealed: {revealed:,} / {total_results:,}")
        
        # Use selectbox for cleaner UI
        reveal_options = ["10", "100", "1000", "All"]
        selected_reveal = st.selectbox(
            "Reveal batch size:",
            options=reveal_options,
            key="reveal_select",
            label_visibility="collapsed"
        )
        
        if st.button("Reveal", key="reveal_btn", use_container_width=True):
            if selected_reveal == "All":
                st.session_state.revealed_count = total_results
            else:
                batch_size = int(selected_reveal)
                st.session_state.revealed_count = min(
                    revealed + batch_size,
                    total_results
                )
            st.rerun()
    else:
        st.caption("No results yet. Start simulation first.")
    
    # Export button - only show when there's data
    df = st.session_state.metrics.get_dataframe()
    if not df.empty and len(df) > 0:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Export Results (CSV)",
            data=csv,
            file_name=f"simulation_results_{int(time.time())}.csv",
            mime="text/csv",
            key="download_csv",
            use_container_width=True,
        )


# Main panel
st.title("Paul vs Joshua Monte Carlo Simulation")

# Debug status
with st.expander("Debug Info", expanded=False):
    st.write("**Session State:**")
    st.json({
        "running": st.session_state.get("running", False),
        "has_engine": st.session_state.get("engine") is not None,
        "sim_id_counter": st.session_state.get("sim_id_counter", 0),
        "tick_counter": st.session_state.get("tick_counter", 0),
        "total_results": len(st.session_state.metrics.results),
        "revealed_count": st.session_state.get("revealed_count", 0),
    })
    
if "running" in st.session_state:
    status_text = "Running" if st.session_state.running else "Stopped"
    engine_text = "Engine Ready" if st.session_state.get("engine") else "No Engine"
    st.caption(f"Status: {status_text} | {engine_text}")

# Run simulation loop
if st.session_state.get("running", False) and st.session_state.get("engine"):
    stats = st.session_state.metrics.get_summary_stats()
    
    if stats["total_sims"] < st.session_state.get("max_sims", 50000):
        # Run batch
        try:
            batch_results = st.session_state.engine.simulate_batch(
                st.session_state.get("sims_per_tick", 100),
                st.session_state.get("sim_id_counter", 0)
            )
            st.session_state.metrics.add_results(batch_results)
            st.session_state.sim_id_counter = st.session_state.get("sim_id_counter", 0) + st.session_state.get("sims_per_tick", 100)
            st.session_state.tick_counter = st.session_state.get("tick_counter", 0) + 1
            
            # Record history every 10 ticks
            if st.session_state.tick_counter % 10 == 0:
                st.session_state.metrics.record_history(st.session_state.tick_counter)
            
            time.sleep(st.session_state.get("sleep_seconds", 0.05))
            st.rerun()
        except Exception as e:
            st.error(f"Error in simulation loop: {e}")
            import traceback
            st.code(traceback.format_exc())
            st.session_state.running = False

# Get revealed results for display
all_results = st.session_state.metrics.results
revealed_count = st.session_state.get("revealed_count", 0)

# Ensure revealed_count doesn't exceed available results
if revealed_count > len(all_results):
    revealed_count = len(all_results)
    st.session_state.revealed_count = revealed_count

revealed_results = all_results[:revealed_count] if revealed_count > 0 and len(all_results) > 0 else []

# Create a temporary metrics object with only revealed results for display
from sim.metrics import SimulationMetrics
display_metrics = SimulationMetrics()
if revealed_results and len(revealed_results) > 0:
    display_metrics.add_results(revealed_results)
    # Copy history from main metrics for convergence chart
    display_metrics.history = st.session_state.metrics.history.copy()

# Get current stats from revealed results
stats = display_metrics.get_summary_stats()

# KPI Tiles
st.subheader("Key Metrics")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Sims", f"{stats['total_sims']:,}")

with col2:
    st.metric("Joshua Win %", f"{stats['joshua_win_pct']:.2f}%")

with col3:
    st.metric("Paul Win %", f"{stats['paul_win_pct']:.2f}%")

with col4:
    st.metric("Joshua KO %", f"{stats['joshua_ko_pct']:.2f}%")

with col5:
    st.metric("Joshua Dec %", f"{stats['joshua_decision_pct']:.2f}%")

with col6:
    st.metric("Paul KO %", f"{stats['paul_ko_pct']:.2f}%")
    
# Show reveal status
total_results = len(all_results)
if total_results > 0:
    if revealed_count == 0:
        st.info("Click 'Reveal' in the sidebar to see simulation results.")
    else:
        st.caption(f"Showing {revealed_count:,} of {total_results:,} simulated results. Use reveal controls in sidebar to see more.")

# Charts row 1
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Outcome Distribution")
    outcome_dist = display_metrics.get_outcome_distribution()
    if sum(outcome_dist.values()) > 0:
        fig = px.bar(
            x=list(outcome_dist.keys()),
            y=list(outcome_dist.values()),
            labels={"x": "Outcome", "y": "Count"},
            color=list(outcome_dist.keys()),
            color_discrete_map={
                "Joshua KO/TKO/DQ": JOSHUA_COLOR,
                "Joshua Decision": JOSHUA_COLOR_LIGHT,
                "Paul KO/TKO/DQ": PAUL_COLOR,
                "Paul Decision": PAUL_COLOR_LIGHT,
                "Draw": "#888888",
            },
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run simulation and reveal results to see distribution")

with col_chart2:
    st.subheader("KO Round Distribution")
    ko_rounds = display_metrics.get_ko_round_distribution()
    if sum(ko_rounds["Joshua"]) + sum(ko_rounds["Paul"]) > 0:
        rounds = list(range(1, 9))
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=rounds,
            y=ko_rounds["Joshua"],
            name="Joshua",
            marker_color=JOSHUA_COLOR,
        ))
        fig.add_trace(go.Bar(
            x=rounds,
            y=ko_rounds["Paul"],
            name="Paul",
            marker_color=PAUL_COLOR,
        ))
        fig.update_layout(
            xaxis_title="Round",
            yaxis_title="Count",
            barmode="group",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run simulation and reveal results to see KO rounds")

# Convergence chart
st.subheader("Convergence Over Time")
conv_df = display_metrics.get_convergence_data()
if not conv_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=conv_df["total_sims"],
        y=conv_df["joshua_win_pct"],
        name="Joshua Win %",
        line=dict(color=JOSHUA_COLOR, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=conv_df["total_sims"],
        y=conv_df["joshua_ko_pct"],
        name="Joshua KO %",
        line=dict(color=JOSHUA_COLOR_LIGHT, width=2),
    ))
    fig.update_layout(
        xaxis_title="Total Simulations",
        yaxis_title="Percentage",
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Run simulation to see convergence")

# Last 20 fights table
st.subheader("Last 20 Revealed Fights")
if revealed_results:
    df = pd.DataFrame([
        {
            "sim_id": r.sim_id,
            "winner": r.winner,
            "method": r.method,
            "round": r.round,
        }
        for r in revealed_results[-20:]
    ])
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Reveal results to see fights")
else:
    st.info("Run simulation and reveal results to see fights")

# Assumptions box
st.subheader("Assumptions & Configuration")
with st.expander("View Assumptions", expanded=False):
    if st.session_state.engine:
        params = st.session_state.engine.params
        st.write("**Odds Used:**")
        st.write(f"- Joshua Moneyline: {params.odds.joshua_moneyline}")
        st.write(f"- Paul Moneyline: {params.odds.paul_moneyline}")
        st.write(f"- Joshua KO: {params.odds.joshua_ko}")
        st.write(f"- Joshua Decision: {params.odds.joshua_decision}")
        st.write(f"- Paul KO: {params.odds.paul_ko}")
        st.write(f"- Paul Decision: {params.odds.paul_decision}")
        if params.enable_draw:
            st.write(f"- Draw: {params.odds.draw}")
        
        st.write("**Vig Removal Method:**")
        st.write("Probabilities are normalized to sum to 1.0 (divide by sum)")
        
        st.write("**KO Round Distributions:**")
        st.write("**Joshua:**", [f"{p:.3f}" for p in params.round_dist.joshua_ko_rounds])
        st.write("**Paul:**", [f"{p:.3f}" for p in params.round_dist.paul_ko_rounds])
        
        st.write("**Total Rounds:**", params.odds.total_rounds)
        
        st.write("**Disclaimer:**")
        st.write("This is an odds-anchored Monte Carlo simulation. It is not a prediction. "
                 "All outputs are driven by the input odds and assumptions. "
                 "The simulation uses implied probabilities from betting odds with vig removed.")
    else:
        st.info("Initialize simulation to see assumptions")

