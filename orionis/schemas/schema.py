from __future__ import annotations
from typing import TYPE_CHECKING, Annotated, get_args, get_origin
import msgspec
from orionis.schemas.compiler import MetaCompiler
from orionis.schemas.metadata import (
    ValidationMetadata,
    GreaterThan, GreaterThanOrEqual,
    LessThan, LessThanOrEqual,
    Message,
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
    Metaclass that compiles Orionis field metadata into msgspec constraints.

    Intercepts ``Annotated`` hints on every ``Schema`` subclass at class-creation
    time and transparently converts ``ValidationMetadata`` instances into a
    ``msgspec.Meta`` descriptor recognised by msgspec.

    Non-``ValidationMetadata`` items kept inside ``Annotated`` are collected
    into ``__orionis_meta__`` on the class after creation, so that other Orionis
    subsystems (sanitisers, transformers, custom validators, …) can access them
    without coupling to msgspec internals.

    Relies on the Python 3.14 lazy-annotation protocol (``__annotate_func__``,
    PEP 649).  Earlier Python versions are not supported.
    """

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
        **kwargs: object,
    ) -> SchemaMeta:
        """
        Build a new ``Schema`` subclass with compiled metadata.

        Wraps ``__annotate_func__`` (PEP 649) so that ``ValidationMetadata``
        objects become ``msgspec.Meta`` instances, then attaches
        ``__orionis_meta__`` to the finished class.
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
        return klass

    @staticmethod
    def _wrap( # NOSONAR
        original_func: Callable[[int], dict[str, object]],
        constraint_msgs: dict[str, dict[str, str]],
    ) -> Callable[[int], dict[str, object]]:
        """
        Return a wrapped annotate callable for the Python 3.14 lazy protocol.

        The wrapper calls the original function to obtain the raw annotations,
        then compiles ``ValidationMetadata`` items into ``msgspec.Meta`` while
        also extracting any custom error messages into ``constraint_msgs``.

        Module-level globals are captured as closure-locals so the inner
        ``_annotate`` uses ``LOAD_DEREF`` instead of the slower ``LOAD_GLOBAL``
        on every call.
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

                # Extract Message separately — it carries a type-level custom
                # error text and must not be forwarded to MetaCompiler.
                type_msg: Message | None = next(
                    (m for m in metadata if isinstance(m, _message_type)), None,
                )

                validation_meta: list[ValidationMetadata] = [
                    m for m in metadata
                    if isinstance(m, _validation_metadata)
                    and not isinstance(m, _message_type)
                ]
                custom_meta: list[object] = [
                    m for m in metadata if not isinstance(m, _validation_metadata)
                ]

                # Collect custom messages keyed by their msgspec constraint name.
                msgs: dict[str, str] = {
                    key: m.message  # type: ignore[union-attr]
                    for m in validation_meta
                    if (key := _constraint_keys.get(type(m))) is not None
                    and getattr(m, "message", None) is not None
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
        Rewrite one ``Annotated`` hint, compiling only msgspec-compatible metadata.

        ``ValidationMetadata`` instances are extracted and compiled into a
        single ``msgspec.Meta`` via ``MetaCompiler``.  Any other items
        (custom Orionis metadata) are kept inside ``Annotated`` so they
        remain inspectable through ``get_args`` and are later harvested by
        ``_collect``.  msgspec silently ignores non-``msgspec.Meta`` items.

        Parameters
        ----------
        annotation :
            The raw ``Annotated`` type hint from the class body.

        Returns
        -------
        object
            The rewritten ``Annotated`` hint, or the original annotation when
            no ``ValidationMetadata`` is present.
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
        Harvest custom (non-msgspec) metadata from a freshly created Struct.

        Iterates over every field of *klass* and collects any ``Annotated``
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
    Subclasses inherit ``msgspec.Struct`` behavior and the ``SchemaMeta``
    metaclass pipeline that compiles validation metadata and stores Orionis
    custom metadata on the resulting class.
    """

__all__: list[str] = ["Schema", "SchemaMeta"]
