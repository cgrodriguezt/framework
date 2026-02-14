class WellKnown:

    @staticmethod
    def response() -> tuple[bytes, dict[str, str]]:
        """
        Return the well-known response headers and body.

        Returns
        -------
        tuple[bytes, dict[str, str]]
            A tuple containing the response body as bytes and a dictionary of
            HTTP headers.
        """
        # Return an empty JSON body and standard headers for well-known endpoints
        return {}, [
            ("content-type", "application/json"),
            ("cache-control", "public, max-age=86400"),
        ]