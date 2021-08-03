"""Filtering methods for API calls."""
from fastapi import Query

SCIM_OPERATORS = ["eq", "co", "sw", "pr", "gt", "ge", "lt", "le"]


def is_valid(q: Query):
    """check validity of a query"""
    return True


def add_filters(qs: str, query, myclass):
    for q in qs:
        for f in q.split(","):
            f = f.split("=")
            value = f[1]
            [attribute, operator] = (
                f[0].split(".") if len(f[0].split(".")) == 2 else [f[0], "eq"]
            )
            query = add_unique_filter(attribute, operator, value, query, myclass)
    return query


def add_unique_filter(attribute: str, operator, value, query, myclass):
    if operator == "eq":
        return query.filter(getattr(myclass, attribute) == value)
    if operator == "co":
        return query.filter(getattr(myclass, attribute).ilike("%{}%".format(value)))
    if operator == "sw":
        return query.filter(getattr(myclass, attribute).ilike("{}%".format(value)))
    if operator == "gt":
        return query.filter(getattr(myclass, attribute) > value)
    if operator == "ge":
        return query.filter(getattr(myclass, attribute) >= value)
    if operator == "lt":
        return query.filter(getattr(myclass, attribute) < value)
    if operator == "le":
        return query.filter(getattr(myclass, attribute) <= value)

    return query
