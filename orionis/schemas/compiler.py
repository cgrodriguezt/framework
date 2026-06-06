from __future__ import annotations
import msgspec
from orionis.schemas.metadata import (
    Description,
    Examples,
    Extra,
    ExtraJsonSchema,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    MaxLength,
    MinLength,
    MultipleOf,
    Pattern,
    TimezoneAware,
    TimezoneNaive,
    Title,
    ValidationMetadata,
)

def _get[MetaT: ValidationMetadata](
    seen: dict[type[ValidationMetadata], ValidationMetadata],
    key: type[MetaT],
) -> MetaT | None:
    """Return the metadata instance for *key*, or ``None`` if absent."""
    return seen.get(key)  # type: ignore[return-value]

class MetadataConflictError(ValueError):
    """
    Signal incompatible or invalid metadata annotations detected by ``MetaCompiler``.

    Four conflict categories are recognized:

    * **Duplicate types** — the same concrete metadata class appears more than
      once in the annotation list (e.g., two ``MinLength`` instances).
    * **Ambiguous bounds** — both an exclusive and an inclusive variant of the
      same bound are present (e.g., ``GreaterThan`` + ``GreaterThanOrEqual``).
    * **Logically impossible ranges** — the combined constraints produce an
      empty valid set (e.g., ``MinLength(100)`` with ``MaxLength(10)``, or
      ``TimezoneAware`` with ``TimezoneNaive``).
    * **Invalid values** — a constraint carries a value that is semantically
      illegal (e.g., ``MultipleOf(0)``, ``MinLength(-1)``, ``MaxLength(-5)``).
    """

