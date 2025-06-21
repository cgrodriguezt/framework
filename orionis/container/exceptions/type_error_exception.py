class OrionisContainerTypeError(TypeError):
    """
    Custom exception for TypeError related to the Orionis container.
    """

    def __init__(self, message: str) -> None:
        """
        Initializes the exception with an error message.

        Args:
            message (str): Descriptive error message.
        """
        super().__init__(message)

    def __str__(self) -> str:
        """Returns a string representation of the exception."""
        return f"[OrionisContainerTypeError] {self.args[0]}"