from enum import Enum

class OracleNencoding(Enum):
    """
    Represent Oracle encoding types for NCHAR and NVARCHAR2 data types.

    This class defines constants for Oracle's national character set encodings.
    It can be extended to implement custom behaviors or properties related to
    Oracle's national character set encoding.

    Attributes
    ----------
    AL32UTF8 : str
        Unicode UTF-8 (recommended).
    AR8MSWIN1256 : str
        Arabic Windows encoding.
    JA16EUC : str
        Japanese EUC encoding.
    JA16SJIS : str
        Japanese Shift-JIS encoding.
    KO16MSWIN949 : str
        Korean Windows encoding.
    TH8TISASCII : str
        Thai encoding.
    TR8MSWIN1254 : str
        Turkish Windows encoding.
    WE8ISO8859P1 : str
        Western European ISO encoding.
    WE8MSWIN1252 : str
        Western European Windows encoding.
    ZHS16GBK : str
        Simplified Chinese GBK encoding.
    ZHT16BIG5 : str
        Traditional Chinese Big5 encoding.
    ZHT32EUC : str
        Traditional Chinese EUC encoding.
    CL8MSWIN1251 : str
        Cyrillic Windows encoding.
    EE8MSWIN1250 : str
        Central European Windows encoding.
    EL8MSWIN1253 : str
        Greek Windows encoding.
    IW8MSWIN1255 : str
        Hebrew Windows encoding.

    Returns
    -------
    OracleNencoding
        An enumeration member representing the Oracle encoding type.
    """

    AL32UTF8 = "AL32UTF8"              # Unicode UTF-8 (recommended)
    AR8MSWIN1256 = "AR8MSWIN1256"      # Arabic Windows
    JA16EUC = "JA16EUC"                # Japanese EUC
    JA16SJIS = "JA16SJIS"              # Japanese Shift-JIS
    KO16MSWIN949 = "KO16MSWIN949"      # Korean Windows
    TH8TISASCII = "TH8TISASCII"        # Thai
    TR8MSWIN1254 = "TR8MSWIN1254"      # Turkish Windows
    WE8ISO8859P1 = "WE8ISO8859P1"      # Western European ISO
    WE8MSWIN1252 = "WE8MSWIN1252"      # Western European Windows
    ZHS16GBK = "ZHS16GBK"              # Simplified Chinese GBK
    ZHT16BIG5 = "ZHT16BIG5"            # Traditional Chinese Big5
    ZHT32EUC = "ZHT32EUC"              # Traditional Chinese EUC
    CL8MSWIN1251 = "CL8MSWIN1251"      # Cyrillic Windows
    EE8MSWIN1250 = "EE8MSWIN1250"      # Central European Windows
    EL8MSWIN1253 = "EL8MSWIN1253"      # Greek Windows
    IW8MSWIN1255 = "IW8MSWIN1255"      # Hebrew Windows
