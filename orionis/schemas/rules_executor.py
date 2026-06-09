from __future__ import annotations
from typing import Annotated, Union, get_args, get_origin
import operator
import types
import msgspec.structs
from orionis.schemas.rule import Rule
from orionis.schemas.exceptions.validation import ValidationException
from orionis.schemas.meta.validation import ValidationMetadata

def _type_contains_nested(tp: object) -> bool:
    """
    Check whether a type annotation contains a nested Orionis schema.

    Parameters
    ----------
    tp : object
        Type annotation to inspect. May be a plain type or wrapped in
        ``Union``/``|`` or ``Annotated``.

    Returns
    -------
    bool
        Return ``True`` if ``tp`` itself, or any nested/union member, is a
        schema type defining ``__orionis_meta__``; otherwise return ``False``.
    """
    origin = get_origin(tp)
    if origin is Union or origin is types.UnionType:
        return any(_type_contains_nested(a) for a in get_args(tp))
    if origin is Annotated:
        return _type_contains_nested(get_args(tp)[0])
    return isinstance(tp, type) and "__orionis_meta__" in tp.__dict__

# Module-level plan cache: avoids classmethod dispatch on every execute() call.
_PLAN_CACHE: dict[type, tuple] = {}

# Pre-bound lookup: saves LOAD_GLOBAL + LOAD_ATTR("get") on the inner hot loop.
_cache_get = _PLAN_CACHE.get

def _warm_child_plan(tp: object) -> None:
    """
    Eagerly populate ``_PLAN_CACHE`` for any nested Orionis schema type.

    Called from ``_build_plan`` so that the first real validation call for a
    nested field always hits the cache instead of triggering a cold build.

    Parameters
    ----------
    tp : object
        Field type annotation, potentially a ``Union`` or bare class.
    """
    origin = get_origin(tp)
    if origin is Union or origin is types.UnionType:
        for arg in get_args(tp):
            if (
                isinstance(arg, type)
                and "__orionis_meta__" in arg.__dict__
                and _cache_get(arg) is None
            ):
                _build_plan(arg)
    elif (
        isinstance(tp, type)
        and "__orionis_meta__" in tp.__dict__
        and _cache_get(tp) is None
    ):
        _build_plan(tp)


def _build_plan(klass: type) -> tuple:
    """
    Build and cache a validation plan for a schema type.

    Parameters
    ----------
    klass : type
                Schema class whose ``msgspec`` fields and ``__orionis_meta__``
                metadata are inspected.

    Returns
    -------
        tuple
                Cached plan entries as ``(field_name, field_name_dot, getter,
                validators, is_nested)`` tuples. Each entry stores the field name,
                the precomputed dotted field prefix, an ``operator.attrgetter`` for
                field access, the field's bound validator callables, and whether the
                field contains a nested Orionis schema.

    Raises
    ------
    TypeError
            Raised when field metadata contains an object that is neither a
            ``Rule`` instance nor supported validation metadata.
    """
    orionis_meta: dict[str, list[object]] = getattr(klass, "__orionis_meta__", {})
    plan: list = []
    for f in msgspec.structs.fields(klass):
        field_items = orionis_meta.get(f.name, ())
        rules: list[Rule] = []
        for item in field_items:
            if isinstance(item, Rule):
                rules.append(item)
            elif isinstance(item, ValidationMetadata):
                # Framework metadata (Message, Title, Description, …) may
                # land here when a field has no compiled constraints; skip.
                continue
            else:
                msg = (
                    f"Field '{f.name}' on '{klass.__name__}': "
                    f"'{type(item).__name__}' is not a valid custom rule. "
                    f"Custom rules must subclass "
                    f"'orionis.schemas.rule.Rule'."
                )
                raise TypeError(msg)
        is_nested = _type_contains_nested(f.type)
        if rules or is_nested:
            # Pre-compile attrgetter: C-level accessor, skips Python getattr() dispatch.
            getter = operator.attrgetter(f.name)
            # Pre-bind validate methods: eliminates attribute lookup + bound-method
            # object creation on every validation call.
            validators = tuple(r.validate for r in rules)
            # Pre-compute "field_name." string: eliminates one string alloc per
            # nested-field validation call (was: qualified + ".").
            field_name_dot = f.name + "."
            plan.append((f.name, field_name_dot, getter, validators, is_nested))
            # Eagerly populate the child plan cache so the hot path never
            # triggers a cold _build_plan() call for nested schemas.
            if is_nested:
                _warm_child_plan(f.type)
    result = tuple(plan)
    _PLAN_CACHE[klass] = result
    return result

def _execute_with_plan(plan: tuple, instance: object, prefix: str) -> None:
    """
    Inner validation loop: execute a pre-resolved plan against an instance.

    This function is the true hot path. It is separated from ``_execute`` so
    that callers who already hold the plan (e.g. ``Schema.validate``) can
    skip the redundant cache lookup and ``type()`` call.

    Parameters
    ----------
    plan : tuple
        Non-empty plan produced by ``_build_plan`` for this instance's type.
    instance : object
        Schema instance to validate.
    prefix : str
        Dot-terminated path prefix for nested field names, e.g.
        ``"address."`` so that child fields report ``"address.zip"``.
        Pass ``""`` at the top level.

    Raises
    ------
    ValidationException
        Raised on the first rule failure encountered.
    """
    for field_name, field_name_dot, getter, validators, is_nested in plan:
        # C-level slot access via pre-compiled attrgetter.
        value = getter(instance)
        # Prefix is "" at top level: CPython's str concat short-circuits to
        # return `field_name` unchanged (no allocation). For nested calls
        # the prefix already ends with ".", so no conditional is needed.
        qualified = prefix + field_name
        if is_nested and value is not None:
            child_klass = type(value)
            child_plan = _cache_get(child_klass)
            if child_plan is None:
                child_plan = _build_plan(child_klass)
            if child_plan:
                # Use pre-computed field_name_dot: avoids one string alloc per call.
                _execute_with_plan(child_plan, value, prefix + field_name_dot)
        for validate in validators:
            # Positional call: avoids keyword-argument dict allocation per call.
            failure = validate(qualified, value, instance)
            if failure is not None:
                raise ValidationException(failure)


def _execute(instance: object, _prefix: str = "") -> None:
    """
    Validate an instance recursively using cached field rules.

    Parameters
    ----------
    instance : object
        Schema instance to validate.
    _prefix : str, default ""
        Dot-separated path prefix used to qualify nested field names.

    Returns
    -------
    None
        Return ``None`` when validation succeeds.

    Raises
    ------
    ValidationException
        Raise when a rule validation fails.
    """
    klass = type(instance)
    plan = _cache_get(klass)
    if plan is None:
        plan = _build_plan(klass)
    if plan:
        _execute_with_plan(plan, instance, _prefix)

class RulesExecutor:
    """Execute custom validation rules on schema instances."""

    # Exposed for external inspection; backed by the module-level _PLAN_CACHE.
    _cache = _PLAN_CACHE

    @staticmethod
    def execute(instance: object, *, _prefix: str = "") -> None:
        """
        Validate an instance using its declared metadata rules.

        Parameters
        ----------
        instance : object
            Instance whose fields and rules will be validated.
        _prefix : str
            Internal dot-separated path prefix used when recursing into
            nested schemas (e.g. ``"address"`` so that failures report
            ``"address.code"`` instead of just ``"code"``).
            Callers should not set this parameter directly.

        Returns
        -------
        None
            Return ``None`` when validation succeeds.

        Raises
        ------
        ValidationException
            Raise when one or more validation failures are found.
        """
        _execute(instance, _prefix)
