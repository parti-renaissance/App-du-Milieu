from typing import Any, Union
from sqlalchemy.orm.query import Query
from fastapi import Query

SCIM_OPERATORS = ["eq", "co", "sw", "pr", "gt", "ge", "lt", "le"]


def is_valid(q: Query) -> bool:
    """
    Check validity of a query.

    Args:
        q (Query): Query to be validated.

    Returns:
        bool: True if query is valid, False otherwise.
    """
    return True  # TODO: Implement query validation logic


def add_filters(qs: str, query: Query, myclass: Any) -> Query:
    """
    Add filters to a query.

    Args:
        qs (str): Comma-separated string of filters.
        query (Query): Query to be filtered.
        myclass (Any): SQLAlchemy model class to be queried.

    Returns:
        Query: Filtered query.
    """
    for q in qs:
        for f in q.split(","):
            attribute, operator, value = _parse_filter(f)
            query = _add_unique_filter(attribute, operator, value, query, myclass)
    return query


def _parse_filter(filter_string: str) -> Union[tuple, None]:
    """
    Parse a filter string.

    Args:
        filter_string (str): Filter string to be parsed.

    Returns:
        Union[tuple, None]: Tuple of attribute, operator and value if filter is valid, None otherwise.
    """
    filter_parts = filter_string.split("=")
    if len(filter_parts) != 2:
        return None

    attribute_operator, value = filter_parts
    attribute_operator_parts = attribute_operator.split(".")
    attribute = attribute_operator_parts[0]
    operator = attribute_operator_parts[1] if len(attribute_operator_parts) == 2 else "eq"
    if operator not in SCIM_OPERATORS:
        return None

    return attribute, operator, value


def _add_unique_filter(attribute: str, operator: str, value: str, query: Query, myclass: Any) -> Query:
    """
    Add a unique filter to a query.

    Args:
        attribute (str): Attribute name.
        operator (str): Operator.
        value (str): Value.
        query (Query): Query to be filtered.
        myclass (Any): SQLAlchemy model class to be queried.

    Returns:
        Query: Filtered query.
    """
    filter_map = {
        "eq": getattr(myclass, attribute) == value,
        "co": getattr(myclass, attribute).ilike(f"%{value}%"),
        "sw": getattr(myclass, attribute).ilike(f"{value}%"),
        "gt": getattr(myclass, attribute) > value,
        "ge": getattr(myclass, attribute) >= value,
        "lt": getattr(myclass, attribute) < value,
        "le": getattr(myclass, attribute) <= value
    }

    if operator in filter_map:
        query = query.filter(filter_map[operator])

    return query
