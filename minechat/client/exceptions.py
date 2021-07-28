class BaseClientException(Exception):
    """Base client exception class."""

    error_msg: str

    def __init__(self, error_msg: str):
        self.error_msg = error_msg

    def __str__(self):
        return f"Client exception: {self.error_msg}"


class AuthenticationError(BaseClientException):
    """Client not authenticated."""
