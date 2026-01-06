from enum import Enum

class PGSQLCollation(Enum):
    """
    Enumerate common PostgreSQL collations.

    This enumeration provides a set of commonly used collations in PostgreSQL.
    Collations determine how string comparison is performed in the database.

    Attributes
    ----------
    C : str
        Binary collation, fast, based on byte order.
    POSIX : str
        Similar to 'C', binary order.
    EN_US : str
        English (United States), case-sensitive.
    EN_US_UTF8 : str
        English (United States), UTF-8 encoding.
    ES_ES : str
        Spanish (Spain).
    ES_ES_UTF8 : str
        Spanish (Spain), UTF-8 encoding.
    DE_DE : str
        German (Germany).
    DE_DE_UTF8 : str
        German (Germany), UTF-8 encoding.

    Returns
    -------
    PGSQLCollation
        The enumeration member representing a PostgreSQL collation.
    """

    C = "C"
    POSIX = "POSIX"
    EN_US = "en_US"
    EN_US_UTF8 = "en_US.utf8"
    ES_ES = "es_ES"
    ES_ES_UTF8 = "es_ES.utf8"
    DE_DE = "de_DE"
    DE_DE_UTF8 = "de_DE.utf8"
