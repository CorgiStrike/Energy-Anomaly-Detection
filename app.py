import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from model import detect_anomalies, generate_summary



st.set_page_config(layout="wide")
st.title("Energy Anomaly Detection")

uploaded = st.file_uploader("Upload your energy CSV file:", type=["csv"])

if uploaded:
    try:
        df = pd.read_csv(uploaded)

        # Check if required column exists
        if 'generated_power_kw' not in df.columns:
            st.error("Uploaded file is missing the required 'generated_power_kw' column.")
        else:
            df['date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='h')  # Simulate hourly dates

            # Anomaly Detection and Classification
            df = detect_anomalies(df)
            summary = generate_summary(df)

            # Create Plotly figure
            fig = go.Figure()

            # Line for full data
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["generated_power_kw"],
                mode='lines',
                name='Generated Power (kW)',
                line=dict(color='blue')
            ))

            # Scatter for anomalies
            anomalies = df[df["anomaly"] == True]
            fig.add_trace(go.Scatter(
                x=anomalies["date"],
                y=anomalies["generated_power_kw"],
                mode='markers',
                name='Anomaly',
                marker=dict(color='red', size=6, symbol='x')
            ))

            # Customize layout
            fig.update_layout(
                title="Generated Power Over Time",
                xaxis_title="Date",
                yaxis_title="Generated Power (kW)",
                height=350,
                margin=dict(t=30, b=30, l=30, r=30),
                showlegend=True,
            )

            # Layout the chart and summary side-by-side
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Generated Power with Anomalies")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Weekly Summary")
                st.markdown(summary)

            if not anomalies.empty:
                alerts = anomalies[["date", "generated_power_kw"]]
                alerts.to_csv("alerts_today.csv", index=False)
                st.warning("Anomalies detected and saved. Check summary for details.")
            else:
                st.success("No anomalies detected. All systems normal.")

    except pd.errors.EmptyDataError:
        st.error("Uploaded file is completely empty. Please upload a valid CSV file.")