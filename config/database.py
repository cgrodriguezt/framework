from dataclasses import dataclass
from orionis.foundation.config.database.entities.connections import Connections
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.database.entities.mysql import MySQL
from orionis.foundation.config.database.entities.oracle import Oracle
from orionis.foundation.config.database.entities.pgsql import PGSQL
from orionis.foundation.config.database.entities.sqlite import SQLite
from orionis.foundation.config.database.enums.mysql_charsets import MySQLCharset
from orionis.foundation.config.database.enums.mysql_collations import MySQLCollation
from orionis.foundation.config.database.enums.mysql_engine import MySQLEngine
from orionis.foundation.config.database.enums.oracle_encoding import OracleEncoding
from orionis.foundation.config.database.enums.oracle_nencoding import OracleNencoding
from orionis.foundation.config.database.enums.pgsql_charsets import PGSQLCharset
from orionis.foundation.config.database.enums.pgsql_mode import PGSQLSSLMode
from orionis.foundation.config.database.enums.sqlite_foreign_key import SQLiteForeignKey
from orionis.foundation.config.database.enums.sqlite_journal import SQLiteJournalMode
from orionis.foundation.config.database.enums.sqlite_synchronous import SQLiteSynchronous
from orionis.services.environment.env import Env

@dataclass
class BootstrapDatabase(Database):

    # -------------------------------------------------------------------------
    # default : str
    #    - The name of the default database connection to use.
    #    - Defaults to the value of the "DB_CONNECTION" environment variable, or "sqlite" if not set.
    # -------------------------------------------------------------------------
    default = Env.get("DB_CONNECTION", "sqlite")

    # -------------------------------------------------------------------------
    # connections : Connections | dict
    #    - The different database connections available to the application.
    #    - Defaults to an instance of Connections with default values if not set.
    # -------------------------------------------------------------------------
    connections = Connections(

        # ---------------------------------------------------------------------
        # sqlite : SQLite
        #    - Configuration for the SQLite database connection.
        #    - Defaults to values from environment variables or sensible defaults.
        # ---------------------------------------------------------------------
        sqlite = SQLite(
            driver = 'sqlite',
            url = Env.get('DB_URL', 'sqlite:///' + Env.get('DB_DATABASE', 'database/database.sqlite')),
            database= Env.get('DB_DATABASE', 'database.sqlite'),
            prefix = Env.get('DB_PREFIX', ''),
            foreign_key_constraints = Env.get('DB_FOREIGN_KEYS', SQLiteForeignKey.OFF),
            busy_timeout = Env.get('DB_BUSY_TIMEOUT', 5000),
            journal_mode = Env.get('DB_JOURNAL_MODE', SQLiteJournalMode.DELETE),
            synchronous= Env.get('DB_SYNCHRONOUS', SQLiteSynchronous.NORMAL)
        ),

        # ---------------------------------------------------------------------
        # mysql : MySQL
        #    - Configuration for the MySQL database connection.
        #    - Defaults to values from environment variables or sensible defaults.
        # ---------------------------------------------------------------------
        mysql = MySQL(
            driver = "mysql",
            host = Env.get("DB_HOST", "127.0.0.1"),
            port = Env.get("DB_PORT", 3306),
            database = Env.get("DB_DATABASE", "orionis"),
            username = Env.get("DB_USERNAME", "root"),
            password = Env.get("DB_PASSWORD", ""),
            unix_socket = Env.get("DB_SOCKET", ""),
            charset = MySQLCharset.UTF8MB4,
            collation = MySQLCollation.UTF8MB4_UNICODE_CI,
            prefix = "",
            prefix_indexes = True,
            strict = True,
            engine = MySQLEngine.INNODB
        ),

        # ---------------------------------------------------------------------
        # pgsql : PGSQL
        #    - Configuration for the PostgreSQL database connection.
        #    - Defaults to values from environment variables or sensible defaults.
        # ---------------------------------------------------------------------
        pgsql = PGSQL(
            driver = "pgsql",
            host = Env.get("DB_HOST", "127.0.0.1"),
            port = Env.get("DB_PORT", 5432),
            database = Env.get("DB_DATABASE", "orionis"),
            username = Env.get("DB_USERNAME", "postgres"),
            password = Env.get("DB_PASSWORD", ""),
            charset = Env.get("DB_CHARSET", PGSQLCharset.UTF8),
            prefix = "",
            prefix_indexes = True,
            search_path = "public",
            sslmode = PGSQLSSLMode.PREFER
        ),

        # ---------------------------------------------------------------------
        # oracle : Oracle
        #    - Configuration for the Oracle database connection.
        #    - Defaults to values from environment variables or sensible defaults.
        # ---------------------------------------------------------------------
        oracle = Oracle(
            driver = "oracle",
            username = Env.get("DB_USERNAME", "sys"),
            password = Env.get("DB_PASSWORD", ""),
            host = Env.get("DB_HOST", "localhost"),
            port = Env.get("DB_PORT", 1521),
            service_name = Env.get("DB_SERVICE_NAME", "ORCL"),
            sid = Env.get("DB_SID", None),
            dsn = Env.get("DB_DSN", None),
            tns_name = Env.get("DB_TNS", None),
            encoding = Env.get("DB_ENCODING", OracleEncoding.AL32UTF8),
            nencoding = Env.get("DB_NENCODING", OracleNencoding.AL32UTF8)
        )

    )