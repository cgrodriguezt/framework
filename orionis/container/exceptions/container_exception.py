class OrionisContainerException(Exception):
    """
    Excepción personalizada para errores relacionados con el contenedor de inyección de dependencias Orionis.
    """

    def __init__(self, message: str) -> None:
        """
        Inicializa la excepción con un mensaje de error.

        Args:
            message (str): Mensaje descriptivo del error.
        """
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna una representación en cadena de la excepción."""
        return f"[OrionisContainerException] {self.args[0]}"