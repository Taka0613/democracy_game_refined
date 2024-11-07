import pytest
from app import app, db
from models import User, Resource, CommonMetric
from utils import (
    parse_resources,
    check_contributions,
    deduct_user_resources,
    update_metrics,
)


# Fixture for setting up the application context and database for tests
@pytest.fixture(scope="module")
def test_app():
    with app.app_context():
        db.create_all()  # Ensure tables are created
        yield app
        db.session.remove()
        db.drop_all()  # Clean up the database after tests


@pytest.fixture
def user_with_resources(test_app):
    user = User(character_name="Test User")
    db.session.add(user)
    db.session.commit()

    resources = [
        Resource(type="Time", amount=5, user_id=user.id),
        Resource(type="Money", amount=3, user_id=user.id),
        Resource(type="Labor", amount=4, user_id=user.id),
    ]
    db.session.bulk_save_objects(resources)
    db.session.commit()

    return user


def test_parse_resources():
    resource_string = "Time: 3, Money: 2, Labor: 1"
    expected_output = {"time": 3, "money": 2, "labor": 1}
    assert parse_resources(resource_string) == expected_output


def test_check_contributions_sufficient():
    contributions = {"time": 3, "money": 2, "labor": 1}
    required_resources = {"time": 3, "money": 2, "labor": 1}
    assert check_contributions(contributions, required_resources) == "sufficient"


def test_check_contributions_not_enough():
    contributions = {"time": 2, "money": 1, "labor": 1}
    required_resources = {"time": 3, "money": 2, "labor": 1}
    assert check_contributions(contributions, required_resources) == "not enough"


def test_check_contributions_too_much():
    contributions = {"time": 4, "money": 3, "labor": 2}
    required_resources = {"time": 3, "money": 2, "labor": 1}
    assert check_contributions(contributions, required_resources) == "too much"


def test_deduct_user_resources(user_with_resources):
    contributions = {"time": 2, "money": 1, "labor": 3}
    deduct_user_resources(user_with_resources, contributions)
    db.session.refresh(user_with_resources)

    resource_dict = {
        resource.type.lower(): resource.amount
        for resource in user_with_resources.resources
    }
    assert resource_dict["time"] == 3  # 5 - 2
    assert resource_dict["money"] == 2  # 3 - 1
    assert resource_dict["labor"] == 1  # 4 - 3


def test_update_metrics(test_app):
    outcome_string = "Environment: +2, Economy: +1"

    # Initialize CommonMetric in the database
    common_metrics = [
        CommonMetric(type="Environment", value=5),
        CommonMetric(type="Economy", value=3),
    ]
    db.session.bulk_save_objects(common_metrics)
    db.session.commit()

    user = User(character_name="Metric User")
    db.session.add(user)
    db.session.commit()

    update_metrics(outcome_string, user)

    # Check updated metric values
    environment_metric = CommonMetric.query.filter_by(type="Environment").first()
    economy_metric = CommonMetric.query.filter_by(type="Economy").first()

    assert environment_metric.value == 7  # 5 + 2
    assert economy_metric.value == 4  # 3 + 1
