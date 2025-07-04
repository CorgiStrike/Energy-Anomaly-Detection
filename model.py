from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = model.fit_predict(df[['generated_power_kw']]) == -1
    return df

def generate_summary(df):
    anomalies = df[df["anomaly"] == True]

    if anomalies.empty:
        return "No anomalies detected this week."

    mean = df["generated_power_kw"].mean()
    std = df["generated_power_kw"].std()

    # Classify severity
    anomalies['severity'] = anomalies.apply(lambda row: classify_severity(row, mean, std), axis=1)

    # Count types
    summary_counts = anomalies['severity'].value_counts()
    total = len(anomalies)

    # Format the summary
    small = summary_counts.get("small", 0)
    medium = summary_counts.get("medium", 0)
    major = summary_counts.get("major", 0)

    return (
        f"Total anomalies: **{total}**\n\n"
        f"  - Small anomalies: {small}\n"
        f"  - Medium anomalies: {medium}\n"
        f"  - Major anomalies: {major}"
    )

def classify_severity(row, mean, std):
    diff = abs(row['generated_power_kw'] - mean)
    if diff > 2 * std:
        return "major"
    elif diff > std:
        return "medium"
    else:
        return "small"
