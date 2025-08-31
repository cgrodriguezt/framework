from orionis.console.contracts.cli_request import ICLIRequest

class DummyRequest(ICLIRequest):

    def all(self):
        """
        Retrieve all input data as a dictionary.

        This method returns a dictionary containing all the input data associated with the request.
        In this dummy implementation, it always returns a dictionary with a single key-value pair.

        Returns
        -------
        dict
            A dictionary with a single entry: {"foo": "bar"}.
        """
        # Return a dummy dictionary with a fixed key-value pair
        return {"foo": "bar"}

    def argument(self, name):
        """
        Retrieve the value of a specific argument by its name.

        This dummy implementation always returns None, regardless of the argument name provided.

        Parameters
        ----------
        name : str
            The name of the argument to retrieve.

        Returns
        -------
        None
            Always returns None in this dummy implementation.
        """
        # Always return None for any argument name
        return None

    def command(self):
        """
        Get the name of the command associated with this request.

        This dummy implementation always returns the string "dummy_command".

        Returns
        -------
        str
            The name of the dummy command, always "dummy_command".
        """
        # Return the name of the dummy command
        return "dummy_command"
