from orionis.schemas.meta.validation import ValidationMetadata

class ConstraintMetadata(ValidationMetadata):
    """
    Intermediate marker for validation constraints.

    Constraint metadata participates in value validation at decode time.
    Each concrete subclass may expose a ``message`` keyword-only field
    (default ``None``) reserved for future custom error messaging without
    breaking the public API when that feature is introduced.
    """

    __slots__ = ()
