from enum import Enum

class EnvironmentValueType(Enum):
    """Define supported types for casting environment variable values.

    Attributes
    ----------
    BASE64 : str
        Base64 encoded value type.
    PATH : str
        File system path type.
    STR : str
        String value type.
    INT : str
        Integer value type.
    FLOAT : str
        Floating-point value type.
    BOOL : str
        Boolean value type.
    LIST : str
        List value type.
    DICT : str
        Dictionary value type.
    TUPLE : str
        Tuple value type.
    SET : str
        Set value type.
    """

    BASE64  = "base64"  # Base64 encoded type
    PATH    = "path"      # File system path type
    STR     = "str"        # String type
    INT     = "int"        # Integer type
    FLOAT   = "float"    # Floating-point type
    BOOL    = "bool"      # Boolean type
    LIST    = "list"      # List type
    DICT    = "dict"      # Dictionary type
    TUPLE   = "tuple"    # Tuple type
    SET     = "set"        # Set type
