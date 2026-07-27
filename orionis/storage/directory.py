from typing import TYPE_CHECKING
from orionis.foundation.contracts.application import IApplication
from orionis.storage.contracts.directory import IDirectory

if TYPE_CHECKING:
    from pathlib import Path

class Directory(IDirectory):

    # ruff: noqa: TC001

    __slots__ = ("_all_paths", "_app")

    def __init__(self, app: IApplication) -> None:
        """
        Initialize the Directory service.

        Parameters
        ----------
        app : IApplication
            The application instance used to resolve directory paths.

        Returns
        -------
        None
        """
        self._app = app
        self._all_paths = {
            "root": self._app.path("root"),
            "app": self._app.path("app"),
            "console": self._app.path("console"),
            "exceptions": self._app.path("exceptions"),
            "http": self._app.path("http"),
            "models": self._app.path("models"),
            "providers": self._app.path("providers"),
            "notifications": self._app.path("notifications"),
            "services": self._app.path("services"),
            "jobs": self._app.path("jobs"),
            "bootstrap": self._app.path("bootstrap"),
            "config": self._app.path("config"),
            "database": self._app.path("database"),
            "resources": self._app.path("resources"),
            "routes": self._app.path("routes"),
            "storage": self._app.path("storage"),
            "storagePublic": self._app.path("storage") / "app" / "public",
            "tests": self._app.path("tests"),
        }

    def root(self) -> Path:
        """
        Get the root directory of the application.

        Returns
        -------
        Path
            Path object representing the root directory.
        """
        return self._all_paths["root"]

    def app(self) -> Path:
        """
        Get the main application directory.

        Returns
        -------
        Path
            Path object representing the application directory.
        """
        return self._all_paths["app"]

    def console(self) -> Path:
        """
        Get the console directory.

        Returns
        -------
        Path
            Path object representing the console directory.
        """
        return self._all_paths["console"]

    def exceptions(self) -> Path:
        """
        Get the exceptions directory.

        Returns
        -------
        Path
            Path object representing the exceptions directory.
        """
        return self._all_paths["exceptions"]

    def http(self) -> Path:
        """
        Get the HTTP directory.

        Returns
        -------
        Path
            Path object representing the HTTP directory.
        """
        return self._all_paths["http"]

    def models(self) -> Path:
        """
        Get the models directory.

        Returns
        -------
        Path
            Path object representing the models directory.
        """
        return self._all_paths["models"]

    def providers(self) -> Path:
        """
        Get the providers directory.

        Returns
        -------
        Path
            Path object representing the providers directory.
        """
        return self._all_paths["providers"]

    def notifications(self) -> Path:
        """
        Get the notifications directory.

        Returns
        -------
        Path
            Path object representing the notifications directory.
        """
        return self._all_paths["notifications"]

    def services(self) -> Path:
        """
        Get the services directory.

        Returns
        -------
        Path
            Path object representing the services directory.
        """
        return self._all_paths["services"]

    def jobs(self) -> Path:
        """
        Get the jobs directory.

        Returns
        -------
        Path
            Path object representing the jobs directory.
        """
        return self._all_paths["jobs"]

    def bootstrap(self) -> Path:
        """
        Get the bootstrap directory.

        Returns
        -------
        Path
            Path object representing the bootstrap directory.
        """
        return self._all_paths["bootstrap"]

    def config(self) -> Path:
        """
        Get the configuration directory.

        Returns
        -------
        Path
            Path object representing the configuration directory.
        """
        return self._all_paths["config"]

    def database(self) -> Path:
        """
        Get the database directory.

        Returns
        -------
        Path
            Path object representing the database directory.
        """
        return self._all_paths["database"]

    def resources(self) -> Path:
        """
        Get the resources directory.

        Returns
        -------
        Path
            Path object representing the resources directory.
        """
        return self._all_paths["resources"]

    def routes(self) -> Path:
        """
        Get the routes directory.

        Returns
        -------
        Path
            Path object representing the routes directory.
        """
        return self._all_paths["routes"]

    def storage(self) -> Path:
        """
        Get the storage directory.

        Returns
        -------
        Path
            Path object representing the storage directory.
        """
        return self._all_paths["storage"]

    def storagePublic(self) -> Path:
        """
        Get the public storage directory.

        Returns
        -------
        Path
            Path object representing the public storage directory.
        """
        return self._all_paths["storagePublic"]

    def tests(self) -> Path:
        """
        Get the tests directory.

        Returns
        -------
        Path
            Path object representing the tests directory.
        """
        return self._all_paths["tests"]
