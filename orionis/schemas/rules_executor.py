from __future__ import annotations
from typing import Annotated, Union, get_args, get_origin
import types
import msgspec.structs
from orionis.schemas.contracts.rule import Rule
from orionis.schemas.exceptions.validation import ValidationException

def _type_contains_nested(tp: object) -> bool:
    """
    Determine whether a type annotation includes a nested Orionis schema.

    Parameters
    ----------
    tp : object
        Type annotation to inspect, including ``Union`` and ``Annotated``
        wrappers.

    Returns
    -------
    bool
        ``True`` when ``tp`` or any wrapped/union member is a type exposing
        ``__orionis_meta__``; otherwise ``False``.
    """
    origin = get_origin(tp)
    if origin is Union or origin is types.UnionType:
        return any(_type_contains_nested(a) for a in get_args(tp))
    if origin is Annotated:
        return _type_contains_nested(get_args(tp)[0])
    return isinstance(tp, type) and hasattr(tp, "__orionis_meta__")

# Module-level plan cache: avoids classmethod dispatch on every execute() call.
# Maps schema type → list of (field_name, rules, is_nested).
_PLAN_CACHE: dict[type, list[tuple[str, tuple[Rule, ...], bool]]] = {}

def _build_plan(klass: type) -> list[tuple[str, tuple[Rule, ...], bool]]:
    """
    Build and cache the validation plan for a schema type.

    Parameters
    ----------
    klass : type
        Schema class whose ``msgspec`` fields and ``__orionis_meta__``
        annotations are inspected.

    Returns
    -------
    list[tuple[str, tuple[Rule, ...], bool]]
        Validation plan entries as ``(field_name, rules, is_nested)`` where
        ``rules`` contains attached :class:`Rule` instances and ``is_nested``
        indicates whether the field type contains a nested Orionis schema.
    """
    orionis_meta: dict[str, list[object]] = getattr(klass, "__orionis_meta__", {})
    plan: list[tuple[str, tuple[Rule, ...], bool]] = []
    for f in msgspec.structs.fields(klass):
        rules: tuple[Rule, ...] = tuple(
            item for item in orionis_meta.get(f.name, ())
            if isinstance(item, Rule)
        )
        is_nested = _type_contains_nested(f.type)
        if rules or is_nested:
            plan.append((f.name, rules, is_nested))
    _PLAN_CACHE[klass] = plan
    return plan

# Module-level execute function: recursive calls resolve via LOAD_GLOBAL
# instead of a class-attribute lookup, and _prefix is positional to avoid
# keyword-only argument overhead in the recursive case.
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
    plan = _PLAN_CACHE.get(klass)
    if plan is None:
        plan = _build_plan(klass)
    for field, rules, is_nested in plan:
        value = getattr(instance, field)
        qualified = f"{_prefix}.{field}" if _prefix else field
        if is_nested and value is not None:
            _execute(value, qualified)
        for rule in rules:
            failure = rule.validate(field=qualified, value=value, instance=instance)
            if failure is not None:
                raise ValidationException(failure)

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
