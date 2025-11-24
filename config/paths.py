from pathlib import Path
from orionis.foundation.config.roots.paths import Paths

class BootstrapPaths(Paths):

    # ------------------------------------------------------------------------
    # root : Path
    #    - The root directory of the project.
    #    - Defaults to the current working directory.
    # ------------------------------------------------------------------------
    root: Path = Path.cwd().resolve()

    # ------------------------------------------------------------------------
    # app : Path
    #    - The main application directory.
    #    - Defaults to "app" directory within the root.
    # ------------------------------------------------------------------------
    app: Path = (Path.cwd() / 'app').resolve()

    # ------------------------------------------------------------------------
    # console : Path
    #    - Directory containing subfolders for console commands and scheduler.py.
    # ------------------------------------------------------------------------
    console: Path = (Path.cwd() / 'app' / 'console').resolve()

    # ------------------------------------------------------------------------
    # exceptions : Path
    #    - Directory containing exception handler classes.
    # ------------------------------------------------------------------------
    exceptions: Path = (Path.cwd() / 'app' / 'exceptions').resolve()

    # ------------------------------------------------------------------------
    # http : Path
    #    - Directory containing HTTP-related classes (controllers, middleware, requests).
    # ------------------------------------------------------------------------
    http: Path = (Path.cwd() / 'app' / 'http').resolve()

    # ------------------------------------------------------------------------
    # models : Path
    #    - Directory containing ORM model classes.
    # ------------------------------------------------------------------------
    models: Path = (Path.cwd() / 'app' / 'models').resolve()

    # ------------------------------------------------------------------------
    # providers : Path
    #    - Directory containing service provider classes.
    # ------------------------------------------------------------------------
    providers: Path = (Path.cwd() / 'app' / 'providers').resolve()

    # ------------------------------------------------------------------------
    # notifications : Path
    #    - Directory containing notification classes.
    # ------------------------------------------------------------------------
    notifications: Path = (Path.cwd() / 'app' / 'notifications').resolve()

    # ------------------------------------------------------------------------
    # services : Path
    #    - Directory containing business logic service classes.
    # ------------------------------------------------------------------------
    services: Path = (Path.cwd() / 'app' / 'services').resolve()

    # ------------------------------------------------------------------------
    # jobs : Path
    #    - Directory containing queued job classes.
    # ------------------------------------------------------------------------
    jobs: Path = (Path.cwd() / 'app' / 'jobs').resolve()

    # ------------------------------------------------------------------------
    # bootstrap : Path
    #    - Directory containing application bootstrap files.
    # ------------------------------------------------------------------------
    bootstrap: Path = (Path.cwd() / 'bootstrap').resolve()

    # ------------------------------------------------------------------------
    # config : Path
    #    - Directory containing application configuration files.
    # ------------------------------------------------------------------------
    config: Path = (Path.cwd() / 'config').resolve()

    # ------------------------------------------------------------------------
    # database : Path
    #    - Directory containing the SQLite database file.
    # ------------------------------------------------------------------------
    database: Path = (Path.cwd() / 'database' / 'database').resolve()

    # ------------------------------------------------------------------------
    # resources : Path
    #    - Directory containing application resources (views, lang, assets).
    # ------------------------------------------------------------------------
    resources: Path = (Path.cwd() / 'resources').resolve()

    # ------------------------------------------------------------------------
    # routes : Path
    #    - Path to the web routes definition file.
    # ------------------------------------------------------------------------
    routes: Path = (Path.cwd() / 'routes').resolve()

    # ------------------------------------------------------------------------
    # storage : Path
    #    - Directory for application storage files.
    # ------------------------------------------------------------------------
    storage: Path = (Path.cwd() / 'storage').resolve()

    # ------------------------------------------------------------------------
    # tests : Path
    #    - Directory containing test files.
    # ------------------------------------------------------------------------
    tests: Path = (Path.cwd() / 'tests').resolve()