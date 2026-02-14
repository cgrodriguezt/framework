from orionis.services.file.contracts.directory import IDirectory

class Favicon:

    @staticmethod
    def response(
        dir: IDirectory
    ) -> tuple:
        """
        Retrieve the contents and headers for the favicon file if it exists.

        Parameters
        ----------
        dir : IDirectory
            Directory interface providing access to public storage.

        Returns
        -------
        tuple of (bytes or None, list of tuple of bytes or None)
            Tuple containing the favicon file contents and headers if found,
            otherwise (None, None).
        """
        # Get the public storage directory
        public_storage = dir.storagePublic()

        # Initialize variables
        bytes_content: bytes | None = None
        headers: list[tuple[bytes, bytes]] = []
        headers.append(("cache-control", "public, max-age=31536000"))

        # Try to extract PNG favicon
        favicon_path = public_storage / 'favicon.png'
        if favicon_path.exists():
            with open(favicon_path, 'rb') as f:
                bytes_content = f.read()
                headers.append(("content-type", "image/png"))
                return headers, bytes_content

        # Try to extract SVG favicon
        favicon_path = public_storage / 'favicon.svg'
        if favicon_path.exists():
            with open(favicon_path, 'rb') as f:
                bytes_content = f.read()
                headers.append(("content-type", "image/svg+xml"))
                return headers, bytes_content

        # Try to extract ICO favicon
        favicon_path = public_storage / 'favicon.ico'
        if favicon_path.exists():
            with open(favicon_path, 'rb') as f:
                bytes_content = f.read()
                headers.append(("content-type", "image/x-icon"))
                return headers, bytes_content

        # Return None if no favicon is found
        return None, None