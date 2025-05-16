"""
This module initializes the Orionis framework package and exposes its main components.
Exports:
    Orionis: The main application class from the luminate app module.
    NAME: The name of the framework.
    VERSION: The current version of the framework.
    AUTHOR: The author of the framework.
    AUTHOR_EMAIL: The email address of the framework's author.
    DESCRIPTION: A brief description of the framework.
    SKELETON: The default project skeleton or template.
    FRAMEWORK: The core framework object or identifier.
    DOCS: Documentation resources or links.
    API: API definitions or endpoints.
    PYTHON_REQUIRES: The minimum required Python version for the framework.
This module serves as the entry point for the Orionis framework, aggregating and exposing
essential metadata and components for external use.
"""

from orionis.luminate.app import Orionis
from orionis.framework import (
    NAME,
    VERSION,
    AUTHOR,
    AUTHOR_EMAIL,
    DESCRIPTION,
    SKELETON,
    FRAMEWORK,
    DOCS,
    API,
    PYTHON_REQUIRES
)

__all__ = [
    "Orionis",
    "NAME",
    "VERSION",
    "AUTHOR",
    "AUTHOR_EMAIL",
    "DESCRIPTION",
    "SKELETON",
    "FRAMEWORK",
    "DOCS",
    "API",
    "PYTHON_REQUIRES"
]