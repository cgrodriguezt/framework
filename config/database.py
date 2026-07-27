from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.database import (
    Connections, Database, MySQL, Oracle, PGSQL, SQLite,
    SQLServer, ConnectionName, MySQLCharset, MySQLCollation,
    MySQLEngine, OracleEncoding, OracleNencoding, PGSQLCharset,
    PGSQLSSLMode, SQLiteForeignKey, SQLiteJournalMode, SQLiteSynchronous,
)
from orionis.environment import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapDatabase(Database):

    # ----------------------------------------------------------------------------------
    # default : ConnectionName | str, optional
    # --- The default database connection name. Uses the 'DB_CONNECTION' environment
    # --- variable or defaults to 'ConnectionName.SQLITE' if not set.
    # ruff: noqa: E501 (Intentionally long lines for configuration clarity.)
    # ----------------------------------------------------------------------------------
    default: ConnectionName | str = field(
        default_factory=lambda: Env.get("DB_CONNECTION", ConnectionName.SQLITE),
    )

    # ----------------------------------------------------------------------------------
    # connections : Connections | dict, optional
    # --- Available database connections for the application. Defaults to a Connections
    # --- instance with preset values if not specified.
    # ----------------------------------------------------------------------------------
    connections: Connections | dict = field(
        default_factory=lambda: Connections(

            # --------------------------------------------------------------------------
            #  - SQLite database connection configuration.
            #  - Uses SQLite entity.
            #  - Defaults to 'database/database.sqlite' or values from env vars.
            #  - Sets journal mode, synchronous, and foreign key constraints as per env.
            # --------------------------------------------------------------------------
            sqlite=SQLite(
                url=Env.get("DB_URL", "sqlite:///" + Env.get("DB_DATABASE", "database/database.sqlite")),
                database=Env.get("DB_DATABASE", "database/database.sqlite"),
                prefix=Env.get("DB_PREFIX", ""),
                foreign_key_constraints=Env.get("DB_FOREIGN_KEYS", SQLiteForeignKey.OFF),
                busy_timeout=Env.get("DB_BUSY_TIMEOUT", 5000),
                journal_mode=Env.get("DB_JOURNAL_MODE", SQLiteJournalMode.DELETE),
                synchronous=Env.get("DB_SYNCHRONOUS", SQLiteSynchronous.NORMAL),
            ),

            # --------------------------------------------------------------------------
            #  - MySQL database connection configuration.
            #  - Uses MySQL entity. Defaults to 'orionis' database or values from env.
            #  - Sets charset, collation, engine, and other options as per environment.
            # --------------------------------------------------------------------------
            mysql=MySQL(
                host=Env.get("DB_HOST", "127.0.0.1"),
                port=Env.get("DB_PORT", 3306),
                database=Env.get("DB_DATABASE", "orionis"),
                username=Env.get("DB_USERNAME", "root"),
                password=Env.get("DB_PASSWORD", ""),
                unix_socket=Env.get("DB_SOCKET", ""),
                charset=MySQLCharset.UTF8MB4,
                collation=MySQLCollation.UTF8MB4_UNICODE_CI,
                prefix="",
                prefix_indexes=True,
                strict=True,
                engine=MySQLEngine.INNODB,
            ),

            # --------------------------------------------------------------------------
            #  - PostgreSQL database connection configuration.
            #  - Uses PGSQL entity. Defaults to 'orionis' database or values from env.
            #  - Sets charset, search_path, and sslmode as per environment variables.
            # --------------------------------------------------------------------------
            pgsql=PGSQL(
                host=Env.get("DB_HOST", "127.0.0.1"),
                port=Env.get("DB_PORT", 5432),
                database=Env.get("DB_DATABASE", "orionis"),
                username=Env.get("DB_USERNAME", "postgres"),
                password=Env.get("DB_PASSWORD", ""),
                charset=Env.get("DB_CHARSET", PGSQLCharset.UTF8),
                prefix="",
                prefix_indexes=True,
                search_path="public",
                sslmode=PGSQLSSLMode.PREFER,
            ),

            # --------------------------------------------------------------------------
            #  - Oracle database connection configuration.
            #  - Uses Oracle entity. Defaults to 'sys' user and 'ORCL' service or env.
            #  - Sets encoding, nencoding, and other options as per environment vars.
            # --------------------------------------------------------------------------
            oracle=Oracle(
                username=Env.get("DB_USERNAME", "sys"),
                password=Env.get("DB_PASSWORD", ""),
                host=Env.get("DB_HOST", "localhost"),
                port=Env.get("DB_PORT", 1521),
                service_name=Env.get("DB_SERVICE_NAME", "ORCL"),
                sid=Env.get("DB_SID", None),
                dsn=Env.get("DB_DSN", None),
                tns_name=Env.get("DB_TNS", None),
                encoding=Env.get("DB_ENCODING", OracleEncoding.AL32UTF8),
                nencoding=Env.get("DB_NENCODING", OracleNencoding.AL32UTF8),
            ),

            # --------------------------------------------------------------------------
            #  - Microsoft SQL Server database connection configuration.
            #  - Uses SQLServer entity. Defaults to 'sa' user or values from env.
            #  - Sets encryption and ODBC driver options as per environment vars.
            # --------------------------------------------------------------------------
            sqlserver=SQLServer(
                host=Env.get("DB_HOST", "127.0.0.1"),
                port=Env.get("DB_PORT", 1433),
                database=Env.get("DB_DATABASE", "orionis"),
                username=Env.get("DB_USERNAME", "sa"),
                password=Env.get("DB_PASSWORD", ""),
                charset=Env.get("DB_CHARSET", "utf8"),
                prefix="",
                prefix_indexes=True,
                encrypt=Env.get("DB_ENCRYPT", "yes"),
                trust_server_certificate=Env.get("DB_TRUST_SERVER_CERTIFICATE", True),
                odbc_driver=Env.get("DB_ODBC_DRIVER", "ODBC Driver 18 for SQL Server"),
            ),
        ),
    )
