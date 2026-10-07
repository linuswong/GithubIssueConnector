"""Expected failures that the connector turns into JSON results."""


class ConnectorError(Exception):
    """Carry an agreed error code and a useful, credential-free message."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
