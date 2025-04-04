import abc
from typing import Any, Type, TypeVar
from orionis.luminate.support.inspection.functions import (
    ensure_abstract_class,
    ensure_instantiable_class,
    ensure_user_defined_class_instance,
    ensure_valid_class_name,
    ensure_valid_module,
)
from orionis.luminate.support.inspection.reflexion_abstract import ReflexionAbstract
from orionis.luminate.support.inspection.reflexion_concrete import ReflexionConcrete
from orionis.luminate.support.inspection.reflexion_concrete_with_abstract import ReflexionConcreteWithAbstract
from orionis.luminate.support.inspection.reflexion_instance import ReflexionInstance
from orionis.luminate.support.inspection.reflexion_instance_with_abstract import ReflexionInstanceWithAbstract
from orionis.luminate.support.inspection.reflexion_module import ReflexionModule
from orionis.luminate.support.inspection.reflexion_module_with_classname import ReflexionModuleWithClassName

T = TypeVar('T')
ABC = TypeVar('ABC', bound=abc.ABC)

class Reflection:
    """A static class providing factory methods for creating reflection objects.

    This class provides methods to create various types of reflection objects
    that encapsulate different aspects of Python's reflection capabilities.
    Each method validates its inputs before creating the appropriate reflection object.

    Methods
    -------
    instance(instance: Any) -> ReflexionInstance
        Creates a reflection object for a class instance
    instanceWithAbstract(instance: Any, abstract: Type[ABC]) -> ReflexionInstanceWithAbstract
        Creates a reflection object for a class instance with its abstract parent
    abstract(abstract: Type[ABC]) -> ReflexionAbstract
        Creates a reflection object for an abstract class
    concrete(concrete: Type[T]) -> ReflexionConcrete
        Creates a reflection object for a concrete class
    concreteWithAbstract(concrete: Type[T], abstract: Type[ABC]) -> ReflexionConcreteWithAbstract
        Creates a reflection object for a concrete class with its abstract parent
    module(module: str) -> ReflexionModule
        Creates a reflection object for a module
    moduleWithClassName(module: str, class_name: str) -> ReflexionModuleWithClassName
        Creates a reflection object for a module with a specific class name
    """

    @staticmethod
    def instance(instance: Any) -> 'ReflexionInstance':
        """Create a reflection object for a class instance.

        Parameters
        ----------
        instance : Any
            The instance to reflect upon

        Returns
        -------
        ReflexionInstance
            A reflection object encapsulating the instance

        Raises
        ------
        TypeError
            If the input is not an object instance
        ValueError
            If the instance is from builtins, abc, or __main__
        """
        ensure_user_defined_class_instance(instance)
        return ReflexionInstance(instance)

    @staticmethod
    def instanceWithAbstract(instance: Any, abstract: Type[ABC]) -> 'ReflexionInstanceWithAbstract':
        """Create a reflection object for a class instance with its abstract parent.

        Parameters
        ----------
        instance : Any
            The instance to reflect upon
        abstract : Type[ABC]
            The abstract parent class

        Returns
        -------
        ReflexionInstanceWithAbstract
            A reflection object encapsulating the instance and its abstract parent

        Raises
        ------
        TypeError
            If the instance is not an object or abstract is not a class
        ValueError
            If the instance is invalid or abstract is not actually abstract
        """
        ensure_user_defined_class_instance(instance)
        ensure_abstract_class(abstract)
        return ReflexionInstanceWithAbstract(instance, abstract)

    @staticmethod
    def abstract(abstract: Type[ABC]) -> 'ReflexionAbstract':
        """Create a reflection object for an abstract class.

        Parameters
        ----------
        abstract : Type[ABC]
            The abstract class to reflect upon

        Returns
        -------
        ReflexionAbstract
            A reflection object encapsulating the abstract class

        Raises
        ------
        TypeError
            If the input is not a class
        ValueError
            If the class is not abstract
        """
        ensure_abstract_class(abstract)
        return ReflexionAbstract(abstract)

    @staticmethod
    def concrete(concrete: Type[T]) -> 'ReflexionConcrete':
        """Create a reflection object for a concrete class.

        Parameters
        ----------
        concrete : Type[T]
            The concrete class to reflect upon

        Returns
        -------
        ReflexionConcrete
            A reflection object encapsulating the concrete class

        Raises
        ------
        TypeError
            If the input is not a class
        ValueError
            If the class is abstract or cannot be instantiated
        """
        ensure_instantiable_class(concrete)
        return ReflexionConcrete(concrete)

    @staticmethod
    def concreteWithAbstract(concrete: Type[T], abstract: Type[ABC]) -> 'ReflexionConcreteWithAbstract':
        """Create a reflection object for a concrete class with its abstract parent.

        Parameters
        ----------
        concrete : Type[T]
            The concrete class to reflect upon
        abstract : Type[ABC]
            The abstract parent class

        Returns
        -------
        ReflexionConcreteWithAbstract
            A reflection object encapsulating the concrete class and its abstract parent

        Raises
        ------
        TypeError
            If either input is not a class
        ValueError
            If concrete is not instantiable or abstract is not actually abstract
        """
        ensure_instantiable_class(concrete)
        ensure_abstract_class(abstract)
        return ReflexionConcreteWithAbstract(concrete, abstract)

    @staticmethod
    def module(module: str) -> 'ReflexionModule':
        """Create a reflection object for a module.

        Parameters
        ----------
        module : str
            The module name to reflect upon

        Returns
        -------
        ReflexionModule
            A reflection object encapsulating the module

        Raises
        ------
        TypeError
            If the input is not a string
        ValueError
            If the module cannot be imported
        """
        ensure_valid_module(module)
        return ReflexionModule(module)

    @staticmethod
    def moduleWithClassName(module: str, class_name: str) -> 'ReflexionModuleWithClassName':
        """Create a reflection object for a module with a specific class name.

        Parameters
        ----------
        module : str
            The module name to reflect upon
        class_name : str
            The class name to look for in the module

        Returns
        -------
        ReflexionModuleWithClassName
            A reflection object encapsulating the module and class name

        Raises
        ------
        TypeError
            If either input is not a string
        ValueError
            If the module cannot be imported or the class doesn't exist in it
        """
        ensure_valid_module(module)
        ensure_valid_class_name(module, class_name)
        return ReflexionModuleWithClassName(module, class_name)



















    # def __inidt__(self,
    #     instance: Any = None, # Instancia ya creada de una clase
    #     concrete: Callable[..., Any] = None, # Clase concreta a instanciar
    #     abstract: Callable[..., Any] = None,    # Clase abstracta a implementar en clases hijas
    #     module: str = None, # Módulo donde se encuentra la clase
    #     class_name: str = None # Nombre de la clase
    # ):

    #     # Garantizar que al menos un argumento sea proporcionado
    #     if not any([abstract, concrete, module, class_name]):
    #         raise ValueError("At least one argument must be provided.")


    #     # Validar que 'abstract' y 'concrete' sean callables
    #     if abstract and not callable(abstract):
    #         raise TypeError("The 'abstract' argument must be callable.")
    #     if concrete and not callable(concrete):
    #         raise TypeError("The 'concrete' argument must be callable.")

    #     # Validar que si se proporciona una clase, también se proporcione el módulo
    #     if class_name and not module:
    #         raise ValueError("If a class name is provided, a module name must also be provided.")

    #     # Validar que el módulo exista e importarlo
    #     if module:
    #         try:
    #             self._module = importlib.import_module(module)
    #         except ModuleNotFoundError:
    #             raise ValueError(f"Module '{module}' not found.")

    #     # Validar que la clase exista en el módulo
    #     if module and class_name:
    #         if not hasattr(self._module, class_name):
    #             raise ValueError(f"Class '{class_name}' not found in module '{module}'.")

    #     # Validar que la clase no sea abstracta antes de instanciarla
    #     if concrete and inspect.isabstract(concrete):
    #         raise TypeError(f"Cannot instantiate abstract class '{concrete.__name__}'.")


    # def safeImport(self):
    #     """
    #     Safely imports the specified module and assigns the class object if a classname is provided.

    #     This method raises a ValueError if the module cannot be imported or if the class does not exist
    #     within the module.

    #     Raises
    #     ------
    #     ValueError
    #         If the module cannot be imported or the class does not exist in the module.
    #     """
    #     try:
    #         module = importlib.import_module(self.module_name)
    #         if self.classname:
    #             self.cls = getattr(module, self.classname, None)
    #             if self.cls is None:
    #                 raise ValueError(f"Class '{self.classname}' not found in module '{self.module_name}'.")
    #     except ImportError as e:
    #         raise ValueError(f"Error importing module '{self.module_name}': {e}")






























    # def getFile(self) -> str:
    #     """
    #     Retrieves the file path where the class is defined.

    #     Returns
    #     -------
    #     str
    #         The file path if the class is found, otherwise raises an error.

    #     Raises
    #     ------
    #     ValueError
    #         If the class has not been loaded yet.
    #     """
    #     if not self.cls:
    #         raise ValueError("Class not loaded. Use 'safeImport()' first.")
    #     return inspect.getfile(self.cls)

    # def hasClass(self) -> bool:
    #     """
    #     Checks whether the class object is available.

    #     Returns
    #     -------
    #     bool
    #         True if the class is loaded, False otherwise.
    #     """
    #     return self.cls is not None

    # def hasMethod(self, method_name: str) -> bool:
    #     """
    #     Checks whether the specified method exists in the class.

    #     Parameters
    #     ----------
    #     method_name : str
    #         The name of the method to check.

    #     Returns
    #     -------
    #     bool
    #         True if the method exists, False otherwise.
    #     """
    #     return hasattr(self.cls, method_name) if self.cls else False

    # def hasProperty(self, prop: str) -> bool:
    #     """
    #     Checks whether the specified property exists in the class.

    #     Parameters
    #     ----------
    #     prop : str
    #         The name of the property to check.

    #     Returns
    #     -------
    #     bool
    #         True if the property exists, False otherwise.
    #     """
    #     return hasattr(self.cls, prop) if self.cls else False

    # def hasConstant(self, constant: str) -> bool:
    #     """
    #     Checks whether the specified constant exists in the class.

    #     Parameters
    #     ----------
    #     constant : str
    #         The name of the constant to check.

    #     Returns
    #     -------
    #     bool
    #         True if the constant exists, False otherwise.
    #     """
    #     return hasattr(self.cls, constant) if self.cls else False

    # def getAttributes(self) -> List[str]:
    #     """
    #     Retrieves a list of all attributes (including methods and properties) of the class.

    #     Returns
    #     -------
    #     list
    #         A list of attribute names in the class.
    #     """
    #     return dir(self.cls) if self.cls else []

    # def getConstructor(self):
    #     """
    #     Retrieves the constructor (__init__) of the class.

    #     Returns
    #     -------
    #     function or None
    #         The constructor method if available, otherwise None.
    #     """
    #     return self.cls.__init__ if self.cls else None

    # def getDocComment(self) -> Optional[str]:
    #     """
    #     Retrieves the docstring of the class.

    #     Returns
    #     -------
    #     str or None
    #         The docstring of the class if available, otherwise None.
    #     """
    #     if not self.cls:
    #         raise ValueError("Class not loaded. Use 'safeImport()' first.")
    #     return self.cls.__doc__

    # def getFileName(self, remove_extension: bool = False) -> str:
    #     """
    #     Retrieves the file name where the class is defined, the same as `get_file()`.

    #     Parameters
    #     ----------
    #     remove_extension : bool, optional
    #         If True, the file extension will be removed from the filename. Default is False.

    #     Returns
    #     -------
    #     str
    #         The file name of the class definition.
    #     """
    #     file_name = os.path.basename(self.getFile())
    #     if remove_extension:
    #         file_name = os.path.splitext(file_name)[0]
    #     return file_name

    # def getMethod(self, method_name: str):
    #     """
    #     Retrieves the specified method from the class.

    #     Parameters
    #     ----------
    #     method_name : str
    #         The name of the method to retrieve.

    #     Returns
    #     -------
    #     function or None
    #         The method if it exists, otherwise None.
    #     """
    #     return getattr(self.cls, method_name, None) if self.cls else None

    # def getMethods(self) -> List[str]:
    #     """
    #     Retrieves a list of all methods in the class.

    #     Returns
    #     -------
    #     list
    #         A list of method names in the class.
    #     """
    #     return [method for method, _ in inspect.getmembers(self.cls, predicate=inspect.isfunction)] if self.cls else []

    # def getName(self) -> str:
    #     """
    #     Retrieves the name of the class.

    #     Returns
    #     -------
    #     str or None
    #         The name of the class if available, otherwise None.
    #     """
    #     return self.cls.__name__ if self.cls else None

    # def getParentClass(self) -> Optional[tuple]:
    #     """
    #     Retrieves the parent classes (base classes) of the class.

    #     Returns
    #     -------
    #     tuple or None
    #         A tuple of base classes if available, otherwise None.
    #     """
    #     return self.cls.__bases__ if self.cls else None

    # def getProperties(self) -> List[str]:
    #     """
    #     Retrieves a list of all properties of the class.

    #     Returns
    #     -------
    #     list
    #         A list of property names in the class.
    #     """
    #     return [name for name, value in inspect.getmembers(self.cls, lambda x: isinstance(x, property))] if self.cls else []

    # def getProperty(self, prop: str):
    #     """
    #     Retrieves the specified property from the class.

    #     Parameters
    #     ----------
    #     prop : str
    #         The name of the property to retrieve.

    #     Returns
    #     -------
    #     property or None
    #         The property if it exists, otherwise None.
    #     """
    #     return getattr(self.cls, prop, None) if self.cls else None

    # def isAbstract(self) -> bool:
    #     """
    #     Checks whether the class is abstract.

    #     Returns
    #     -------
    #     bool
    #         True if the class is abstract, False otherwise.
    #     """
    #     return hasattr(self.cls, '__abstractmethods__') and bool(self.cls.__abstractmethods__) if self.cls else False

    # def isEnum(self) -> bool:
    #     """
    #     Checks whether the class is an enumeration.

    #     Returns
    #     -------
    #     bool
    #         True if the class is a subclass of Enum, False otherwise.
    #     """
    #     return self.cls is not None and isinstance(self.cls, type) and issubclass(self.cls, Enum)

    # def isSubclassOf(self, parent: type) -> bool:
    #     """
    #     Checks whether the class is a subclass of the specified parent class.

    #     Parameters
    #     ----------
    #     parent : type
    #         The parent class to check against.

    #     Returns
    #     -------
    #     bool
    #         True if the class is a subclass of the parent, False otherwise.
    #     """
    #     return self.cls is not None and issubclass(self.cls, parent)

    # def isInstanceOf(self, instance: Any) -> bool:
    #     """
    #     Checks whether the class is an instance of the specified class.

    #     Parameters
    #     ----------
    #     parent : type
    #         The class to check against.

    #     Returns
    #     -------
    #     bool
    #         True if the class is a subclass of the parent, False otherwise.
    #     """
    #     return self.cls is not None and isinstance(instance, self.cls)

    # def isIterable(self) -> bool:
    #     """
    #     Checks whether the class is iterable.

    #     Returns
    #     -------
    #     bool
    #         True if the class is iterable, False otherwise.
    #     """
    #     return hasattr(self.cls, '__iter__') if self.cls else False

    # def isInstantiable(self) -> bool:
    #     """
    #     Checks whether the class can be instantiated.

    #     Returns
    #     -------
    #     bool
    #         True if the class is callable and not abstract, False otherwise.
    #     """
    #     return self.cls is not None and callable(self.cls) and not self.isAbstract()

    # def newInstance(self, *args, **kwargs):
    #     """
    #     Creates a new instance of the class if it is instantiable.

    #     Parameters
    #     ----------
    #     args : tuple
    #         Arguments to pass to the class constructor.
    #     kwargs : dict
    #         Keyword arguments to pass to the class constructor.

    #     Returns
    #     -------
    #     object
    #         A new instance of the class.

    #     Raises
    #     ------
    #     TypeError
    #         If the class is not instantiable.
    #     """
    #     if self.isInstantiable():
    #         return self.cls(*args, **kwargs)
    #     raise TypeError(f"Cannot instantiate class '{self.classname}'. It may be abstract or not callable.")

    # def __str__(self) -> str:
    #     """
    #     Returns a string representation of the Reflection instance.

    #     Returns
    #     -------
    #     str
    #         A string describing the class and module.
    #     """
    #     status = "loaded" if self.cls else "not loaded"
    #     return f"<Orionis Reflection class '{self.classname}' in module '{self.module_name}' ({status})>"