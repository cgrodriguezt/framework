from dataclasses import dataclass
from typing import List

@dataclass(frozen=False, kw_only=True)
class ClassMethod:
    """
    Represents the methods of a class instance.

    Attributes
    ----------
    public : List[str]
        List of public method names.
    private : List[str]
        List of private method names.
    protected : List[str]
        List of protected method names.
    static : List[str]
        List of static method names.
    asynchronous : List[str]
        List of asynchronous method names.
    synchronous : List[str]
        List of synchronous method names.
    class_methods : List[str]
        List of class method names.
    asynchronous_static : List[str]
        List of asynchronous static method names.
    synchronous_static : List[str]
        List of synchronous static method names.
    magic : List[str]
        List of magic method names.
    """
    public: List[str]
    private: List[str]
    protected: List[str]
    static: List[str]
    asynchronous: List[str]
    synchronous: List[str]
    class_methods: List[str]
    asynchronous_static: List[str]
    synchronous_static: List[str]
    magic: List[str]