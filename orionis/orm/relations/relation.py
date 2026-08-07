from __future__ import annotations
from typing import TYPE_CHECKING, Any, ClassVar
from orionis.orm.contracts.relation import IRelation
from orionis.orm.query.builder import ModelQueryBuilder

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from orionis.orm.model import Model
    from orionis.support.types.collection import Collection

class Relation[TRelated: "Model"](ModelQueryBuilder[TRelated], IRelation):
    """
    Base class for every query builder bound to a parent model instance.

    A relationship is a regular :class:`ModelQueryBuilder` targeting the
    related model, pre-constrained to the rows belonging to a specific
    parent instance. Concrete kinds (``hasOne``, ``hasMany``,
    ``belongsTo``, ``belongsToMany``, and future polymorphic or
    through-relations) only need to implement the template methods
    below; the full fluent query API is inherited for free.
    """

    __slots__ = ("_parent",)

    # Suspended by `noConstraints` while eager loading builds a
    # "template" instance purely to read its metadata (related model,
    # foreign key, ...) without binding the query to one specific parent.
    _constraints: ClassVar[bool] = True

    def __init__(self, parent: Model, related: type[TRelated]) -> None:
        """
        Bind a relationship query builder to its parent instance.

        Parameters
        ----------
        parent : Model
            Model instance the relationship is accessed from.
        related : type of Model
            Model class the relationship targets.

        Returns
        -------
        None
            This method does not return a value.
        """
        super().__init__(related)
        self._parent = parent
        if Relation._constraints:
            self.addConstraints()

    # ── Template methods (overridden per relationship kind) ─────────────────

    def addConstraints(self) -> None:
        """
        Constrain the query to the bound parent instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        error_msg = f"{type(self).__name__} must implement addConstraints()."
        raise NotImplementedError(error_msg)

    def addEagerConstraints(self, models: list[Model]) -> None:
        """
        Constrain the query to every parent instance of an eager batch.

        Parameters
        ----------
        models : list of Model
            Parent instances being eager loaded together.

        Returns
        -------
        None
            This method does not return a value.
        """
        error_msg = f"{type(self).__name__} must implement addEagerConstraints()."
        raise NotImplementedError(error_msg)

    async def getResults(self) -> Any:  # noqa: ANN401
        """
        Execute the relationship query for its bound parent instance.

        Returns
        -------
        Any
            A single model, ``None``, or a ``Collection``, depending on
            the relationship kind.
        """
        error_msg = f"{type(self).__name__} must implement getResults()."
        raise NotImplementedError(error_msg)

    async def getEager(self) -> Collection:
        """
        Execute the relationship query assembled for eager loading.

        The default implementation reuses the regular ``get()``
        terminal, since most relationships project every matching row
        the same way whether they are lazy or eager loaded.

        Returns
        -------
        Collection
            Every related row across the whole eager-loaded batch.
        """
        return await self.get()

    def match(
        self,
        models: list[Model],
        results: Collection,
        name: str,
    ) -> None:
        """
        Group eager-loaded results and attach them to their parents.

        Parameters
        ----------
        models : list of Model
            Parent instances being eager loaded together.
        results : Collection
            Rows produced by :meth:`getEager`.
        name : str
            Relationship name the results are stored under.

        Returns
        -------
        None
            This method does not return a value.
        """
        error_msg = f"{type(self).__name__} must implement match()."
        raise NotImplementedError(error_msg)

    # ── Ergonomics ────────────────────────────────────────────────────────

    def __await__(self) -> Generator[Any, None, Any]:
        """
        Allow ``await`` directly on a relationship without a terminal.

        Equivalent to ``await relation.getResults()``, mirroring how
        Eloquent resolves ``$model->relation`` as a property access.

        Returns
        -------
        Generator
            Delegate generator driving :meth:`getResults`.
        """
        return self.getResults().__await__()

    @classmethod
    def noConstraints(
        cls,
        callback: Callable[[], Relation[Any]],
    ) -> Relation[Any]:
        """
        Build a relationship instance without its single-parent constraint.

        Used by eager loading to read a relationship's metadata (related
        model, foreign key, ...) from a sample instance without binding
        the query to that specific instance. Safe under concurrent
        ``asyncio`` tasks: the callback never awaits, so no other task
        can observe the flag while it is temporarily disabled.

        Parameters
        ----------
        callback : Callable
            Zero-argument callable constructing the relationship,
            typically a bound relationship method such as
            ``model.posts``.

        Returns
        -------
        Relation
            The relationship built by ``callback``, unconstrained.
        """
        previous = Relation._constraints
        Relation._constraints = False
        try:
            return callback()
        finally:
            Relation._constraints = previous
