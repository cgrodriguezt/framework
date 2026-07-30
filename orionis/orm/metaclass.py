# ruff: noqa: N815 (camelCase attributes are an Orionis convention)
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from orionis.orm.attributes import getCastHandler
from orionis.orm.schema.column import ColumnDefinition
from orionis.orm.schema.table import TableDefinition

if TYPE_CHECKING:
    from collections.abc import Callable

# Pattern splitting CamelCase words for snake_case conversion.
_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")

# Suffixes that pluralize with "es".
_ES_SUFFIXES: tuple[str, ...] = ("s", "x", "z", "ch", "sh")

# English vowels used by the pluralization heuristic.
_VOWELS: frozenset[str] = frozenset("aeiou")

# Wildcard marking every attribute as guarded.
_GUARD_ALL: str = "*"

# Builder entry points forwarded from the model class via the metaclass.
_FORWARDED_BUILDER_METHODS: frozenset[str] = frozenset({
    "avg",
    "count",
    "doesntExist",
    "exists",
    "get",
    "groupBy",
    "having",
    "latest",
    "limit",
    "max",
    "min",
    "offset",
    "oldest",
    "orWhere",
    "orderBy",
    "paginate",
    "select",
    "skip",
    "sum",
    "take",
    "where",
    "whereBetween",
    "whereIn",
    "whereLike",
    "whereNotIn",
    "whereNotNull",
    "whereNull",
})


def snakeCase(name: str) -> str:
    """
    Convert a CamelCase class name into snake_case.

    Leading underscores are ignored so private class names still map
    to clean table names.

    Parameters
    ----------
    name : str
        Class name to convert.

    Returns
    -------
    str
        snake_case version of the name.
    """
    return _CAMEL_BOUNDARY.sub("_", name.lstrip("_")).lower()


def pluralize(word: str) -> str:
    """
    Pluralize an English word using conventional heuristics.

    Parameters
    ----------
    word : str
        Singular word to pluralize.

    Returns
    -------
    str
        Pluralized word.
    """
    # Consonant + y becomes "ies" (category -> categories).
    if word.endswith("y") and len(word) > 1 and word[-2] not in _VOWELS:
        return word[:-1] + "ies"
    # Sibilant endings take "es" (box -> boxes).
    if word.endswith(_ES_SUFFIXES):
        return word + "es"
    return word + "s"


@dataclass(slots=True, eq=False)
class ModelMetadata:
    """
    Precomputed metadata describing a model class.

    Built once by the metaclass so hot paths (hydration, persistence)
    never perform reflection at runtime.

    Attributes
    ----------
    tableName : str
        Logical table name of the model.
    table : TableDefinition
        Table definition consumed by the SQL compiler.
    columns : dict of str to ColumnDefinition
        Column definitions keyed by attribute name.
    primaryKey : str
        Name of the primary key column.
    casts : dict of str to str
        Declared cast names keyed by attribute name.
    castLookup : dict of str to Callable
        Precompiled cast handlers keyed by attribute name.
    fillable : frozenset of str
        Attributes allowed for mass assignment.
    guarded : frozenset of str
        Attributes blocked from mass assignment.
    hidden : frozenset of str
        Attributes omitted from serialization.
    timestamps : bool
        Whether the model maintains creation/update timestamps.
    incrementing : bool
        Whether the primary key is auto-incrementing.
    connection : str or None
        Named connection used by the model, or ``None`` for default.
    createdColumn : str or None
        Creation timestamp column, when present.
    updatedColumn : str or None
        Update timestamp column, when present.
    """

    tableName: str  # NOSONAR
    table: TableDefinition
    columns: dict[str, ColumnDefinition] = field(default_factory=dict)
    primaryKey: str = "id"  # NOSONAR
    casts: dict[str, str] = field(default_factory=dict)
    castLookup: dict[str, Callable[[Any], Any]] = field(default_factory=dict)  # NOSONAR
    fillable: frozenset[str] = frozenset()
    guarded: frozenset[str] = frozenset()
    hidden: frozenset[str] = frozenset()
    timestamps: bool = True
    incrementing: bool = True
    connection: str | None = None
    createdColumn: str | None = None  # NOSONAR
    updatedColumn: str | None = None  # NOSONAR

    def isFillable(self, key: str) -> bool:
        """
        Report whether an attribute accepts mass assignment.

        Parameters
        ----------
        key : str
            Attribute name to check.

        Returns
        -------
        bool
            ``True`` when the attribute can be mass assigned.
        """
        # An explicit whitelist takes precedence over the guard list.
        if self.fillable:
            return key in self.fillable
        if self.guarded:
            return _GUARD_ALL not in self.guarded and key not in self.guarded
        return True

    def applyCasts(self, attributes: dict[str, Any]) -> dict[str, Any]:
        """
        Apply the declared casts to a raw attribute mapping in place.

        Parameters
        ----------
        attributes : dict
            Raw attribute values, typically a database row.

        Returns
        -------
        dict
            The same mapping with cast values applied.
        """
        for key, handler in self.castLookup.items():
            value = attributes.get(key)
            if value is not None:
                attributes[key] = handler(value)
        return attributes


