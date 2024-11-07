from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_socketio import SocketIO, emit
from config import Config
from models import db, User, Project, Metric, CommonMetric, CompletedProject, Resource
from forms import LoginForm, ProjectInsightForm
from datetime import datetime
from utils import (
    parse_resources,
    deduct_user_resources,
    update_metrics,
    check_contributions,
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        character_name = form.character_name.data
        user = User.query.filter_by(character_name=character_name).first()
        if user:
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Character not found.", "danger")
    return render_template("login.html", form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(current_user.id)
    return render_template("dashboard.html", user=user)


@app.route("/projects")
@login_required
def project_list():
    projects = Project.query.filter_by(is_completed=False).all()
    return render_template("project_list.html", projects=projects)


@app.route("/project/<int:project_id>", methods=["GET", "POST"])
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectInsightForm(request.form)
    users = User.query.all()

    # Parse required resources from the project
    required_resources = parse_resources(project.required_resources)

    # Collect contributions from form inputs
    contributions = {
        user.id: {
            "time": int(request.form.get(f"contribute_time_{user.id}", 0)),
            "money": int(request.form.get(f"contribute_money_{user.id}", 0)),
            "labor": int(request.form.get(f"contribute_labor_{user.id}", 0)),
        }
        for user in users
    }

    # Sum total contributions
    total_contributed = {
        "time": sum(contrib["time"] for contrib in contributions.values()),
        "money": sum(contrib["money"] for contrib in contributions.values()),
        "labor": sum(contrib["labor"] for contrib in contributions.values()),
    }

    # Check if contributions meet project requirements
    if any(
        total_contributed[res] > required_resources[res] for res in required_resources
    ):
        flash(
            "The contributions exceed the required resources. Please adjust.", "danger"
        )
    elif any(
        total_contributed[res] < required_resources[res] for res in required_resources
    ):
        flash(
            "The contributions are not enough to meet the project requirements. Please adjust.",
            "warning",
        )
    else:
        # Contributions are appropriate
        flash("Contributions are appropriate. Project succeeded!", "success")

        # Deduct resources from each user
        for user_id, contrib in contributions.items():
            user = User.query.get(user_id)
            if user:
                deduct_user_resources(user, contrib)

        # Update common/global metrics
        update_metrics(project.outcomes, current_user)

        # Mark project as completed and commit to the database
        project.is_completed = True
        db.session.commit()

        # Broadcast updates to all connected users using SocketIO
        socketio.emit(
            "project_completed", {"project_id": project.id}, to="/", namespace="/"
        )

        return redirect(url_for("finished_projects"))

    return render_template(
        "project_detail.html", project=project, form=form, users=users
    )


@app.route("/finished_projects")
@login_required
def finished_projects():
    projects = Project.query.filter_by(is_completed=True).all()
    return render_template("finished_projects.html", projects=projects)


@app.route("/scoreboard")
@login_required
def score_board():
    common_metrics = CommonMetric.query.all()
    return render_template("score_board.html", metrics=common_metrics)


def adjust_resources(resources_str, factor):
    return resources_str


def adjust_outcomes(outcomes_str, factor):
    return outcomes_str


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    socketio.run(app, debug=True)
