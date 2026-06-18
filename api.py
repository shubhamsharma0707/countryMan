from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from realtime_data import (
    fetch_live_national_metrics,
    fetch_state_realtime_data,
    fetch_generation_mix,
    fetch_historical_trend,
    fetch_recent_policy_updates
)
from enhanced_model import EnhancedEDIModel
from app import (
    make_3d_edi_surface,
    make_3d_scatter,
    make_radar,
    make_animated_bar,
    make_generation_donut,
    make_trend_chart,
    make_corr_heatmap,
    get_national_metrics,
    get_state_data,
    get_historical,
    get_generation_mix,
    get_policy_updates
)

app = FastAPI(title="Energy Dignity API")

# Add CORS so our React frontend can access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard")
def get_dashboard_data():
    """Returns all data and Plotly charts required for the frontend."""
    metrics = get_national_metrics()
    state_df = get_state_data()
    hist_df = get_historical()
    gen_mix = get_generation_mix()
    policy_updates = get_policy_updates()
    
    model = EnhancedEDIModel()
    urban_df = state_df[state_df["area"] == "urban"].drop_duplicates("state")
    rural_df = state_df[state_df["area"] == "rural"].drop_duplicates("state")
    
    # Generate charts
    fig_3d_surface = make_3d_edi_surface(state_df)
    fig_3d_scatter = make_3d_scatter(state_df)
    
    avg_scores = {}
    for d in ["A", "E", "R", "H", "P", "G"]:
        avg_scores[f"S_{d}"] = float(state_df[f"S_{d}"].mean())
    fig_radar = make_radar(avg_scores, "National Profile")
    
    fig_bar = make_animated_bar(state_df, "EDI")
    fig_donut = make_generation_donut(gen_mix)
    fig_trend = make_trend_chart(hist_df)
    fig_corr = make_corr_heatmap(state_df)
    
    af_stats = model.alkire_foster(state_df)
    
    return {
        "metrics": metrics,
        "af_stats": af_stats,
        "policies": policy_updates,
        "state_data": state_df.to_dict(orient="records"),
        "plots": {
            "surface_3d": json.loads(fig_3d_surface.to_json()),
            "scatter_3d": json.loads(fig_3d_scatter.to_json()),
            "radar": json.loads(fig_radar.to_json()),
            "bar": json.loads(fig_bar.to_json()),
            "donut": json.loads(fig_donut.to_json()),
            "trend": json.loads(fig_trend.to_json()),
            "heatmap": json.loads(fig_corr.to_json())
        }
    }
