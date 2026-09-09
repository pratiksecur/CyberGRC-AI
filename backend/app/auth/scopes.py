from enum import Enum


class AccessScope(str, Enum):
    """
    Defines the organizational scope of a user's access.
    """

    OWN = "own"

    SUBORDINATES = "subordinates"

    ORGANIZATION = "organization"