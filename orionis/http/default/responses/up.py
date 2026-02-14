from pathlib import Path

class UpPage:

    @staticmethod
    def response() -> tuple[bytes, list[tuple[str, str]]]:
        """
        Return the HTTP response for the "up" page.

        Returns
        -------
        tuple of bytes and list of tuple of str
            The response body as bytes and a list of HTTP headers.
        """
        # Load the HTML content for the "up" page from the filesystem
        page_path = Path(__file__).parent.parent / "pages" / "up.html"
        with page_path.open("rb") as f:
            body = f.read()

        # Prepare headers for HTML content and disable caching
        return body, [
            ("content-type", "text/html; charset=utf-8"),
            ("cache-control", "no-cache"),
        ]
