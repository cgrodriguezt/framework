from pathlib import Path
from orionis.foundation.config.roots.paths import Paths

class BootstrapPaths(Paths):

    # ------------------------------------------------------------------------
    # root : Path
    #    - The root directory of the project.
    #    - Defaults to the current working directory.
    # ------------------------------------------------------------------------
    root = Path.cwd().resolve()

    # ------------------------------------------------------------------------
    # app : Path
    #    - The main application directory.
    #    - Defaults to "app" directory within the root.
    # ------------------------------------------------------------------------
    app = (Path.cwd() / 'app').resolve()

    # ------------------------------------------------------------------------
    # console : Path
    #    - Directory containing subfolders for console commands and scheduler.py.
    # ------------------------------------------------------------------------
    console = (Path.cwd() / 'app' / 'console').resolve()

    # ------------------------------------------------------------------------
    # exceptions : Path
    #    - Directory containing exception handler classes.
    # ------------------------------------------------------------------------
    exceptions = (Path.cwd() / 'app' / 'exceptions').resolve()

    # ------------------------------------------------------------------------
    # http : Path
    #    - Directory containing HTTP-related classes (controllers, middleware, requests).
    # ------------------------------------------------------------------------
    http = (Path.cwd() / 'app' / 'http').resolve()

    # ------------------------------------------------------------------------
    # models : Path
    #    - Directory containing ORM model classes.
    # ------------------------------------------------------------------------
    models = (Path.cwd() / 'app' / 'models').resolve()

    # ------------------------------------------------------------------------
    # providers : Path
    #    - Directory containing service provider classes.
    # ------------------------------------------------------------------------
    providers = (Path.cwd() / 'app' / 'providers').resolve()

    # ------------------------------------------------------------------------
    # notifications : Path
    #    - Directory containing notification classes.
    # ------------------------------------------------------------------------
    notifications = (Path.cwd() / 'app' / 'notifications').resolve()

    # ------------------------------------------------------------------------
    # services : Path
    #    - Directory containing business logic service classes.
    # ------------------------------------------------------------------------
    services = (Path.cwd() / 'app' / 'services').resolve()

    # ------------------------------------------------------------------------
    # jobs : Path
    #    - Directory containing queued job classes.
    # ------------------------------------------------------------------------
    jobs = (Path.cwd() / 'app' / 'jobs').resolve()

    # ------------------------------------------------------------------------
    # bootstrap : Path
    #    - Directory containing application bootstrap files.
    # ------------------------------------------------------------------------
    bootstrap = (Path.cwd() / 'bootstrap').resolve()

    # ------------------------------------------------------------------------
    # config : Path
    #    - Directory containing application configuration files.
    # ------------------------------------------------------------------------
    config = (Path.cwd() / 'config').resolve()

    # ------------------------------------------------------------------------
    # database : Path
    #    - Directory containing the SQLite database file.
    # ------------------------------------------------------------------------
    database = (Path.cwd() / 'database' / 'database').resolve()

    # ------------------------------------------------------------------------
    # resources : Path
    #    - Directory containing application resources (views, lang, assets).
    # ------------------------------------------------------------------------
    resources = (Path.cwd() / 'resources').resolve()

    # ------------------------------------------------------------------------
    # routes : Path
    #    - Path to the web routes definition file.
    # ------------------------------------------------------------------------
    routes = (Path.cwd() / 'routes').resolve()

    # ------------------------------------------------------------------------
    # storage : Path
    #    - Directory for application storage files.
    # ------------------------------------------------------------------------
    storage = (Path.cwd() / 'storage').resolve()

    # ------------------------------------------------------------------------
    # tests : Path
    #    - Directory containing test files.
    # ------------------------------------------------------------------------
    tests = (Path.cwd() / 'tests').resolve()