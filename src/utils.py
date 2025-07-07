import pandas as pd
from model import detect_anomalies, generate_summary
import plotly.graph_objs as go
from flask import has_request_context
import os

def process_CSV(source):
    df = pd.read_csv(source)

    alerts = []

    if 'date' in df.columns:
        try:
            df['date'] = pd.to_datetime(df['date'])
        except Exception as e:
            alerts.append({"type": 'error', "message": f"Date column exists but could not be parsed: {e}"})
            df['date'] = pd.date_range(start='2025-01-01', periods=len(df), freq='h')
    else:
        alerts.append({"type": 'error', "message": f"Uploaded file is missing the 'date' column."})
        df['date'] = pd.date_range(start='2025-01-01', periods=len(df), freq='h')

    if 'generated_power_kw' not in df.columns:
        alerts.append({"type": 'error', "message": f"Missing required 'generated_power_kw' column"})
        raise ValueError("Missing required 'generated_power_kw' column")

    df = detect_anomalies(df)
    summary = generate_summary(df)
    
    anomalies = df[df["anomaly"] == True]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["generated_power_kw"],
        mode='lines',
        name='Generated Power (kW)',
        line=dict(color='#1E3A8A')
    ))

    severity_colors = {
        'Small': '#FFD600',
        'Medium': '#FF9800',
        'Major': '#B22222'
    }

    for severity, color in severity_colors.items():
        subset = anomalies[anomalies["severity"] == severity]
        if not subset.empty:
            fig.add_trace(go.Scatter(
                x=subset["date"],
                y=subset["generated_power_kw"],
                mode='markers',
                name=f'Anomaly ({severity})',
                marker=dict(color=color, size=8, symbol='x')
            ))

    fig.update_layout(
        title="Generated Power Over Time",
        xaxis_title="Date",
        yaxis_title="Generated Power (kW)",
        height=400,
        margin=dict(t=30, b=30, l=30, r=30),
        showlegend=True,
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='#E0E0E0'), 
        xaxis=dict(
            gridcolor='#333333',
            zerolinecolor='#444444',
            linecolor='#888888',
            tickcolor='#E0E0E0',
        ),
        yaxis=dict(
            gridcolor='#333333',
            zerolinecolor='#444444',
            linecolor='#888888',
            tickcolor='#E0E0E0',
        ),
    )

    if not anomalies.empty:
        report = anomalies[["date", "generated_power_kw", "severity"]]
        report.to_csv(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), 'alerts_today.csv'), index=False)
        alerts.append({"type": 'warning', "message": f"Anomalies detected and saved. Check summary for details."})
    else:
        alerts.append({"type": 'success', "message": f"No anomalies detected. All systems normal."})

    chart = fig.to_html(full_html=False)

    return summary, chart, anomalies, fig, alerts