class Comment:

    def __init__(self, text: str) -> None:
        """
        Initialize a Comment instance.

        Parameters
        ----------
        text : str
            The comment text content.

        Returns
        -------
        None
        """
        # Store the comment text.
        self.text = text.strip()
