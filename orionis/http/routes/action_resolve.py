import importlib
from orionis.foundation.contracts.application import IApplication
from orionis.http.enums.route_types import RouteTypes
from typing import Callable, Awaitable, Any

class RouteAction:

    def __init__(
        self,
        app: IApplication,
    ) -> None:
        """
        Initialize RouteAction with the application context.

        Parameters
        ----------
        app : IApplication
            The application instance used for dependency resolution.

        Returns
        -------
        None
            This method does not return any value.
        """
        self.__app: IApplication = app

    def resolve(
        self,
        action_type: RouteTypes | str,
        action_metadata: dict[str, str],
    ) -> Callable[..., Awaitable[Any]]:
        """
        Resolve and return an async handler for the specified route action.

        Parameters
        ----------
        action_type : RouteTypes or str
            The type of route action to resolve.
        action_metadata : dict[str, str]
            Metadata describing the action, such as module, class, and method.

        Returns
        -------
        Callable[..., Awaitable[Any]]
            An asynchronous callable that can be used as a route handler.

        Raises
        ------
        ValueError
            If the route type is invalid.
        """
        # Convert string action_type to RouteTypes enum if necessary
        if isinstance(action_type, str):
            try:
                action_type = RouteTypes(action_type)
            except ValueError:
                error_msg = f"Invalid route type: {action_type}"
                raise ValueError(error_msg)

        if action_type == RouteTypes.CONTROLLER_METHOD:
            module_name: str | None = action_metadata.get("module")
            class_name: str | None = action_metadata.get("class")
            method_name: str | None = action_metadata.get("method")

            module = importlib.import_module(module_name)
            controller_class = getattr(module, class_name)

            async def handler(*args, **kwargs) -> object:
                """
                Invoke the controller method asynchronously.

                Parameters
                ----------
                *args : tuple
                    Positional arguments for the method.
                **kwargs : dict
                    Keyword arguments for the method.

                Returns
                -------
                object
                    The result of the controller method invocation.
                """
                controller_instance = await self.__app.build(controller_class)
                return await self.__app.call(
                    controller_instance,
                    method_name,
                    *args,
                    **kwargs
                )

            return handler

        elif action_type == RouteTypes.CONTROLLER_CALL:
            module_name: str | None = action_metadata.get("module")
            class_name: str | None = action_metadata.get("class")

            module = importlib.import_module(module_name)
            controller_class = getattr(module, class_name)

            async def handler(*args, **kwargs) -> object:
                """
                Invoke the controller instance asynchronously.

                Parameters
                ----------
                *args : tuple
                    Positional arguments for the callable.
                **kwargs : dict
                    Keyword arguments for the callable.

                Returns
                -------
                object
                    The result of the controller invocation.
                """
                # The instance itself is the callable.
                controller_instance = await self.__app.build(controller_class)
                return await self.__app.invoke(
                    controller_instance,
                    *args,
                    **kwargs
                )

            return handler

        elif action_type == RouteTypes.FUNCTION:
            module_name: str | None = action_metadata.get("module")
            function_name: str | None = action_metadata.get("callable")

            module = importlib.import_module(module_name)
            function = getattr(module, function_name)

            async def handler(*args, **kwargs) -> object:
                """
                Invoke the function asynchronously.

                Parameters
                ----------
                *args : tuple
                    Positional arguments for the function.
                **kwargs : dict
                    Keyword arguments for the function.

                Returns
                -------
                object
                    The result of the function invocation.
                """
                return await self.__app.invoke(
                    function,
                    *args,
                    **kwargs
                )

            return handler