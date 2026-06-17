import shutil
from orionis.console.base.command import BaseCommand
from orionis.console.output.console import Console
from orionis.foundation.contracts.application import IApplication

# Build artifact directory names to remove during cleanup
_ARTIFACT_DIRS: tuple[str, ...] = ("build", "dist", "orionis.egg-info")

class OptimizeClearCommand(BaseCommand):

    # ruff: noqa: TC001

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = True

    # Command signature and description
    signature: str = "optimize:clear"

    # Command description
    description: str = (
        "Removes configuration, route, and command caches, "
        "Python bytecode, and build artifacts."
    )

    def handle(
        self,
        app: IApplication,
        console: Console,
    ) -> None:
        """
        Clear Python bytecode, cache directories, and build artifacts.

        Parameters
        ----------
        app : IApplication
            Application instance for path resolution.
        console : Console
            Console instance for output.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove all __pycache__ directories found recursively under the project root
        for pycache_dir in app.basePath.rglob("__pycache__"):
            shutil.rmtree(pycache_dir, ignore_errors=True)

        # Log the results of clearing bytecode and caches
        console.info("Python bytecode cleared!", timestamp=False)

        # Remove build artifact directories if they exist
        base_path = app.basePath
        for artifact_dir in _ARTIFACT_DIRS:
            artifact_path = base_path / artifact_dir
            if artifact_path.is_dir():
                shutil.rmtree(artifact_path, ignore_errors=True)

        # Log the results of clearing build artifacts
        console.info("Build artifacts cleared!", timestamp=False)

        # Remove the framework cache directory if it exists
        cache_path = app.path("storage") / "framework"
        if cache_path.exists():
            shutil.rmtree(cache_path)

        # Log the results of clearing framework cache
        console.info("Commands cache cleared!", timestamp=False)
        console.info("Route cache cleared!", timestamp=False)
        console.info("Configuration cache cleared!", timestamp=False)

        # Recreate the framework cache directory
        cache_path.mkdir(parents=True, exist_ok=True)

        # Log the results of recreating the framework cache directory
        console.info("Framework cache directory has been recreated.", timestamp=False)
