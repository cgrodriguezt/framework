from __future__ import annotations
from dataclasses import dataclass, field
from orionis.container.enums.lifetimes import Lifetime
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Binding(BaseEntity):

    contract: type = field(
        default=None,
        metadata={
            "description": "Contract of the concrete class to inject.",
            "default": None,
        },
    )

    concrete: type = field(
        default=None,
        metadata={
            "description": "Concrete class implementing the contract.",
            "default": None,
        },
    )

    instance: object = field(
        default=None,
        metadata={
            "description": "Concrete instance of the class, if provided.",
            "default": None,
        },
    )

    function: callable = field(
        default=None,
        metadata={
            "description": "Function invoked to create the instance.",
            "default": None,
        },
    )

    lifetime: Lifetime = field(
        default=Lifetime.TRANSIENT,
        metadata={
            "description": "Lifetime of the instance.",
            "default": Lifetime.TRANSIENT,
        },
    )

    enforce_decoupling: bool = field(
        default=False,
        metadata={
            "description": "Enforce decoupling.",
            "default": False,
        },
    )

    alias: str = field(
        default=None,
        metadata={
            "description": "Alias for resolving the dependency from the container.",
            "default": None,
        },
    )

    def __post_init__(self) -> None:
        """
        Validate attribute types after object initialization.

        Ensures that:
        - 'lifetime' is an instance of `Lifetime`.
        - 'enforce_decoupling' is a boolean.
        - 'alias' is a string or None.

        Raises
        ------
        TypeError
            If 'lifetime' is not a `Lifetime` instance.
        TypeError
            If 'enforce_decoupling' is not a `bool`.
        TypeError
            If 'alias' is not a `str` or `None`.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Check if 'lifetime' is an instance of Lifetime
        if self.lifetime and not isinstance(self.lifetime, Lifetime):
            error_msg = (
                "The 'lifetime' attribute must be an instance of 'Lifetime', but "
                f"received type '{type(self.lifetime).__name__}'."
            )
            raise TypeError(error_msg)

        # Check if 'enforce_decoupling' is a boolean
        if not isinstance(self.enforce_decoupling, bool):
            error_msg = (
                "The 'enforce_decoupling' attribute must be of type 'bool', but "
                f"received type '{type(self.enforce_decoupling).__name__}'."
            )
            raise TypeError(error_msg)

        # Check if 'alias' is a string or None
        if self.alias and not isinstance(self.alias, str):
            error_msg = (
                "The 'alias' attribute must be of type 'str' or 'None', but "
                f"received type '{type(self.alias).__name__}'."
            )
            raise TypeError(error_msg)
