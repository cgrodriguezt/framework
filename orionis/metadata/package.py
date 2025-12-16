import requests
from typing import Final
from orionis.metadata.framework import API

class PypiOrionisPackage(metaclass=Final):

    def __init__(self) -> None:
        """
        Initialize the PypiOrionisPackage instance.

        Sets up the base URL for the Orionis PyPI package, initializes the internal
        information dictionary, and fetches all available package metadata from PyPI.

        Returns
        -------
        None
            This method does not return any value. It initializes instance attributes
            and populates the `_info` dictionary with package metadata.
        """
        # Set the base URL for the PyPI API endpoint
        self._base_url = API

        # Initialize the dictionary to store package metadata
        self._info = {}

        # Fetch and populate metadata from PyPI
        self.getAllData()

    def getAllData(self) -> dict:
        """
        Fetch and update package metadata from the PyPI API.

        Sends a GET request to the PyPI JSON API endpoint specified by
        `self._base_url`. Updates the internal `_info` attribute with the value
        associated with the "info" key from the response.

        Returns
        -------
        dict
            Dictionary containing the package metadata retrieved from PyPI.

        Raises
        ------
        ConnectionError
            If the request to the PyPI API fails or returns a non-200 status code.
        ValueError
            If the response structure is invalid or missing the "info" key.
        """
        try:
            # Send a GET request to the PyPI API endpoint with a timeout
            response = requests.get(self._base_url, timeout=10)
            response.raise_for_status()

            # Parse the JSON response
            data: dict = response.json()

            # Extract the 'info' section containing package metadata
            self._info = data.get("info", {})

            # Raise an error if 'info' key is missing or empty
            if not self._info:
                error_msg = "No 'info' key found in PyPI response."
                raise ValueError(error_msg)

            # Return the package metadata dictionary
            return self._info

        except requests.RequestException as e:
            # Handle network or HTTP errors
            error_msg = (
                f"Error fetching data from PyPI: {e}. "
                "Please check your internet connection or try again later."
            )
            raise ConnectionError(error_msg) from e

        except ValueError as ve:
            # Handle invalid response structure
            error_msg = f"Invalid response structure from PyPI: {ve}"
            raise ValueError(error_msg) from ve

    def getName(self) -> str:
        """
        Return the package name from the internal metadata dictionary.

        Accesses the '_info' attribute, which contains metadata fetched from the
        PyPI API, and returns the value associated with the 'name' key.

        Returns
        -------
        str
            The name of the package as specified in the PyPI metadata.

        Raises
        ------
        KeyError
            If the 'name' key is missing in the '_info' dictionary.
        """
        # Return the package name from the metadata dictionary
        return self._info["name"]

    def getVersion(self) -> str:
        """
        Return the version string of the Orionis framework.

        Access the '_info' dictionary and retrieve the value associated with the
        'version' key.

        Returns
        -------
        str
            Version string of the Orionis framework as specified in the PyPI metadata.

        Raises
        ------
        KeyError
            If the 'version' key is missing in the '_info' dictionary.
        """
        # Return the version string from the metadata dictionary
        return self._info["version"]

    def getAuthor(self) -> str:
        """
        Return the author's name from the package metadata.

        Access the '_info' dictionary, which contains metadata fetched from the
        PyPI API, and return the value associated with the 'author' key.

        Returns
        -------
        str
            The author's name as specified in the PyPI metadata.

        Raises
        ------
        KeyError
            If the 'author' key is missing in the '_info' dictionary.
        """
        # Return the author's name from the metadata dictionary
        return self._info["author"]

    def getAuthorEmail(self) -> str:
        """
        Return the author's email address from the package metadata.

        Access the '_info' dictionary, which contains metadata fetched from the
        PyPI API, and return the value associated with the 'author_email' key.

        Returns
        -------
        str
            The author's email address as specified in the PyPI metadata.

        Raises
        ------
        KeyError
            If the 'author_email' key is missing in the '_info' dictionary.
        """
        # Return the author's email address from the metadata dictionary
        return self._info["author_email"]

    def getDescription(self) -> str:
        """
        Return the summary description of the Orionis framework package.

        Access the internal `_info` dictionary and return the value associated
        with the 'summary' key. The summary provides a brief description of the
        package as registered on PyPI.

        Returns
        -------
        str
            The summary description of the Orionis framework package from the
            '_info' dictionary under the 'summary' key.
        """
        # Return the summary description from the metadata dictionary
        return self._info["summary"]

    def getUrl(self) -> str:
        """
        Return the homepage URL of the Orionis framework package.

        Retrieves the homepage URL from the 'project_urls' sub-dictionary under
        the 'Homepage' key in the internal `_info` dictionary.

        Returns
        -------
        str
            Homepage URL as specified in the PyPI metadata under
            `_info['project_urls']['Homepage']`.

        Raises
        ------
        KeyError
            If the 'Homepage' key is missing in the 'project_urls' dictionary.
        """
        # Return the homepage URL from the project_urls metadata
        return self._info["project_urls"]["Homepage"]

    def getLongDescription(self) -> str:
        """
        Return the long description of the Orionis framework package.

        Access the internal `_info` dictionary and return the value associated
        with the 'description' key. The long description provides a detailed
        overview of the package as registered on PyPI.

        Returns
        -------
        str
            The long description text of the Orionis framework package from the
            '_info' dictionary under the 'description' key.
        """
        # Return the long description from the metadata dictionary
        return self._info["description"]

    def getDescriptionContentType(self) -> str:
        """
        Return the content type of the package description.

        Retrieves the value of the 'description_content_type' key from the internal
        metadata dictionary, indicating the format of the package's long description.

        Returns
        -------
        str
            The content type of the package description, such as 'text/markdown' or
            'text/plain'.
        """
        # Return the content type for the package description from metadata
        return self._info["description_content_type"]

    def getLicense(self) -> str:
        """
        Return the license type from the package metadata.

        Retrieves the value of the 'license' key from the internal `_info`
        dictionary. If the license is not set or is an empty string, returns "MIT".

        Returns
        -------
        str
            License type as specified in the PyPI metadata, or "MIT" if not set.
        """
        # Return the license type from metadata, defaulting to "MIT" if empty
        return self._info["license"] or "MIT"

    def getClassifiers(self) -> list:
        """
        Retrieve the list of classifiers for the Orionis framework package.

        Access the internal `_info` dictionary and return the value associated
        with the 'classifiers' key. Classifiers are standardized strings used by
        PyPI to categorize the package.

        Returns
        -------
        list of str
            List of classifier strings from the PyPI metadata under the
            'classifiers' key.

        Raises
        ------
        KeyError
            If the 'classifiers' key is missing in the '_info' dictionary.
        """
        # Return the list of classifiers from the metadata dictionary
        return self._info["classifiers"]

    def getPythonVersion(self) -> str:
        """
        Retrieve the required Python version specification.

        Access the internal `_info` dictionary and return the value associated
        with the 'requires_python' key. This specifies the Python version(s)
        required by the Orionis framework package.

        Returns
        -------
        str
            Python version specification required by the framework, as defined in
            the '_info' dictionary under the 'requires_python' key.

        Raises
        ------
        KeyError
            If the 'requires_python' key is missing in the '_info' dictionary.
        """
        # Return the required Python version specification from the metadata
        return self._info["requires_python"]

    def getKeywords(self) -> list:
        """
        Retrieve the list of keywords for the Orionis framework package.

        Access the internal `_info` dictionary and return the value associated with
        the 'keywords' key. Keywords describe the package's functionality or domain.

        Returns
        -------
        list of str
            List of keywords from the PyPI metadata under the 'keywords' key.

        Raises
        ------
        KeyError
            If the 'keywords' key is missing in the '_info' dictionary.
        """
        # Return the list of keywords from the metadata dictionary
        return self._info["keywords"]
