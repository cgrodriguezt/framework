from setuptools import setup, find_packages
from orionis.framework import *

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url=FRAMEWORK,
    packages=find_packages(
        exclude=[
            "orionis/installer",
            "orionis/installer/*",
            "orionis/static",
            "orionis/static/*"
        ]
    ),
    include_package_data=True,
    classifiers = [
        # Development status (0.X.0 → Alpha)
        "Development Status :: 3 - Alpha",

        # Environment and Framework
        "Environment :: Web Environment",
        # "Framework :: Orionis",

        # Audience and license
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

        # Python compatibility (async requires 3.12+)
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",

        # Key features (async/ASGI)
        "Typing :: Typed",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",

        # Development categories
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=PYTHON_REQUIRES,
    install_requires=[
        "apscheduler>=3.11.0",                  # Task scheduling.
        "python-dotenv>=1.0.1",                 # Load environment variables from a .env file
        "requests>=2.32.3",                     # HTTP requests
        "rich>=13.9.4",                         # Library for printing messages in the console
        "psutil>=7.0.0",                        # Library for obtaining system data
        "cryptography>=44.0.3",                 # Library for data encryption
    ],
    entry_points={
        "console_scripts": [
            "orionis = orionis.clinstall:main"
        ]
    },
    test_suite="tests",
    keywords=[
        "orionis",
        "framework",
        "python",
        "orionis-framework",
        "django",
        "flask",
        "fastapi",
        "starlette"
        "werkzeug"
        "uvicorn"
    ],
    zip_safe=True
)
