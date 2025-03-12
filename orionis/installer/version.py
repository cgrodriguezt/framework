import requests
from orionis.framework import API

def check_version():
    """
    Checks the current API version and compares it with the installed version.

    Returns
    -------
    str
        The latest available version from the API.
    """
    try:

        response = requests.get(API, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest_version = data.get("info", {}).get("version")

        if not latest_version:
            raise ValueError("Version information not found in API response.")

        return latest_version

    except requests.RequestException as e:

        return None