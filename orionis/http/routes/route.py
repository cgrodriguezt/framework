class Route:

    def __call__(self) -> None:
        """
        Initialize the Route singleton instance.

        Parameters
        ----------
        *args : tuple
            Positional arguments (unused).
        **kwds : dict
            Keyword arguments (unused).

        Returns
        -------
        None
            This method initializes the routers and routes attributes.
        """
        # Initialize the list of routers and the routes dictionary
        self.__routers: list[Router] = []
        self.__routes: dict = {}

    def __addRoute(
        self,
        method: str,
        path: str,
        action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Add a new route to the routers list.

        Parameters
        ----------
        method : str
            HTTP method for the route.
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance.
        """
        router = Router()
        self.__routers.append(router)
        return router.addRoute(method, path, action)

    def post(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a POST route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('post', path, action)

    def get(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a GET route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('get', path, action)

    def put(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a PUT route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('put', path, action)

    def delete(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a DELETE route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('delete', path, action)

    def patch(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a PATCH route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('patch', path, action)

    def head(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a HEAD route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('head', path, action)

    def options(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register an OPTIONS route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('options', path, action)

    def trace(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a TRACE route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('trace', path, action)

    def copy(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a COPY route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('copy', path, action)

    def link(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a LINK route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('link', path, action)

    def unlink(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register an UNLINK route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('unlink', path, action)

    def purge(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a PURGE route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('purge', path, action)

    def lock(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a LOCK route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('lock', path, action)

    def unlock(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register an UNLOCK route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('unlock', path, action)

    def propfind(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a PROPFIND route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('propfind', path, action)

    def view(
        self,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Register a VIEW route.

        Parameters
        ----------
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        None
            This method registers the route and returns None.
        """
        self.__addRoute('view', path, action)

    def group(self, *routes: FluentRoute) -> Router:
        """
        Group multiple FluentRoute instances into a new Router.

        Parameters
        ----------
        *routes : FluentRoute
            Variable number of FluentRoute instances to group.

        Returns
        -------
        Router
            The Router instance containing the grouped routes.
        """
        router = Router()
        self.__routers.append(router)
        router.group(*routes)
        return router

    def middleware(self, middleware: IMiddleware) -> Router:
        """
        Add middleware to a new Router.

        Parameters
        ----------
        middleware : IMiddleware
            Middleware instance to add.

        Returns
        -------
        Router
            The Router instance with the middleware applied.
        """
        router = Router()
        self.__routers.append(router)
        router.middleware(middleware)
        return router

    def withOutMiddleware(self, middleware: IMiddleware) -> Router:
        """
        Exclude middleware from a new Router.

        Parameters
        ----------
        middleware : IMiddleware
            Middleware instance to exclude.

        Returns
        -------
        Router
            The Router instance with the middleware excluded.
        """
        router = Router()
        self.__routers.append(router)
        router.withOutMiddleware(middleware)
        return router

    def prefix(self, prefix: str) -> Router:
        """
        Set a prefix for all routes in a new Router.

        Parameters
        ----------
        prefix : str
            Prefix to set for the router.

        Returns
        -------
        Router
            The Router instance with the prefix applied.
        """
        router = Router()
        self.__routers.append(router)
        router.prefix(prefix)
        return router

    def loadRoutes(self) -> None:
        """
        Load all routes from the registered routers and organize them in a nested dictionary.

        Populates self.__routes with the structure:
        {
            path: {
                method: route_info_dict,
                ...
            },
            ...
        }
        """
        for router in self.__routers:
            for path, method, info in router._loadRoutes():
                if path not in self.__routes:
                    self.__routes[path] = {}
                self.__routes[path][method] = info

    def getRoutes(self) -> dict:
        """
        Retrieve all registered routes.

        Returns
        -------
        dict
            A dictionary containing all loaded routes, organized by path and method.
        """
        # Load routes if not already loaded
        if not self.__routes:
            self.loadRoutes()
        return self.__routes
