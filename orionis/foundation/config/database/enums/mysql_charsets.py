from enum import Enum

class MySQLCharset(Enum):
    """
    Enumerate supported MySQL character sets for database configuration.

    Each member represents a valid MySQL character set name. These character sets
    determine how text is stored and compared in the database.

    Attributes
    ----------
    ARMSCII8 : str
        Armenian Standard Code for Information Interchange, 8-bit.
    ASCII : str
        US ASCII.
    BIG5 : str
        Big5 Traditional Chinese.
    BINARY : str
        Binary pseudo charset.
    CP1250 : str
        Windows Central European.
    CP1251 : str
        Windows Cyrillic.
    CP1256 : str
        Windows Arabic.
    CP1257 : str
        Windows Baltic.
    CP850 : str
        DOS West European.
    CP852 : str
        DOS Central European.
    CP866 : str
        DOS Russian.
    CP932 : str
        SJIS for Windows Japanese.
    DEC8 : str
        DEC West European.
    EUCJPMS : str
        UJIS for Windows Japanese.
    EUCKR : str
        EUC-KR Korean.
    GB2312 : str
        GB2312 Simplified Chinese.
    GBK : str
        GBK Simplified Chinese.
    GEOSTD8 : str
        GEOSTD8 Georgian.
    GREEK : str
        ISO 8859-7 Greek.
    HEBREW : str
        ISO 8859-8 Hebrew.
    HP8 : str
        HP West European.
    KEYBCS2 : str
        DOS Kamenicky Czech-Slovak.
    KOI8R : str
        KOI8-R Relcom Russian.
    KOI8U : str
        KOI8-U Ukrainian.
    LATIN1 : str
        cp1252 West European.
    LATIN2 : str
        ISO 8859-2 Central European.
    LATIN5 : str
        ISO 8859-9 Turkish.
    LATIN7 : str
        ISO 8859-13 Baltic.
    MACCE : str
        Mac Central European.
    MACROMAN : str
        Mac West European.
    SJIS : str
        Shift-JIS Japanese.
    SWE7 : str
        7bit Swedish.
    TIS620 : str
        TIS620 Thai.
    UCS2 : str
        UCS-2 Unicode.
    UJIS : str
        EUC-JP Japanese.
    UTF16 : str
        UTF-16 Unicode.
    UTF16LE : str
        UTF-16LE Unicode.
    UTF32 : str
        UTF-32 Unicode.
    UTF8 : str
        UTF-8 Unicode.
    UTF8MB3 : str
        UTF-8 Unicode (3-byte).
    UTF8MB4 : str
        UTF-8 Unicode (4-byte).

    Returns
    -------
    MySQLCharset
        The enumeration member representing a MySQL character set.
    """

    ARMSCII8 = "armscii8"
    ASCII = "ascii"
    BIG5 = "big5"
    BINARY = "binary"
    CP1250 = "cp1250"
    CP1251 = "cp1251"
    CP1256 = "cp1256"
    CP1257 = "cp1257"
    CP850 = "cp850"
    CP852 = "cp852"
    CP866 = "cp866"
    CP932 = "cp932"
    DEC8 = "dec8"
    EUCJPMS = "eucjpms"
    EUCKR = "euckr"
    GB2312 = "gb2312"
    GBK = "gbk"
    GEOSTD8 = "geostd8"
    GREEK = "greek"
    HEBREW = "hebrew"
    HP8 = "hp8"
    KEYBCS2 = "keybcs2"
    KOI8R = "koi8r"
    KOI8U = "koi8u"
    LATIN1 = "latin1"
    LATIN2 = "latin2"
    LATIN5 = "latin5"
    LATIN7 = "latin7"
    MACCE = "macce"
    MACROMAN = "macroman"
    SJIS = "sjis"
    SWE7 = "swe7"
    TIS620 = "tis620"
    UCS2 = "ucs2"
    UJIS = "ujis"
    UTF16 = "utf16"
    UTF16LE = "utf16le"
    UTF32 = "utf32"
    UTF8 = "utf8"
    UTF8MB3 = "utf8mb3"
    UTF8MB4 = "utf8mb4"
