import pandas as pd
import plotly.graph_objs as go
import os
import json
from flask import Flask, render_template, request, flash, redirect, url_for, get_flashed_messages
from flask_login import login_manager, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm
from model import Workflow, User
from utils import process_CSV
from dotenv import load_dotenv
from extensions import db, login_manager
from werkzeug.utils import secure_filename
from plotly.utils import PlotlyJSONEncoder

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///configs.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager.login_view = 'login'
login_manager.init_app(app)

@app.route('/')
@login_required
def home():
    workflows = Workflow.query.filter_by(user_id=current_user.id).order_by(Workflow.created_at.desc()).all()
    return render_template("home.html", workflows=workflows)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    workflow_id = request.args.get("id")
    chart = None
    summary = None
    alerts = []
    uploaded_filename = None

    if workflow_id:
        workflow = Workflow.query.get_or_404(workflow_id)
        uploaded_filename = workflow.filename
        summary = json.loads(workflow.summary_json) if workflow.summary_json else None
        fig_dict = json.loads(workflow.chart_json) if workflow.chart_json else None
        chart = go.Figure(fig_dict).to_html(full_html=False) if fig_dict else None
        alerts = json.loads(workflow.alerts_json or "[]")

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            uploaded_filename = secure_filename(file.filename)
            os.makedirs("uploads", exist_ok=True)
            save_path = os.path.join("uploads", uploaded_filename)
            file.save(save_path)

            try:
                summary, chart, anomalies, fig, alerts = process_CSV(save_path)

                workflow = Workflow(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    name=uploaded_filename,
                    filename=uploaded_filename,
                    summary_json=json.dumps(summary) if summary else None,
                    chart_json = json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder) if chart else None,
                    alerts_json=json.dumps(alerts) if alerts else []
                )

                db.session.add(workflow)
                db.session.commit()
                
            except ValueError as e:
                alerts.append({"type": 'error', "message": f"Error processing file: {str(e)}"})
                os.remove(save_path)
            except pd.errors.EmptyDataError:
                alerts.append({"type": 'error', "message": "Uploaded file is completely empty. Please upload a valid CSV file."})
                os.remove(save_path)
        else:
            alerts.append({"type": 'error', "message": "Please upload a valid CSV file."})

    if summary is None:
        summary = {}

    if uploaded_filename is None:
        uploaded_filename = ""

    if chart is None:
        chart = ""

    for alert in alerts:
        flash(alert['message'], alert['type'])

    messages = get_flashed_messages(with_categories=True)

    return render_template("dashboard.html", chart=chart, summary=summary, uploaded_filename=uploaded_filename, alerts=alerts)

@app.route('/workflow/delete/<int:workflow_id>', methods=['POST'])
def delete_workflow(workflow_id):
    workflow = Workflow.query.get_or_404(workflow_id)
    file_path = os.path.join("uploads", workflow.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(workflow)
    db.session.commit()
    flash(f'Workflow "{workflow.name}" deleted.', 'success')
    return redirect(url_for('home'))

@app.route('/workflow/rename/<int:workflow_id>', methods=['POST'])
def rename_workflow(workflow_id):
    workflow = Workflow.query.get_or_404(workflow_id)
    new_name = request.form.get('new_name')
    if new_name:
        workflow.name = new_name
        db.session.commit()
        return '', 204
    else:
        return 'Name is required', 400

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "Auth Error")
            return redirect(url_for('register'))

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created", "Auth Success")
        return redirect(url_for('login'))

    return render_template("register.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully", "Auth Success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "Auth Error")

    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
