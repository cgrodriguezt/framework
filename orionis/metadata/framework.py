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
DESCRIPTION = (
    "Orionis Framework — "
    "Async-first full-stack framework for modern Python applications."
)

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
PYTHON_REQUIRES = ">=3.14"

#---------------------------------------------------------------------------
# Project Classifiers
#---------------------------------------------------------------------------

# List of classifiers that provide metadata about the project for PyPI and other tools.
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Environment :: Web Environment",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.14",
    "Typing :: Typed",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Framework :: AsyncIO",
]

#---------------------------------------------------------------------------
# Project Keywords
#---------------------------------------------------------------------------

# List of keywords that describe the project and help with discoverability.
KEYWORDS = [
    "orionis",
    "async framework",
    "asgi framework",
    "rsgi framework",
    "python 3.14",
    "asyncio",
    "dependency injection",
    "service container",
    "service providers",
    "facades",
    "mvc",
    "full stack framework",
    "web framework",
    "api framework",
    "websockets",
    "real time applications",
]

#---------------------------------------------------------------------------
# Project Dependencies
#---------------------------------------------------------------------------

# List of required packages and their minimum versions.
REQUIRES = [
    "apscheduler~=3.11.0",
    "python-dotenv~=1.2.0",
    "rich~=14.3.0",
    "psutil~=7.2.0",
    "cryptography~=46.0.0",
    "granian[dotenv, reload, uvloop, pname, winloop]>=2.7.0",
    "pendulum~=3.2.0",
    "uvloop; sys_platform != 'win32'",
    "winloop; sys_platform == 'win32'",
]

#---------------------------------------------------------------------------
# Function to retrieve the icon SVG code
#---------------------------------------------------------------------------

def icon() -> str | None:
    """
    Returns the SVG code for the project's icon.

    Attempts to read 'icon.svg' located in the same directory as this module.
    Returns the SVG content as a string, or None if the file does not exist or cannot be read.

    Returns
    -------
    str | None
        SVG code as a string if successful, otherwise None.
    """
    icon_path = Path(__file__).with_name("icon.svg")
    try:
        return icon_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
