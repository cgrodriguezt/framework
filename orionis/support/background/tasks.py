from __future__ import annotations
from typing import Any, Callable, Sequence
from orionis.support.background.task import BackgroundTask


class BackgroundTasks(BackgroundTask):
    """
    Manage and execute a collection of background tasks sequentially.

    This class holds an ordered list of :class:`BackgroundTask` instances
    and runs them one after another when invoked.
    """

    def __init__(self, tasks: Sequence[BackgroundTask] | None = None) -> None:
        """
        Initialize BackgroundTasks with an optional sequence of tasks.

        Parameters
        ----------
        tasks : Sequence[BackgroundTask] | None
            Optional sequence of BackgroundTask instances to initialize with.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Convert tasks to a list or initialize as empty if not provided
        self.tasks = list(tasks) if tasks else []

    def addTask(
        self, func: Callable, *args: Any, **kwargs: Any
    ) -> None:
        """
        Add a new BackgroundTask to the task list.

        Parameters
        ----------
        func : Callable
            The function to be executed as a background task.
        *args
            Positional arguments to pass to the function.
        **kwargs
            Keyword arguments to pass to the function.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Create and append a new BackgroundTask instance
        self.tasks.append(BackgroundTask(func, *args, **kwargs))

    async def __call__(self) -> None:
        """
        Execute all background tasks sequentially.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Await each task in the list
        for task in self.tasks:
            await task()

    async def run(self) -> None:
        """
        Run all background tasks by invoking the instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Call the instance to execute all tasks
        await self()