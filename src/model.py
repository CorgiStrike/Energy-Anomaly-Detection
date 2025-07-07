from sklearn.ensemble import IsolationForest
from extensions import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    workflows = db.relationship('Workflow', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    summary_json = db.Column(db.Text)
    chart_json = db.Column(db.Text)
    alerts_json = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

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
