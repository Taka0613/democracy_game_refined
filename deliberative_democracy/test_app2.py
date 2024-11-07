import pytest
from app import app, db
from models import User, Project, CommonMetric, Resource
from utils import parse_resources, deduct_user_resources, update_metrics


@pytest.fixture
def test_app():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()

        # Set up common metrics
        common_metrics = [
            CommonMetric(type="Environment", value=5),
            CommonMetric(type="Economy", value=5),
            CommonMetric(type="Welfare", value=5),
        ]
        db.session.bulk_save_objects(common_metrics)
        db.session.commit()

        # Set up users and resources
        user1 = User(character_name="User 1")
        user2 = User(character_name="User 2")
        user1.resources = [
            Resource(type="Time", amount=5),
            Resource(type="Money", amount=3),
            Resource(type="Labor", amount=2),
        ]
        user2.resources = [
            Resource(type="Time", amount=4),
            Resource(type="Money", amount=2),
            Resource(type="Labor", amount=3),
        ]
        db.session.add_all([user1, user2])
        db.session.commit()

        # Set up project
        project = Project(
            name="Project Test",
            description="A test project.",
            outcomes="Environment: +2, Economy: +1",
            required_resources="Time: 6, Money: 4, Labor: 4",
        )
        db.session.add(project)
        db.session.commit()

        yield app

        db.drop_all()


def test_project_submission_and_metrics_update(test_app):
    with test_app.app_context():
        # Retrieve the test data
        user1 = User.query.filter_by(character_name="User 1").first()
        user2 = User.query.filter_by(character_name="User 2").first()
        project = Project.query.filter_by(name="Project Test").first()

        # Simulate resource contributions from users
        contributions = {
            user1.id: {"time": 3, "money": 2, "labor": 1},
            user2.id: {"time": 3, "money": 2, "labor": 3},
        }

        # Deduct resources from users and update communal metrics
        for user_id, contrib in contributions.items():
            user = User.query.get(user_id)
            deduct_user_resources(user, contrib)

        # Update common metrics based on project outcomes
        update_metrics(project.outcomes, user1)

        # Check if resources were deducted correctly
        assert user1.resources[0].amount == 2  # Time
        assert user1.resources[1].amount == 1  # Money
        assert user1.resources[2].amount == 1  # Labor

        assert user2.resources[0].amount == 1  # Time
        assert user2.resources[1].amount == 0  # Money
        assert user2.resources[2].amount == 0  # Labor

        # Check if communal metrics were updated correctly
        env_metric = CommonMetric.query.filter_by(type="Environment").first()
        econ_metric = CommonMetric.query.filter_by(type="Economy").first()

        assert env_metric.value == 7  # Initial 5 + 2 from project outcome
        assert econ_metric.value == 6  # Initial 5 + 1 from project outcome
