from orionis.http.multipart_stream_parser.upload_file import UploadedFile

class MultipartPart:

    __slots__ = (
        "headers",
        "name",
        "filename",
        "content_type",
        "is_file",
        "data",
    )

    def __init__(self, headers: dict[str, str], memory_threshold: int) -> None:
        """
        Initialize a MultipartPart instance.

        Parameters
        ----------
        headers : dict[str, str]
            The headers for this multipart part.
        memory_threshold : int
            The memory threshold for file uploads.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        self.headers = headers

        # Parse Content-Disposition header for attributes
        disposition = headers.get("content-disposition", "")
        attrs = self._parseContentDisposition(disposition)

        self.name: str | None = attrs.get("name")
        self.filename: str | None = attrs.get("filename")
        self.content_type: str | None = headers.get("content-type")

        self.is_file: bool = self.filename is not None

        # Store data as UploadedFile if file, else as bytearray
        if self.is_file:
            self.data: UploadedFile = UploadedFile(
                self.filename, self.content_type, memory_threshold
            )
        else:
            self.data: bytearray = bytearray()

    def _parseContentDisposition(self, disposition: str) -> dict[str, str]:
        """
        Parse the Content-Disposition header into attribute dictionary.

        Parameters
        ----------
        disposition : str
            Content-Disposition header value.

        Returns
        -------
        dict[str, str]
            Dictionary containing parsed attributes.
        """
        attrs: dict[str, str] = {}
        # Split header by semicolon and process each attribute
        for part in disposition.split(";"):
            part = part.strip()
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip().lower()
                value = value.strip()
                # Remove surrounding quotes if present
                if (
                    (value.startswith('"') and value.endswith('"')) or
                    (value.startswith("'") and value.endswith("'"))
                ):
                    value = value[1:-1]
                # Unescape any escaped quotes
                value = value.replace('\\"', '"').replace("\\'", "'")
                attrs[key] = value
        return attrs

    def write(self, chunk: bytes) -> None:
        """
        Write a chunk of data to this part.

        Parameters
        ----------
        chunk : bytes
            The data chunk to write.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Write to UploadedFile or extend bytearray depending on part type
        if self.is_file:
            self.data.write(chunk)
        else:
            self.data.extend(chunk)

    def finalize(self) -> UploadedFile | str:
        """
        Finalize the part and return its content.

        Returns
        -------
        UploadedFile or str
            The UploadedFile instance if this is a file part, otherwise the
            decoded string content.
        """
        # Return decoded string for non-file, UploadedFile for file
        if not self.is_file:
            return self.data.decode("utf-8")
        return self.data