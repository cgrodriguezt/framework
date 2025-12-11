from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.console.contracts.schedule_event_listener import IScheduleEventListener
    from orionis.console.enums.listener import ListeningEvent
    from orionis.console.contracts.event import IEvent

class ISchedule(ABC):

    @abstractmethod
    def registerListener(
        self,
        event: str | ListeningEvent,
        listener: IScheduleEventListener | callable,
    ) -> None:
        """
        Register a listener for a scheduler event or job.

        Register a callback or an instance of IScheduleEventListener for a global
        scheduler event or a specific job ID. The listener will be invoked when
        the event occurs.

        Parameters
        ----------
        event : str or ListeningEvent
            Event name or job ID to listen for. Can be a string or a ListeningEvent
            instance.
        listener : IScheduleEventListener or callable
            Listener to register. Must be callable or an instance of
            IScheduleEventListener.

        Returns
        -------
        None
            This method always returns None. No value is returned.

        Raises
        ------
        TypeError
            If the event name is not a non-empty string.
        ValueError
            If the event is not a valid ListeningEvent or job ID string.
        TypeError
            If the listener is not callable or not an instance of
            IScheduleEventListener.
        """

    @abstractmethod
    def command(
        self,
        signature: str,
        args: list[str] | None = None,
    ) -> IEvent:
        """
        Register an Event instance for a command signature and arguments.

        Validate the command signature and arguments, ensuring the command exists
        and arguments are in the correct format. If valid, create and register an
        Event object representing the scheduled command, storing it internally.

        Parameters
        ----------
        signature : str
            Unique signature identifying the command to schedule. Must be non-empty.
        args : list of str or None, optional
            List of string arguments for the command. Defaults to None.

        Returns
        -------
        IEvent
            The registered Event instance for further scheduling configuration.

        Raises
        ------
        RuntimeError
            If attempting to add a command while the scheduler is running.
        TypeError
            If the signature is not a non-empty string, or if arguments are not a
            list of strings.
        ValueError
            If the command signature is not registered.
        """

    @abstractmethod
    async def start(self) -> None:
        """
        Start the AsyncIO scheduler and keep it running.

        Initialize and start the AsyncIOScheduler, ensuring all scheduled events are
        loaded and listeners are subscribed. The scheduler runs within an asyncio
        context until a stop signal is received. Handles graceful shutdowns and
        interruptions.

        Returns
        -------
        None
            This method does not return any value. The scheduler runs until stopped.

        Raises
        ------
        RuntimeError
            If the scheduler fails to start due to missing an asyncio event loop or
            other runtime issues.
        """

    @abstractmethod
    def pause(self) -> None:
        """
        Pause all user jobs managed by the scheduler.

        Pause all currently scheduled user jobs in the AsyncIOScheduler if the
        scheduler is running. Iterate through all jobs, attempt to pause each one,
        and trigger listeners for the pause event. After all jobs are paused,
        trigger a global listener for the scheduler pause event. Clear the set of
        paused jobs before pausing to ensure only currently paused jobs are tracked.

        Returns
        -------
        None
            This method does not return any value. It pauses all user jobs and
            triggers the appropriate listeners and logging.
        """

    @abstractmethod
    def resume(self) -> None:
        """
        Resume all user jobs previously paused by the scheduler.

        Resume jobs only if the scheduler is currently paused. After resuming,
        trigger the global listener for the scheduler resume event and log the
        action. For jobs that missed execution while paused, trigger the missed
        event listener. The method does not return any value.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    async def shutdown(self, *, wait: bool = True) -> None:
        """
        Shut down the AsyncIO scheduler asynchronously.

        Gracefully stop the AsyncIOScheduler and signal the main event loop to
        terminate waiting. Ensures clean shutdown of both main and control schedulers.

        Parameters
        ----------
        wait : bool, optional
            If True, wait for currently executing jobs to finish. Default is True.

        Returns
        -------
        None
            Always returns None.
        """

    @abstractmethod
    def pauseCommand(self, signature: str) -> bool:
        """
        Pause a scheduled job in the AsyncIO scheduler.

        Validate the signature and attempt to pause the job. Log the action and
        invoke the paused job listener if successful. Return True if paused,
        otherwise return False.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to pause.

        Returns
        -------
        bool
            True if the job was successfully paused, False otherwise.
        """

    @abstractmethod
    def resumeCommand(self, signature: str) -> bool:
        """
        Resume a paused job in the AsyncIO scheduler.

        Validate the job signature and attempt to resume the job if it exists
        and is paused. Log the action and invoke the resumed job listener.
        Return True if the job was resumed, otherwise return False.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to resume.

        Returns
        -------
        bool
            True if the job was resumed, False otherwise.
        """

    @abstractmethod
    def removeCommand(self, signature: str) -> bool:
        """
        Remove a scheduled job from the scheduler by its signature.

        Validate the signature and attempt to remove the job from both the scheduler
        and the internal jobs list. Log the removal and return True if successful.
        Return False if the job does not exist or an error occurs.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to remove.

        Returns
        -------
        bool
            True if the job was removed, False otherwise.
        """

    @abstractmethod
    def listScheduledJobs(self) -> list[dict]:
        """
        Retrieve all scheduled jobs managed by the scheduler.

        Ensure all scheduled events are loaded into the internal jobs list. Iterate
        through each job and collect its details in a dictionary format. Each dictionary
        contains the command signature, arguments, purpose, random delay, start and end
        dates, and additional job details.

        Returns
        -------
        list of dict
            List of dictionaries, each representing a scheduled job with keys:
            'signature', 'args', 'purpose', 'random_delay', 'start_date', 'end_date',
            'details', 'coalesce', 'max_instances', 'misfire_grace_time'. Returns an
            empty list if no jobs are scheduled.
        """

    @abstractmethod
    def getScheduledJobDetails(self, signature: str) -> dict | None:
        """
        Retrieve job details by signature.

        Search the internal jobs list for a job matching the provided signature.
        Ensure all events are loaded before searching. Return a dictionary with
        job details if found, otherwise return None.

        Parameters
        ----------
        signature : str
            Unique signature (ID) of the job to retrieve.

        Returns
        -------
        dict or None
            Dictionary with job details if found, otherwise None.

        Notes
        -----
        Returns None if no job matches the signature.
        """

    @abstractmethod
    def isRunning(self) -> bool:
        """
        Check if the scheduler is running.

        Inspect the internal state of the AsyncIOScheduler to determine if it is active.
        The scheduler is running if it has been started and is not paused or shut down.

        Returns
        -------
        bool
            True if the scheduler is running and its state is STATE_RUNNING.
            False otherwise.
        """

    @abstractmethod
    def isPaused(self) -> bool:
        """
        Check if the scheduler is paused.

        Determine if the scheduler is currently in a paused state by inspecting its
        running status and internal state.

        Returns
        -------
        bool
            True if the scheduler is running and its state is paused, otherwise False.
        """

    @abstractmethod
    def forceStop(self) -> None:
        """
        Force stop the scheduler immediately without waiting for jobs to finish.

        This method shuts down the AsyncIOScheduler and control scheduler instantly,
        bypassing any graceful shutdown procedures. It also sets the internal stop
        event to interrupt the scheduler's main loop.

        Returns
        -------
        None
            Always returns None. The scheduler is stopped and the stop event is set.

        Notes
        -----
        Use with caution. Running jobs may be interrupted.
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Signal the scheduler to stop synchronously by setting the internal stop event.

        Set the internal asyncio stop event to request a graceful shutdown of the
        scheduler from a synchronous context. If an asyncio event loop is running,
        set the stop event in a thread-safe manner using `call_soon_threadsafe`.
        If no event loop is running, set the stop event directly.

        Returns
        -------
        None
            Always returns None. Signals the scheduler to stop by setting the internal
            stop event.

        Notes
        -----
        If the stop event is already set or does not exist, this method does nothing.
        Any exceptions encountered while setting the stop event are logged as warnings,
        but the method will still attempt to set the event directly.
        """
