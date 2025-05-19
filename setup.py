from setuptools import setup, find_packages
from orionis.framework import *

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    url=FRAMEWORK,
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(
        exclude=[
            "orionis/installer",
            "orionis/installer/*",
            "orionis/static",
            "orionis/static/*"
        ]
    ),
    include_package_data=True,
    classifiers = get_classifiers(),
    python_requires=PYTHON_REQUIRES,
    install_requires=get_requires(),
    entry_points={
        "console_scripts": [
            "orionis = orionis.clinstall:main"
        ]
    },
    test_suite="tests",
    keywords=KEYWORDS,
    zip_safe=True
)