class ModelMeta(type):
    """
    Metaclass discovering model columns and building their metadata.

    At class creation time the metaclass collects column definitions
    (including inherited ones), removes them from the class namespace so
    instance attribute access reaches the attribute store, derives the
    table name and primary key, and precompiles cast handlers.
    """

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> type:
        """
        Create the model class and attach its metadata.

        Parameters
        ----------
        name : str
            Name of the class being created.
        bases : tuple of type
            Base classes of the class being created.
        namespace : dict
            Class namespace as declared in the class body.
        **kwargs : Any
            Additional keyword arguments forwarded to ``type``.

        Returns
        -------
        type
            The created model class with ``__meta__`` attached.
        """
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Abstract classes (including the base model) defer their columns
        # to concrete descendants instead of building metadata.
        if not bases or namespace.get("__abstract__", False):
            cls.__pending_columns__ = mcs._collectPending(cls, namespace)
            cls.__meta__ = None
            return cls

        columns = mcs._collectColumns(cls, namespace)
        table_name = mcs._resolveTableName(cls, name, namespace)
        primary_key = mcs._resolvePrimaryKey(cls, namespace, columns)
        casts = mcs._collectCasts(cls)

        # Timestamp columns are tracked only when actually declared.
        created = str(getattr(cls, "CREATED_AT", "created_at"))
        updated = str(getattr(cls, "UPDATED_AT", "updated_at"))
        timestamps = bool(getattr(cls, "timestamps", True))

        cls.__meta__ = ModelMetadata(
            tableName=table_name,
            table=TableDefinition(
                name=table_name,
                columns=columns,
                primary_key=primary_key,
            ),
            columns=columns,
            primaryKey=primary_key,
            casts=casts,
            castLookup={
                key: getCastHandler(cast) for key, cast in casts.items()
            },
            fillable=frozenset(getattr(cls, "fillable", ()) or ()),
            guarded=frozenset(getattr(cls, "guarded", ()) or ()),
            hidden=frozenset(getattr(cls, "hidden", ()) or ()),
            timestamps=timestamps,
            incrementing=bool(getattr(cls, "incrementing", True)),
            connection=getattr(cls, "connection", None),
            createdColumn=created if timestamps and created in columns else None,
            updatedColumn=updated if timestamps and updated in columns else None,
        )
        return cls

    def __getattr__(cls, name: str) -> Any:  # noqa: ANN401
        """
        Forward chainable builder entry points from the model class.

        Enables the Eloquent-style static API, e.g.
        ``User.where(...)`` starts a builder transparently.

        Parameters
        ----------
        name : str
            Attribute name requested on the model class.

        Returns
        -------
        Any
            Bound builder method for whitelisted entry points.

        Raises
        ------
        AttributeError
            If the attribute is not a forwarded builder method.
        """
        if name in _FORWARDED_BUILDER_METHODS:
            meta = cls.__dict__.get("__meta__")
            if meta is not None:
                return getattr(cls.query(), name)
        error_msg = (
            f"type object '{cls.__name__}' has no attribute '{name}'"
        )
        raise AttributeError(error_msg)

    # ── Discovery helpers ───────────────────────────────────────────────────

    @staticmethod
    def _collectPending(
        owner: type,
        namespace: dict[str, Any],
    ) -> dict[str, ColumnDefinition]:
        """
        Collect and detach column declarations from an abstract class.

        Parameters
        ----------
        owner : type
            Abstract class being created.
        namespace : dict
            Class namespace as declared in the class body.

        Returns
        -------
        dict of str to ColumnDefinition
            Columns deferred to concrete descendants.
        """
        pending: dict[str, ColumnDefinition] = {}

        # Inherit deferred columns from abstract ancestors.
        for base in reversed(owner.__mro__[1:]):
            inherited = base.__dict__.get("__pending_columns__")
            if inherited:
                pending.update(inherited)

        # Register own columns and detach them from the class body.
        for key, value in namespace.items():
            if isinstance(value, ColumnDefinition):
                value.name = key
                pending[key] = value
                delattr(owner, key)

        return pending

    @staticmethod
    def _collectColumns(
        owner: type,
        namespace: dict[str, Any],
    ) -> dict[str, ColumnDefinition]:
        """
        Collect column definitions from bases and the class namespace.

        Own declarations are removed from the class so instance access
        is served by the model attribute store.

        Parameters
        ----------
        owner : type
            Class being created.
        namespace : dict
            Class namespace as declared in the class body.

        Returns
        -------
        dict of str to ColumnDefinition
            Column definitions keyed by attribute name.
        """
        columns: dict[str, ColumnDefinition] = {}

        # Inherit columns from parent models in resolution order.
        for base in reversed(owner.__mro__[1:]):
            base_meta = base.__dict__.get("__meta__")
            if base_meta is not None:
                columns.update(base_meta.columns)
                continue
            deferred = base.__dict__.get("__pending_columns__")
            if deferred:
                columns.update(deferred)

        # Register own columns and detach them from the class body.
        for key, value in namespace.items():
            if isinstance(value, ColumnDefinition):
                value.name = key
                columns[key] = value
                delattr(owner, key)

        return columns

    @staticmethod
    def _resolveTableName(
        owner: type,
        name: str,
        namespace: dict[str, Any],
    ) -> str:
        """
        Resolve the table name from the declaration or the class name.

        Parameters
        ----------
        owner : type
            Class being created.
        name : str
            Name of the class being created.
        namespace : dict
            Class namespace as declared in the class body.

        Returns
        -------
        str
            Logical table name.
        """
        declared = namespace.get("table")
        if isinstance(declared, str) and declared.strip():
            return declared.strip()

        # Inherit an explicitly declared table from a parent model.
        inherited = getattr(owner, "table", None)
        if isinstance(inherited, str) and inherited.strip():
            return inherited.strip()

        return pluralize(snakeCase(name))

    @staticmethod
    def _resolvePrimaryKey(
        owner: type,
        namespace: dict[str, Any],
        columns: dict[str, ColumnDefinition],
    ) -> str:
        """
        Resolve the primary key from declarations or column flags.

        Parameters
        ----------
        owner : type
            Class being created.
        namespace : dict
            Class namespace as declared in the class body.
        columns : dict of str to ColumnDefinition
            Collected column definitions.

        Returns
        -------
        str
            Primary key column name.
        """
        declared = namespace.get("primaryKey") or getattr(
            owner, "primaryKey", None,
        )
        if isinstance(declared, str) and declared.strip():
            return declared.strip()

        # Use the first column flagged as primary, defaulting to "id".
        for key, column in columns.items():
            if column.is_primary:
                return key
        return "id"

    @staticmethod
    def _collectCasts(owner: type) -> dict[str, str]:
        """
        Merge cast declarations across the model hierarchy.

        Parameters
        ----------
        owner : type
            Class being created.

        Returns
        -------
        dict of str to str
            Cast names keyed by attribute name.
        """
        casts: dict[str, str] = {}
        for base in reversed(owner.__mro__):
            declared = base.__dict__.get("casts")
            if isinstance(declared, dict):
                casts.update(declared)
        return casts
