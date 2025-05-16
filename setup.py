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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=PYTHON_REQUIRES,
    install_requires=[
        "apscheduler>=3.11.0",                  # Programacion de tareas.
        "python-dotenv>=1.0.1",                 # Carga de variables de entorno desde un archivo .env
        "requests>=2.32.3",                     # Peticiones HTTP
        "rich>=13.9.4",                         # Libreria para la impresion de mensajes en consola
        "psutil>=7.0.0",                        # Libreria para la obtencion de datos del sistema
        "cryptography>=44.0.3",                 # Libreria para la encriptacion de datos
    ],
    entry_points={
        "console_scripts": [
            "orionis=orionis.console:main"
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
