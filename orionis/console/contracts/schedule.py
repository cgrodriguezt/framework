from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from orionis.console.contracts.event import IEvent
    from orionis.console.contracts.schedule_event_listener import IScheduleEventListener
    from orionis.console.enums.listener import ListeningEvent

class ISchedule(ABC):

    @abstractmethod
    def command(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> IEvent:
        """
        Prepare an Event for a command signature and arguments.

        Validates the command signature and arguments. If valid, creates and returns
        an Event object representing the scheduled command.

        Parameters
        ----------
        signature : str
            Unique identifier for the command.
        args : Optional[List[str]], optional
            Arguments for the command.

        Returns
        -------
        IEvent
            Event instance with command details.

        Raises
        ------
        ValueError
            If signature is invalid or arguments are not a list of strings.
        """

    @abstractmethod
    def setListener(
        self,
        event: str | ListeningEvent,
        listener: IScheduleEventListener | callable,
    ) -> None:
        """
        Register a listener for a scheduler event.

        Associates a listener with a scheduler event or job ID.

        Parameters
        ----------
        event : str or ListeningEvent
            Event name or job ID.
        listener : IScheduleEventListener or callable
            Listener to invoke on event.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If event or listener is invalid.
        """

    @abstractmethod
    def pause(
        self,
        at: datetime,
    ) -> None:
        """
        Schedule a pause for all operations at a specific datetime.

        Adds a job to pause the scheduler at the given time.

        Parameters
        ----------
        at : datetime
            Datetime to pause the scheduler.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If 'at' is not a valid datetime.
        """

    @abstractmethod
    def resume(
        self,
        at: datetime,
    ) -> None:
        """
        Schedule a resume for all operations at a specific datetime.

        Adds a job to resume the scheduler at the given time.

        Parameters
        ----------
        at : datetime
            Datetime to resume the scheduler.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If 'at' is not a valid datetime.
        """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the AsyncIO scheduler and keep it running.

        Initiates the scheduler within an asyncio context.

        Returns
        -------
        None
        """

    @abstractmethod
    async def shutdown(self, *, wait: bool = True) -> None:
        """
        Shut down the AsyncIO scheduler asynchronously.

        Stops the scheduler and optionally waits for jobs to finish.

        Parameters
        ----------
        wait : bool, optional
            Wait for jobs to finish before shutdown.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If 'wait' is not a boolean.
        CLIOrionisRuntimeError
            If shutdown fails.
        """

    @abstractmethod
    def pauseCommand(self, signature: str) -> bool:
        """
        Pause a scheduled job by its signature.

        Attempts to pause the job identified by signature.

        Parameters
        ----------
        signature : str
            Job signature to pause.

        Returns
        -------
        bool
            True if paused, False otherwise.

        Raises
        ------
        CLIOrionisValueError
            If signature is invalid.
        """

    @abstractmethod
    def resumeCommand(self, signature: str) -> bool:
        """
        Resume a paused job by its signature.

        Attempts to resume the job identified by signature.

        Parameters
        ----------
        signature : str
            Job signature to resume.

        Returns
        -------
        bool
            True if resumed, False otherwise.

        Raises
        ------
        CLIOrionisValueError
            If signature is invalid.
        """

    @abstractmethod
    def removeCommand(self, signature: str) -> bool:
        """
        Remove a scheduled job by its signature.

        Attempts to remove the job identified by signature.

        Parameters
        ----------
        signature : str
            Job signature to remove.

        Returns
        -------
        bool
            True if removed, False otherwise.

        Raises
        ------
        CLIOrionisValueError
            If signature is invalid.
        """

    @abstractmethod
    def events(self) -> list:
        """
        Retrieve all scheduled jobs managed by the scheduler.

        Loads and returns a list of job dictionaries.

        Returns
        -------
        list of dict
            List of job details.
        """

    @abstractmethod
    def isRunning(self) -> bool:
        """
        Determine if the scheduler is currently running.

        Checks if the scheduler is active.

        Returns
        -------
        bool
            True if running, False otherwise.
        """

    @abstractmethod
    def isPaused(self) -> bool:
        """
        Check if the scheduler is currently paused.

        Determines if any jobs are paused.

        Returns
        -------
        bool
            True if paused, False otherwise.
        """

    @abstractmethod
    def forceStop(self) -> None:
        """
        Force stop the scheduler immediately.

        Shuts down the scheduler without waiting for jobs.

        Returns
        -------
        None
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the scheduler synchronously.

        Signals the scheduler to stop.

        Returns
        -------
        None
        """
