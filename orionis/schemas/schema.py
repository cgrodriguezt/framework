from __future__ import annotations
from typing import TYPE_CHECKING, Annotated, get_args, get_origin
import msgspec
from orionis.schemas.compiler import MetaCompiler
from orionis.schemas.metadata import ValidationMetadata

if TYPE_CHECKING:
    from collections.abc import Callable

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
        if annotate_func is not None:
            namespace["__annotate_func__"] = SchemaMeta._wrap(annotate_func)

        klass: SchemaMeta = super().__new__(cls, name, bases, namespace, **kwargs)
        # After the Struct is built, collect any remaining custom metadata
        # (items that are not msgspec.Meta) from every annotated field.
        klass.__orionis_meta__ = SchemaMeta._collect(klass)
        return klass

    @staticmethod
    def _wrap(
        original_func: Callable[[int], dict[str, object]],
    ) -> Callable[[int], dict[str, object]]:
        """
        Return a wrapped annotate callable for the Python 3.14 lazy protocol.

        The wrapper calls the original function to obtain the raw annotations,
        then passes each ``Annotated`` hint through ``_compile`` before
        returning the result to msgspec.

        Module-level globals (``get_origin``, ``Annotated``, ``_compile``) are
        captured as closure-locals so the inner ``_annotate`` uses
        ``LOAD_DEREF`` instead of the slower ``LOAD_GLOBAL`` on every call.
        """
        _compile = SchemaMeta._compile
        _get_origin = get_origin
        _annotated_type = Annotated

        def _annotate(fmt: int) -> dict[str, object]:
            annotations: dict[str, object] = original_func(fmt)
            return {
                k: _compile(v) if _get_origin(v) is _annotated_type else v
                for k, v in annotations.items()
            }
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
    """Base class for all Orionis schema definitions."""

__all__: list[str] = ["Schema", "SchemaMeta"]
