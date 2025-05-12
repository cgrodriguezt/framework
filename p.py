# Dump de valores simples
from datetime import datetime
from orionis.luminate.console.dumper.dump_die import Debug

# Lista de diccionarios
usuarios = [
    {"id": 1, "nombre": "María", "activo": True},
    {"id": 2, "nombre": "Carlos", "activo": False},
    {"id": 3, "nombre": "Ana", "activo": True}
]
Debug().dump(usuarios)

# Lista de objetos
class Producto:
    def __init__(self, id, nombre, precio):
        self.id = id
        self.nombre = nombre
        self.precio = precio

productos = [
    Producto(1, "Laptop", 1200.50),
    Producto(2, "Mouse", 25.99),
    Producto(3, "Teclado", 45.75)
]
Debug().dump(productos)
