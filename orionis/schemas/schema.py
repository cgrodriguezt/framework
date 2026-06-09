from __future__ import annotations
from typing import TYPE_CHECKING, Annotated, get_args, get_origin
import msgspec
from orionis.schemas.compiler import MetaCompiler
from orionis.schemas.meta.validation import ValidationMetadata
from orionis.schemas.metadata import (
    Message,
)
from orionis.schemas.constraints import (
    GreaterThan, GreaterThanOrEqual,
    LessThan, LessThanOrEqual,
    MinLength, MaxLength,
    MultipleOf, Pattern,
    TimezoneAware, TimezoneNaive,
)

if TYPE_CHECKING:
    from collections.abc import Callable

# Maps each ConstraintMetadata type to the msgspec.Meta kwarg name it compiles to.
# Used to build __orionis_constraints__ (field → {msgspec_key → custom_message}).
_CONSTRAINT_MSGSPEC_KEYS: dict[type, str] = {
    MinLength: "min_length",
    MaxLength: "max_length",
    Pattern: "pattern",
    GreaterThan: "gt",
    GreaterThanOrEqual: "ge",
    LessThan: "lt",
    LessThanOrEqual: "le",
    MultipleOf: "multiple_of",
    TimezoneAware: "tz_aware",
    TimezoneNaive: "tz_naive",
}

_StructMeta = type(msgspec.Struct)