class MetaCompiler:
    """
    Compile Orionis metadata annotations into a field constraint descriptor.

    Act as the single integration point between Orionis' public metadata API
    and the underlying serialization layer. Schema consumers (validation,
    JSON Schema generation, OpenAPI export) should use this compiler so that
    the serialization layer remains an implementation detail invisible to
    application code.
    """

    # ruff: noqa: C901, PLR0912

    __slots__ = ()

    @staticmethod
    def compile(metadata: list[ValidationMetadata]) -> msgspec.Meta:
        """
        Compile metadata annotations into a field constraint descriptor.

        Parameters
        ----------
        metadata : list[ValidationMetadata]
            The list of field-level metadata annotations to compile.
            Order does not matter; each concrete type may appear at most once.

        Returns
        -------
        msgspec.Meta
            A field constraint descriptor configured with all provided
            constraints and documentation properties.

        Raises
        ------
        MetadataConflictError
            If any duplicate or logically conflicting metadata is detected
            before the descriptor is constructed.
        """
        seen = MetaCompiler._index(metadata)
        MetaCompiler._validateConflicts(seen)
        return MetaCompiler._build(seen)

    @staticmethod
    def _index(
        metadata: list[ValidationMetadata],
    ) -> dict[type[ValidationMetadata], ValidationMetadata]:
        """
        Build a ``type → instance`` mapping and reject duplicate types.

        Parameters
        ----------
        metadata : list[ValidationMetadata]
            Raw annotation list from the caller.

        Returns
        -------
        dict[type[ValidationMetadata], ValidationMetadata]
            Mapping from each concrete metadata type to its single instance.

        Raises
        ------
        MetadataConflictError
            If the same concrete type appears more than once.
        """
        seen: dict[type[ValidationMetadata], ValidationMetadata] = {}
        for meta in metadata:
            t = type(meta)
            if t in seen:
                msg = (
                    f"Duplicate metadata annotation: '{t.__name__}'"
                    " appears more than once. "
                    "Each metadata type may be used at most once per field."
                )
                raise MetadataConflictError(msg)
            seen[t] = meta
        return seen

    @staticmethod
    def _validateConflicts(
        seen: dict[type[ValidationMetadata], ValidationMetadata],
    ) -> None:
        """
        Validate the indexed metadata for semantic conflicts.

        Checks are applied in order: ambiguous bounds first, then
        impossible numeric ranges, then impossible length ranges,
        then mutually exclusive timezone flags.

        Parameters
        ----------
        seen : dict[type[ValidationMetadata], ValidationMetadata]
            The indexed metadata mapping produced by ``_index``.

        Raises
        ------
        MetadataConflictError
            On any detected conflict.
        """
        MetaCompiler._checkAmbiguousNumericBounds(seen)
        MetaCompiler._checkNumericRange(seen)
        MetaCompiler._checkLengthRange(seen)
        MetaCompiler._checkTimezone(seen)
        MetaCompiler._checkValues(seen)

    @staticmethod
    def _checkAmbiguousNumericBounds(
        seen: dict[type[ValidationMetadata], ValidationMetadata],
    ) -> None:
        """
        Reject ambiguous lower or upper numeric bounds.

        Parameters
        ----------
        seen : dict[type[ValidationMetadata], ValidationMetadata]
            Indexed metadata mapped by validation metadata type.

        Raises
        ------
        MetadataConflictError
            If both exclusive and inclusive variants of the same lower
            or upper bound are present.
        """
        if GreaterThan in seen and GreaterThanOrEqual in seen:
            msg = (
                "Cannot combine 'GreaterThan' and 'GreaterThanOrEqual'"
                " on the same field. "
                "Use one exclusive lower bound or one inclusive lower bound, not both."
            )
            raise MetadataConflictError(msg)
        if LessThan in seen and LessThanOrEqual in seen:
            msg = (
                "Cannot combine 'LessThan' and 'LessThanOrEqual'"
                " on the same field. "
                "Use one exclusive upper bound or one inclusive upper bound, not both."
            )
            raise MetadataConflictError(msg)

    @staticmethod
    def _checkNumericRange(
        seen: dict[type[ValidationMetadata], ValidationMetadata],
    ) -> None:
        """
        Validate numeric bounds and reject empty ranges.

        Parameters
        ----------
        seen : dict[type[ValidationMetadata], ValidationMetadata]
            Indexed metadata mapped by validation metadata type.

        Raises
        ------
        MetadataConflictError
            If lower and upper numeric bounds combine to produce an empty
            set of valid values.
        """
        lower_gt = _get(seen, GreaterThan)
        lower_ge = _get(seen, GreaterThanOrEqual)
        upper_lt = _get(seen, LessThan)
        upper_le = _get(seen, LessThanOrEqual)

        lower = lower_gt or lower_ge
        upper = upper_lt or upper_le

        if lower is None or upper is None:
            return

        lower_val = lower.value
        upper_val = upper.value

        both_inclusive = lower_ge is not None and upper_le is not None
        invalid = lower_val > upper_val if both_inclusive else lower_val >= upper_val

        if invalid:
            msg = (
                f"Impossible numeric range: {type(lower).__name__}({lower_val})"
                f" combined with {type(upper).__name__}({upper_val})"
                " produces an empty set of valid values."
            )
            raise MetadataConflictError(msg)

    @staticmethod
    def _checkLengthRange(
        seen: dict[type[ValidationMetadata], ValidationMetadata],
    ) -> None:
        """
        Reject length constraints where the minimum exceeds the maximum.

        Parameters
        ----------
        seen : dict[type[ValidationMetadata], ValidationMetadata]
            Indexed metadata mapped by validation metadata type.

        Raises
        ------
        MetadataConflictError
            If the minimum length exceeds the maximum length.
        """
        min_meta = _get(seen, MinLength)
        max_meta = _get(seen, MaxLength)

        if (
            min_meta is not None
            and max_meta is not None
            and min_meta.value > max_meta.value
        ):
            msg = (
                f"Impossible length range: MinLength({min_meta.value})"
                f" is greater than MaxLength({max_meta.value}). "
                "The minimum length must not exceed the maximum."
            )
            raise MetadataConflictError(msg)

    @staticmethod
    def _checkTimezone(
        seen: dict[type[ValidationMetadata], ValidationMetadata],
    ) -> None:
        """
        Reject the coexistence of mutually exclusive timezone constraints.

        Parameters
        ----------
        seen : dict[type[ValidationMetadata], ValidationMetadata]
            Indexed metadata mapped by validation metadata type.

        Raises
        ------
        MetadataConflictError
            If both 'TimezoneAware' and 'TimezoneNaive' constraints are present.
        """
        if TimezoneAware in seen and TimezoneNaive in seen:
            msg = (
                "Cannot combine 'TimezoneAware' and 'TimezoneNaive'"
                " on the same field. "
                "A datetime field cannot simultaneously require and"
                " forbid timezone information."
            )
            raise MetadataConflictError(msg)

    @staticmethod
    def _checkValues(
        seen: dict[type[ValidationMetadata], ValidationMetadata],
    ) -> None:
        """
        Validate individual metadata values for semantic correctness.

        Checks applied:

        * ``MultipleOf.value`` must be strictly positive (> 0).
        * ``MinLength.value`` must be non-negative (>= 0).
        * ``MaxLength.value`` must be non-negative (>= 0).

        Parameters
        ----------
        seen : dict[type[ValidationMetadata], ValidationMetadata]
            The indexed metadata mapping produced by ``_index``.

        Raises
        ------
        MetadataConflictError
            If any constraint carries an invalid value.
        """
        mul = _get(seen, MultipleOf)
        if mul is not None and mul.value <= 0:
            msg = (
                f"Invalid 'MultipleOf' value: {mul.value!r}."
                " The divisor must be strictly positive (> 0)."
            )
            raise MetadataConflictError(msg)

        min_len = _get(seen, MinLength)
        if min_len is not None and min_len.value < 0:
            msg = (
                f"Invalid 'MinLength' value: {min_len.value!r}."
                " The minimum length must be non-negative (>= 0)."
            )
            raise MetadataConflictError(msg)

        max_len = _get(seen, MaxLength)
        if max_len is not None and max_len.value < 0:
            msg = (
                f"Invalid 'MaxLength' value: {max_len.value!r}."
                " The maximum length must be non-negative (>= 0)."
            )
            raise MetadataConflictError(msg)

    @staticmethod
    def _build(
        seen: dict[type[ValidationMetadata], ValidationMetadata],
    ) -> msgspec.Meta:
        """
        Construct the field constraint descriptor from the validated metadata index.

        Built in a single pass over *seen* to avoid allocating intermediate
        dictionaries.  All fourteen ``msgspec.Meta`` parameters are populated
        here in one go, each guarded by an O(1) dict look-up via ``_get``.

        Parameters
        ----------
        seen : dict[type[ValidationMetadata], ValidationMetadata]
            The conflict-free metadata index produced by ``_index``.

        Returns
        -------
        msgspec.Meta
            The fully configured field constraint descriptor.
        """
        kwargs: dict[str, object] = {}

        # numeric -------------------------------------------------------
        if (gt := _get(seen, GreaterThan)) is not None:
            kwargs["gt"] = gt.value
        if (ge := _get(seen, GreaterThanOrEqual)) is not None:
            kwargs["ge"] = ge.value
        if (lt := _get(seen, LessThan)) is not None:
            kwargs["lt"] = lt.value
        if (le := _get(seen, LessThanOrEqual)) is not None:
            kwargs["le"] = le.value
        if (mul := _get(seen, MultipleOf)) is not None:
            kwargs["multiple_of"] = mul.value

        # string / collection -------------------------------------------
        if (pat := _get(seen, Pattern)) is not None:
            kwargs["pattern"] = pat.regex
        if (min_len := _get(seen, MinLength)) is not None:
            kwargs["min_length"] = min_len.value
        if (max_len := _get(seen, MaxLength)) is not None:
            kwargs["max_length"] = max_len.value

        # timezone ------------------------------------------------------
        if TimezoneAware in seen:
            kwargs["tz"] = True
        elif TimezoneNaive in seen:
            kwargs["tz"] = False

        # documentation -------------------------------------------------
        if (title := _get(seen, Title)) is not None:
            kwargs["title"] = title.value
        if (desc := _get(seen, Description)) is not None:
            kwargs["description"] = desc.value
        if (examples := _get(seen, Examples)) is not None:
            kwargs["examples"] = list(examples.values)
        if (extra_json := _get(seen, ExtraJsonSchema)) is not None:
            kwargs["extra_json_schema"] = dict(extra_json.data)
        if (extra := _get(seen, Extra)) is not None:
            kwargs["extra"] = dict(extra.data)

        return msgspec.Meta(**kwargs)

__all__: list[str] = [
    "MetaCompiler",
    "MetadataConflictError",
]
