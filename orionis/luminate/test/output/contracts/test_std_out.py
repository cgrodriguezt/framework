from abc import ABC, abstractmethod
class ITestStdOut(ABC):
    """
    Utility for printing debug info during tests, including caller context (file, line, method).
    """

    @abstractmethod
    def dd(self, *args):
        """
        Dumps debugging information using the Debug class.
        This method captures the caller's file, method, and line number,
        and uses the Debug class to output debugging information.
        Args:
            *args: Variable length argument list to be dumped.
        """
        pass

    @abstractmethod
    def dump(self, *args):
        """
        Dumps debugging information using the Debug class.
        This method captures the caller's file, method, and line number,
        and uses the Debug class to output debugging information.
        Args:
            *args: Variable length argument list to be dumped.
        """
        pass