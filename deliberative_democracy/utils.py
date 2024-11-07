def parse_resources(resource_string):
    """
    Parse a resource string like 'Time: 2, Money: 1, Labor: 3'
    and return a dictionary with resource amounts.
    """
    resource_dict = {"time": 0, "money": 0, "labor": 0}  # Default values
    resources = resource_string.split(", ")
    for resource in resources:
        if ": " in resource:
            key, value = resource.split(": ")
            resource_dict[key.lower()] = int(value)
    return resource_dict


def check_contributions(contributions, required_resources):
    """
    Check if contributions meet or exceed the required resources.
    """
    for resource, required_amount in required_resources.items():
        contributed_amount = contributions.get(resource, 0)
        if contributed_amount < required_amount:
            return "not enough"
        elif contributed_amount > required_amount:
            return "too much"
    return "sufficient"


def deduct_user_resources(user, contrib):
    """
    Deduct resources from the user based on the contribution.
    """
    for resource in user.resources:
        if resource.type.lower() == "time":
            resource.amount = max(resource.amount - contrib.get("time", 0), 0)
        elif resource.type.lower() == "money":
            resource.amount = max(resource.amount - contrib.get("money", 0), 0)
        elif resource.type.lower() == "labor":
            resource.amount = max(resource.amount - contrib.get("labor", 0), 0)
    db.session.add(user)


def update_metrics(outcomes_str, user):
    """
    Update user and global metrics based on project outcomes.
    """
    outcomes = parse_resources(outcomes_str)  # Assuming the format is similar
    for outcome_type, value in outcomes.items():
        metric = CommonMetric.query.filter_by(type=outcome_type.capitalize()).first()
        if metric:
            metric.value += value
            db.session.add(metric)
    db.session.commit()
