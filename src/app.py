from flask import Flask, render_template, request, flash
import pandas as pd
import plotly.graph_objs as go
from model import detect_anomalies, generate_summary

app = Flask(__name__)
app.secret_key = 'secret'  # For flash messages

@app.route('/', methods=['GET', 'POST'])
def index():
    chart = None
    summary = None
    alerts = None
    uploaded_filename = None

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            uploaded_filename = file.filename
            try:
                df = pd.read_csv(file)

                if 'generated_power_kw' not in df.columns:
                    flash("Uploaded file is missing the required 'generated_power_kw' column.", 'error')
                else:
                    df['date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='h')

                    df = detect_anomalies(df)
                    summary = generate_summary(df)

                    anomalies = df[df["anomaly"] == True]

                    # Create plot
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
                        plot_bgcolor='#121212',   # dark background inside plot
                        paper_bgcolor='#121212',  # dark background outside plot
                        font=dict(color='#E0E0E0'),  # light text for titles, ticks, legend
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
                    
                    chart = fig.to_html(full_html=False)

                    if not anomalies.empty:
                        alerts = anomalies[["date", "generated_power_kw", "severity"]]
                        alerts.to_csv("alerts_today.csv", index=False)
                        flash("Anomalies detected and saved. Check summary for details.", "warning")
                    else:
                        flash("No anomalies detected. All systems normal.", "success")

            except pd.errors.EmptyDataError:
                flash("Uploaded file is completely empty. Please upload a valid CSV file.", "error")
        else:
            flash("Please upload a valid CSV file.", "error")

    return render_template("index.html", chart=chart, summary=summary, uploaded_filename=uploaded_filename)

if __name__ == '__main__':
    app.run(debug=True)
