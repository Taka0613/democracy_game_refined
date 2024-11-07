from app import app
from models import db, User, Project, CommonMetric

with app.app_context():
    db.create_all()

    # Initialize common metrics
    metrics = [
        CommonMetric(type="Environment", value=5),
        CommonMetric(type="Economy", value=5),
        CommonMetric(type="Welfare", value=5),
    ]
    db.session.bulk_save_objects(metrics)

    # Add users (characters)
    users = [
        User(
            character_name="Character 1",
            interests="Interest in environmental sustainability",
            utility_criteria="Achieve 10 Environment metric",
            starting_resources="Time: 3, Money: 2, Labor: 1",
            reading="Environmental impact studies and green initiatives.",
        ),
        User(
            character_name="Character 2",
            interests="Interest in economic growth",
            utility_criteria="Achieve 10 Economy metric",
            starting_resources="Time: 2, Money: 4, Labor: 1",
            reading="Economic strategies for city growth.",
        ),
        User(
            character_name="Character 3",
            interests="Interest in community welfare",
            utility_criteria="Achieve 10 Welfare metric",
            starting_resources="Time: 3, Money: 2, Labor: 2",
            reading="Social programs and community health.",
        ),
        User(
            character_name="Character 4",
            interests="Interest in balanced development",
            utility_criteria="Achieve a balanced score in all metrics",
            starting_resources="Time: 2, Money: 3, Labor: 2",
            reading="Integrated development plans.",
        ),
        User(
            character_name="Character 5",
            interests="Interest in rapid project execution",
            utility_criteria="Complete the most projects",
            starting_resources="Time: 4, Money: 1, Labor: 3",
            reading="Project management and efficiency strategies.",
        ),
    ]
    db.session.bulk_save_objects(users)

    # Add projects
    projects = [
        Project(
            name="Project 1",
            description="Develop a community park to improve green space.",
            outcomes="Environment: +2, Welfare: +1",
            required_resources="Time: 2, Money: 1",
        ),
        Project(
            name="Project 2",
            description="Upgrade local businesses to boost the economy.",
            outcomes="Economy: +3, Environment: -1",
            required_resources="Time: 3, Money: 2",
        ),
        Project(
            name="Project 3",
            description="Establish a health clinic for better community welfare.",
            outcomes="Welfare: +3, Economy: +1",
            required_resources="Time: 3, Labor: 2",
        ),
        Project(
            name="Project 4",
            description="Launch a renewable energy initiative.",
            outcomes="Environment: +4, Economy: +1",
            required_resources="Time: 4, Money: 3",
        ),
        Project(
            name="Project 5",
            description="Construct a new library for public education.",
            outcomes="Welfare: +2, Environment: +1",
            required_resources="Time: 3, Money: 2, Labor: 1",
        ),
    ]
    db.session.bulk_save_objects(projects)

    db.session.commit()
    print("Database initialized!")