class SchemaMeta(_StructMeta):
    """
    Compile Orionis field metadata into msgspec constraints.

    Intercept ``Annotated`` hints on every ``Schema`` subclass at class
    creation time and transparently convert ``ValidationMetadata`` instances
    into a ``msgspec.Meta`` descriptor recognized by msgspec.

    Collect non-``ValidationMetadata`` items kept inside ``Annotated`` into
    ``__orionis_meta__`` on the class after creation, allowing other Orionis
    subsystems to consume them without coupling to msgspec internals.

    Rely on the Python 3.14 lazy-annotation protocol
    (``__annotate_func__``, PEP 649). Earlier Python versions are not
    supported.
    """

    # ruff: noqa: C901

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
        **kwargs: object,
    ) -> SchemaMeta:
        """
        Build a new ``Schema`` subclass with compiled metadata.

        Wrap ``__annotate_func__`` (PEP 649) so ``ValidationMetadata`` objects
        become ``msgspec.Meta`` instances, then attach ``__orionis_meta__``
        and ``__orionis_constraints__`` to the finished class.

        Parameters
        ----------
        cls : type
            Provide the metaclass itself.
        name : str
            Define the class name.
        bases : tuple[type, ...]
            Define the direct base classes.
        namespace : dict[str, object]
            Provide the class body namespace.
        **kwargs : object
            Forward metaclass keyword arguments to ``msgspec.Struct``.

        Returns
        -------
        SchemaMeta
            Return the created schema class.
        """
        annotate_func: Callable[[int], dict[str, object]] | None = (
            namespace.get("__annotate_func__")  # type: ignore[assignment]
        )
        # Mutable dict populated lazily when __annotate_func__ is first called
        # (during super().__new__).  A reference is stored on the class so
        # later accesses always see the fully-populated mapping.
        constraint_msgs: dict[str, dict[str, str]] = {}
        if annotate_func is not None:
            namespace["__annotate_func__"] = SchemaMeta._wrap(
                annotate_func, constraint_msgs,
            )

        klass: SchemaMeta = super().__new__(cls, name, bases, namespace, **kwargs)
        # After the Struct is built, collect any remaining custom metadata
        # (items that are not msgspec.Meta) from every annotated field.
        klass.__orionis_meta__ = SchemaMeta._collect(klass)
        # Mapping: field_name -> {msgspec_constraint_key -> custom_message}.
        # Only entries where message != None are stored.
        klass.__orionis_constraints__ = constraint_msgs
        # Eagerly populate the validation plan cache at class-definition time.
        # This moves _build_plan() cost to import/class-creation (acceptable once)
        # and guarantees that Schema.validate() always hits the cache — the
        # "if plan is None" branch on the hot path becomes unreachable.
        # Deferred import avoids a module-level circular dependency.
        from orionis.schemas.rules_executor import _build_plan  # noqa: PLC0415
        _build_plan(klass)
        return klass

    @staticmethod
    def _wrap( # NOSONAR
        original_func: Callable[[int], dict[str, object]],
        constraint_msgs: dict[str, dict[str, str]],
    ) -> Callable[[int], dict[str, object]]:
        """
        Return a wrapped annotate callable for the Python 3.14 lazy protocol.

        Call the original annotate function to obtain raw annotations, compile
        ``ValidationMetadata`` items into ``msgspec.Meta``, and extract custom
        error messages into ``constraint_msgs``.

        Capture module-level globals as closure locals so the inner
        ``_annotate`` uses ``LOAD_DEREF`` rather than ``LOAD_GLOBAL``.

        Parameters
        ----------
        original_func : Callable[[int], dict[str, object]]
            Provide the original PEP 649 annotation callback.
        constraint_msgs : dict[str, dict[str, str]]
            Store per-field custom error messages keyed by constraint name.

        Returns
        -------
        Callable[[int], dict[str, object]]
            Return the wrapped annotation callback.
        """
        _meta_compiler = MetaCompiler
        _validation_metadata = ValidationMetadata
        _message_type = Message
        _constraint_keys = _CONSTRAINT_MSGSPEC_KEYS
        _get_origin = get_origin
        _get_args = get_args
        _annotated_type = Annotated

        def _annotate(fmt: int) -> dict[str, object]:
            annotations: dict[str, object] = original_func(fmt)
            result: dict[str, object] = {}
            for k, v in annotations.items():
                if _get_origin(v) is not _annotated_type:
                    result[k] = v
                    continue

                args = _get_args(v)
                base_type: object = args[0]
                metadata: tuple[object, ...] = args[1:]

                # Single-pass classification: avoids iterating `metadata`.
                type_msg: Message | None = None
                validation_meta: list[ValidationMetadata] = []
                custom_meta: list[object] = []
                for m in metadata:
                    if isinstance(m, _message_type):
                        if type_msg is None:
                            type_msg = m
                    elif isinstance(m, _validation_metadata):
                        validation_meta.append(m)
                    else:
                        custom_meta.append(m)

                # Collect custom messages keyed by their msgspec constraint name.
                # Direct slot read (m.message) instead of getattr(m, "message", None):
                # all ConstraintMetadata subclasses declare the slot, so the 3-arg
                # getattr fallback machinery is never needed.
                msgs: dict[str, str] = {
                    key: m.message  # type: ignore[union-attr]
                    for m in validation_meta
                    if (key := _constraint_keys.get(type(m))) is not None
                    and m.message is not None  # direct slot read; no getattr overhead
                }
                # Register the Message text under the reserved "type" key.
                if type_msg is not None:
                    msgs["type"] = type_msg.text
                if msgs:
                    constraint_msgs[k] = msgs

                if not validation_meta:
                    result[k] = v
                    continue

                compiled: msgspec.Meta = _meta_compiler.compile(validation_meta)
                result[k] = Annotated[(base_type, compiled, *custom_meta)]

            return result
        return _annotate

    @staticmethod
    def _compile(annotation: object) -> object:
        """
        Rewrite one ``Annotated`` hint with compiled msgspec metadata.

        Extract ``ValidationMetadata`` instances and compile them into a single
        ``msgspec.Meta`` via ``MetaCompiler``. Keep non-validation metadata
        inside ``Annotated`` so it remains inspectable and can be harvested by
        ``_collect``.

        Parameters
        ----------
        annotation :
            The raw ``Annotated`` type hint from the class body.

        Returns
        -------
        object
            Return the rewritten ``Annotated`` hint, or the original
            annotation when no ``ValidationMetadata`` is present.
        """
        args = get_args(annotation)
        base_type: object = args[0]
        metadata: tuple[object, ...] = args[1:]

        validation_meta: list[ValidationMetadata] = [
            m for m in metadata if isinstance(m, ValidationMetadata)
        ]
        custom_meta: list[object] = [
            m for m in metadata if not isinstance(m, ValidationMetadata)
        ]

        if not validation_meta:
            return annotation

        compiled: msgspec.Meta = MetaCompiler.compile(validation_meta)
        # custom_meta survives inside Annotated; msgspec ignores non-Meta items,
        # but they remain accessible for Orionis-specific processing.
        return Annotated[(base_type, compiled, *custom_meta)]

    @staticmethod
    def _collect(klass: type) -> dict[str, list[object]]:
        """
        Collect custom non-msgspec metadata from a freshly created struct.

        Iterate over each field of ``klass`` and collect ``Annotated``
        arguments that are not ``msgspec.Meta`` instances into a
        ``field_name -> [custom_items]`` mapping.

        Parameters
        ----------
        klass :
            The newly created ``Schema`` subclass.

        Returns
        -------
        dict[str, list[object]]
            A mapping of field names to their custom metadata objects.
            Fields with no custom metadata are omitted.
        """
        result: dict[str, list[object]] = {}
        _msgspec_meta = msgspec.Meta # pre-bind: avoids attribute lookup per item
        _get_origin = get_origin # pre-bind: avoids global lookup per field
        _get_args = get_args # pre-bind: avoids global lookup per field
        for field in msgspec.structs.fields(klass):
            if _get_origin(field.type) is Annotated:
                custom: list[object] = [
                    item
                    for item in _get_args(field.type)[1:]
                    if not isinstance(item, _msgspec_meta)
                ]
                if custom:
                    result[field.name] = custom
        return result

class Schema(msgspec.Struct, metaclass=SchemaMeta):
    """
    Define the base class for Orionis schema declarations.

    Notes
    -----
    Inherit ``msgspec.Struct`` behavior and the ``SchemaMeta`` metaclass
    pipeline, which compiles validation metadata and stores Orionis custom
    metadata on the resulting class.
    """

__all__: list[str] = ["Schema", "SchemaMeta"]
