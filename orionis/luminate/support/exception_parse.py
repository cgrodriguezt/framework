import traceback
from orionis.luminate.contracts.support.exception_parse import IExceptionParse

class ExceptionParse(IExceptionParse):
    """
    A utility class to parse an exception and convert it into a structured dictionary.
    """

    @staticmethod
    def toDict(exception):
        """
        Parse the provided exception and serialize it into a dictionary format.

        Parameters
        ----------
        exception : Exception
            The exception object to be serialized.

        Returns
        -------
        dict
            A dictionary containing the exception details such as error type, message,
            and the stack trace.

        Notes
        -----
        - Uses `traceback.TracebackException.from_exception()` to extract detailed traceback information.
        - The stack trace includes filenames, line numbers, function names, and the exact line of code.
        """
        # Extract the detailed traceback information from the exception
        tb = traceback.TracebackException.from_exception(exception)

        # Construct and return the dictionary containing all necessary exception details
        return {
            "error_type": tb.exc_type_str,
            "error_message": str(tb).strip(),
            "error_code": getattr(exception, "code", None),
            "stack_trace": [
                {
                    "filename": frame.filename,
                    "lineno": frame.lineno,
                    "name": frame.name,
                    "line": frame.line
                }
                for frame in tb.stack
            ]
        }
