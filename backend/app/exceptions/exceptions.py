class ResourceNotFound(Exception):
    """
    Raised when a resource does not exist.
    """

    def __init__(self, resource: str):
        self.resource = resource


class DuplicateResource(Exception):
    """
    Raised when attempting to create a duplicate resource.
    """

    def __init__(self, resource: str):
        self.resource = resource


class InvalidOperation(Exception):
    """
    Raised when a business rule is violated.
    """

    def __init__(self, message: str):
        self.message = message