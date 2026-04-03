from typing import TYPE_CHECKING, Self
from orionis.support.patterns.final.meta import Final

if TYPE_CHECKING:
    from types import TracebackType

class FormData(metaclass=Final):

    def __init__(self, fields: dict, files: dict) -> None:
        """
        Initialize FormData with fields and files.

        Parameters
        ----------
        fields : dict
            Dictionary containing form fields.
        files : dict
            Dictionary containing uploaded files.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.fields = fields
        self.files = files

    def get(self, key: str, default: object | None = None) -> object | None:
        """
        Retrieve a value from fields or files by key.

        Parameters
        ----------
        key : str
            The key to look up in fields or files.
        default : object or None, optional
            The value to return if the key is not found (default is None).

        Returns
        -------
        object or None
            The value associated with the key, or default if not found.
        """
        # Check fields first, then files, else return default
        if key in self.fields:
            return self.fields[key]
        if key in self.files:
            return self.files[key]
        return default

    def __getitem__(self, key: str) -> object:
        """
        Get a value by key using dictionary-style access.

        Parameters
        ----------
        key : str
            The key to retrieve from fields or files.

        Returns
        -------
        object
            The value associated with the key, or default if not found.
        """
        return self.get(key)

    def close(self) -> None:
        """
        Close all uploaded files to free resources.

        Returns
        -------
        None
            This method does not return a value.
        """
        for file_list in self.files.values():
            if isinstance(file_list, list):
                for uploaded_file in file_list:
                    if hasattr(uploaded_file, "close"):
                        uploaded_file.close()
            elif hasattr(file_list, "close"):
                file_list.close()

    def __enter__(self) -> Self:
        """
        Enter the runtime context for FormData.

        Returns
        -------
        FormData
            The FormData instance itself.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the runtime context and clean up resources.

        Parameters
        ----------
        exc_type : type or None
            Exception type if raised, else None.
        exc_val : BaseException or None
            Exception value if raised, else None.
        exc_tb : object or None
            Traceback object if exception raised, else None.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Ensure all uploaded files are closed when exiting context
        self.close()
