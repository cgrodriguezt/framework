from __future__ import annotations
from pathlib import Path

#---------------------------------------------------------------------------
# Framework Metadata
#---------------------------------------------------------------------------

NAME = "orionis"

# Current version of the framework
VERSION = "0.750.0"

# Full name of the author or maintainer of the project
AUTHOR = "Raul Mauricio Uñate Castro"

# Email address of the author or maintainer for contact purposes
AUTHOR_EMAIL = "raulmauriciounate@gmail.com"

# Short description of the project or framework
DESCRIPTION = "Orionis Framework - Elegant, Fast, and Powerful."

#---------------------------------------------------------------------------
# Project URLs
#---------------------------------------------------------------------------

# URL to the project's skeleton or template repository (for initial setup)
SKELETON = "https://github.com/orionis-framework/skeleton"

# URL to the project's main framework repository
FRAMEWORK = "https://github.com/orionis-framework/framework"

# URL to the project's documentation
DOCS = "https://orionis-framework.com/"

# API URL to the project's JSON data
API = "https://pypi.org/pypi/orionis/json"

#---------------------------------------------------------------------------
# Python Requirements
#---------------------------------------------------------------------------

# Minimum Python version required to run the project
PYTHON_REQUIRES = ">=3.12"

#---------------------------------------------------------------------------
# Project Classifiers
#---------------------------------------------------------------------------

# List of classifiers that provide metadata about the project for PyPI and other tools.
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Internet :: WWW/HTTP :: WSGI",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

#---------------------------------------------------------------------------
# Project Keywords
#---------------------------------------------------------------------------

# List of keywords that describe the project and help with discoverability.
KEYWORDS = [
    "orionis",
    "framework",
    "python",
    "orionis-framework",
    "granian",
    "asgi",
    "rsgi",
]

#---------------------------------------------------------------------------
# Project Dependencies
#---------------------------------------------------------------------------

# List of required packages and their minimum versions.
REQUIRES = [
    "apscheduler~=3.11.0",
    "python-dotenv~=1.2.0",
    "requests~=2.32.0",
    "rich~=14.3.0",
    "psutil~=7.2.0",
    "cryptography~=46.0.0",
    "setuptools~=80.10.0",
    "wheel~=0.46.0",
    "twine~=6.2.0",
    "pyclean~=3.5.0",
    "dotty-dict~=1.3.0",
    "granian[dotenv, reload, uvloop, pname, winloop]>=2.7.0",
    "pendulum~=3.2.0",
]

#---------------------------------------------------------------------------
# Function to retrieve the icon SVG code
#---------------------------------------------------------------------------

def icon() -> str | None:
    """
    Return the SVG code for the project's icon image.

    Reads the 'icon.svg' file located in the same directory as this module and
    returns its content as a string. Returns None if the file is not found or
    cannot be read.

    Returns
    -------
    str or None
        SVG code as a string if the file is successfully read, otherwise None.
    """
    path = (Path(__file__).parent / "icon.svg").resolve()
    try:
        with path.open(encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None
