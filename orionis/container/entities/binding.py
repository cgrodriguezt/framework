from dataclasses import dataclass, field
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions import OrionisContainerTypeError
from orionis.support.entities.base import BaseEntity

@dataclass(unsafe_hash=True, kw_only=True)
class Binding(BaseEntity):

    contract: type = field(
        default=None,
        metadata={
            "description": "Contrato de la clase concreta a inyectar.",
            "default": None
        }
    )

    concrete: type = field(
        default=None,
        metadata={
            "description": "Clase concreta que implementa el contrato.",
            "default": None
        }
    )

    instance: object = field(
        default=None,
        metadata={
            "description": "Instancia concreta de la clase, si se proporciona.",
            "default": None
        }
    )

    function: callable = field(
        default=None,
        metadata={
            "description": "Función que se invoca para crear la instancia.",
            "default": None
        }
    )

    lifetime: Lifetime = field(
        default=Lifetime.TRANSIENT,
        metadata={
            "description": "Tiempo de vida de la instancia.",
            "default": Lifetime.TRANSIENT
        }
    )

    enforce_decoupling: bool = field(
        default=False,
        metadata={
            "description": "Indica si se debe forzar el desacoplamiento entre contrato y concreta.",
            "default": False
        }
    )

    alias: str = field(
        default=None,
        metadata={
            "description": "Alias para resolver la dependencia desde el contenedor.",
            "default": None
        }
    )

    def __post_init__(self):
        """
        Performs type validation of instance attributes after initialization.

        Parameters
        ----------
        None

        Raises
        ------
        OrionisContainerTypeError
            If 'lifetime' is not an instance of `Lifetime` (when not None).
        OrionisContainerTypeError
            If 'enforce_decoupling' is not of type `bool`.
        OrionisContainerTypeError
            If 'alias' is not of type `str` or `None`.
        """
        if self.lifetime and not isinstance(self.lifetime, Lifetime):
            raise OrionisContainerTypeError(
                f"The 'lifetime' attribute must be an instance of 'Lifetime', but received type '{type(self.lifetime).__name__}'."
            )

        if not isinstance(self.enforce_decoupling, bool):
            raise OrionisContainerTypeError(
                f"The 'enforce_decoupling' attribute must be of type 'bool', but received type '{type(self.enforce_decoupling).__name__}'."
            )

        if self.alias and not isinstance(self.alias, str):
            raise OrionisContainerTypeError(
                f"The 'alias' attribute must be of type 'str' or 'None', but received type '{type(self.alias).__name__}'."
            )