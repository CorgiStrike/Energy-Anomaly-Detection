from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = model.fit_predict(df[['generated_power_kw']]) == -1

    # Calculate severity for anomalies
    mean = df["generated_power_kw"].mean()
    std = df["generated_power_kw"].std()
    df['severity'] = None
    df.loc[df['anomaly'], 'severity'] = df[df['anomaly']].apply(lambda row: classify_severity(row, mean, std), axis=1)

    return df

def generate_summary(df):
    anomalies = df[df["anomaly"] == True]

    if anomalies.empty:
        return (
            "Total Anomalies: <strong>0</strong><br>"
            "&nbsp;&nbsp;Small Anomalies: <strong>0</strong><br>"
            "&nbsp;&nbsp;Medium Anomalies: <strong>0</strong><br>"
            "&nbsp;&nbsp;Major Anomalies: <strong>0</strong>"
        )

    mean = df["generated_power_kw"].mean()
    std = df["generated_power_kw"].std()

    anomalies['severity'] = anomalies.apply(lambda row: classify_severity(row, mean, std), axis=1)

    summary_counts = anomalies['severity'].value_counts()
    total = len(anomalies)
    small = summary_counts.get("Small", 0)
    medium = summary_counts.get("Medium", 0)
    major = summary_counts.get("Major", 0)

    return (
        f"Total Anomalies: <strong>{total}</strong><br>"
        f"&nbsp;&nbsp;Small Anomalies: <strong>{small}</strong><br>"
        f"&nbsp;&nbsp;Medium Anomalies: <strong>{medium}</strong><br>"
        f"&nbsp;&nbsp;Major Anomalies: <strong>{major}</strong>"
    )

def classify_severity(row, mean, std):
    diff = abs(row['generated_power_kw'] - mean)
    if diff > 2 * std:
        return "Major"
    elif diff > std:
        return "Medium"
    else:
        return "Small"
