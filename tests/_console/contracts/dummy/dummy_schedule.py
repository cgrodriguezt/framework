from unittest.mock import MagicMock
from orionis.console.contracts.base_scheduler import IBaseScheduler
from orionis.console.contracts.schedule import ISchedule
from orionis.console.entities.scheduler_error import SchedulerError
from orionis.console.entities.scheduler_paused import SchedulerPaused
from orionis.console.entities.scheduler_resumed import SchedulerResumed
from orionis.console.entities.scheduler_shutdown import SchedulerShutdown
from orionis.console.entities.scheduler_started import SchedulerStarted

class DummySchedule(ISchedule):
    """
    Dummy implementation of the ISchedule interface for testing purposes.

    This class provides stub methods for all required scheduling operations,
    returning default values or performing no action. It is intended for use
    in unit tests or as a placeholder where a functional scheduler is not needed.

    Methods
    -------
    command(signature, args=None)
        Simulates execution of a command with the given signature and arguments.
    setListener(event, listener)
        Registers a listener for a specific event (no-op).
    events()
        Returns a list of scheduled events (always empty).
    start()
        Starts the scheduler (no-op).
    stop()
        Stops the scheduler (no-op).
    pauseEverythingAt(time)
        Schedules a pause for all tasks at the specified time (no-op).
    resumeEverythingAt(time)
        Schedules a resume for all tasks at the specified time (no-op).
    shutdownEverythingAt(time)
        Schedules a shutdown for all tasks at the specified time (no-op).
    pauseTask(job_id)
        Pauses a specific task (no-op).
    resumeTask(job_id)
        Resumes a specific task (no-op).
    removeTask(job_id)
        Removes a specific task from the schedule (no-op).
    forceStop(job_id)
        Forcefully stops a specific task (no-op).
    cancelScheduledPause(job_id)
        Cancels a scheduled pause for a specific task (no-op).
    cancelScheduledResume(job_id)
        Cancels a scheduled resume for a specific task (no-op).
    cancelScheduledShutdown(job_id)
        Cancels a scheduled shutdown for a specific task (no-op).
    isRunning()
        Indicates whether the scheduler is running (always False).
    shutdown()
        Shuts down the scheduler (no-op).
    """
    def command(self, signature, args=None):
        return None
    def setListener(self, event, listener):
        pass
    def events(self):
        return []
    def start(self):
        pass
    def stop(self):
        pass
    def pauseEverythingAt(self, time):
        pass
    def resumeEverythingAt(self, time):
        pass
    def shutdownEverythingAt(self, time):
        pass
    def pauseTask(self, job_id):
        pass
    def resumeTask(self, job_id):
        pass
    def removeTask(self, job_id):
        pass
    def forceStop(self, job_id):
        pass
    def cancelScheduledPause(self, job_id):
        pass
    def cancelScheduledResume(self, job_id):
        pass
    def cancelScheduledShutdown(self, job_id):
        pass
    def isRunning(self):
        return False
    def shutdown(self):
        pass

class DummyScheduler(IBaseScheduler):
    """
    Dummy implementation of the IBaseScheduler interface for testing purposes.

    This scheduler provides asynchronous method stubs for handling various scheduler events.
    Each method sets an attribute indicating it was called, useful for verifying event handling
    in unit tests.

    Methods
    -------
    tasks(schedule: ISchedule)
        Called to execute scheduled tasks.

    onStarted(event: SchedulerStarted, schedule: ISchedule)
        Called when the scheduler has started.

    onPaused(event: SchedulerPaused, schedule: ISchedule)
        Called when the scheduler has been paused.

    onResumed(event: SchedulerResumed, schedule: ISchedule)
        Called when the scheduler has resumed from a paused state.

    onFinalized(event: SchedulerShutdown, schedule: ISchedule)
        Called when the scheduler has been finalized or shut down.

    onError(event: SchedulerError, schedule: ISchedule)
        Called when an error occurs in the scheduler.
    """
    async def tasks(self, schedule: ISchedule):
        self.tasks_called = True
    async def onStarted(self, event: SchedulerStarted, schedule: ISchedule):
        self.started_called = (event, schedule)
    async def onPaused(self, event: SchedulerPaused, schedule: ISchedule):
        self.paused_called = (event, schedule)
    async def onResumed(self, event: SchedulerResumed, schedule: ISchedule):
        self.resumed_called = (event, schedule)
    async def onFinalized(self, event: SchedulerShutdown, schedule: ISchedule):
        self.finalized_called = (event, schedule)
    async def onError(self, event: SchedulerError, schedule: ISchedule):
        self.error_called = (event, schedule)

class DummyScheduleTwo(ISchedule):
    """
    Dummy implementation of the ISchedule interface for testing purposes.

    This class provides stub methods for all required scheduling operations,
    allowing for the simulation of scheduler behavior in unit tests or as a placeholder
    where a functional scheduler is not needed.

    Methods
    -------
    command(signature, args=None)
        Simulates execution of a command with the given signature and arguments.

        Parameters
        ----------
        signature : str
            The command signature to execute.
        args : list, optional
            Arguments for the command.

        Returns
        -------
        MagicMock
            A MagicMock object simulating the command execution.

    setListener(event, listener)
        Registers a listener for a specific event.

        Parameters
        ----------
        event : str
            The event to listen for.
        listener : callable
            The listener function to register.

        Returns
        -------
        None

    pauseEverythingAt(at)
        Schedules a pause for all tasks at the specified time.

        Parameters
        ----------
        at : Any
            The time at which to pause all tasks.

        Returns
        -------
        None

    resumeEverythingAt(at)
        Schedules a resume for all tasks at the specified time.

        Parameters
        ----------
        at : Any
            The time at which to resume all tasks.

        Returns
        -------
        None

    shutdownEverythingAt(at)
        Schedules a shutdown for all tasks at the specified time.

        Parameters
        ----------
        at : Any
            The time at which to shut down all tasks.

        Returns
        -------
        None

    start()
        Starts the scheduler.

        Returns
        -------
        None

    shutdown(wait=True)
        Shuts down the scheduler.

        Parameters
        ----------
        wait : bool, optional
            Whether to wait for shutdown to complete (default is True).

        Returns
        -------
        None

    pauseTask(signature)
        Pauses a specific task.

        Parameters
        ----------
        signature : str
            The signature of the task to pause.

        Returns
        -------
        bool
            True if the task was paused.

    resumeTask(signature)
        Resumes a specific task.

        Parameters
        ----------
        signature : str
            The signature of the task to resume.

        Returns
        -------
        bool
            True if the task was resumed.

    removeTask(signature)
        Removes a specific task from the schedule.

        Parameters
        ----------
        signature : str
            The signature of the task to remove.

        Returns
        -------
        bool
            True if the task was removed.

    events()
        Returns a list of scheduled events.

        Returns
        -------
        list of dict
            A list containing event dictionaries.

    cancelScheduledPause()
        Cancels a scheduled pause for all tasks.

        Returns
        -------
        bool
            True if the scheduled pause was canceled.

    cancelScheduledResume()
        Cancels a scheduled resume for all tasks.

        Returns
        -------
        bool
            True if the scheduled resume was canceled.

    cancelScheduledShutdown()
        Cancels a scheduled shutdown for all tasks.

        Returns
        -------
        bool
            True if the scheduled shutdown was canceled.

    isRunning()
        Indicates whether the scheduler is running.

        Returns
        -------
        bool
            True if the scheduler is running.

    forceStop()
        Forcefully stops all tasks.

        Returns
        -------
        None

    stop()
        Stops the scheduler.

        Returns
        -------
        None
    """
    def command(self, signature, args=None):
        # Simulate execution of a command and return a MagicMock object
        return MagicMock(signature=signature, args=args)

    def setListener(self, event, listener):
        # Store the event and listener for verification in tests
        self.listener_set = (event, listener)

    def pauseEverythingAt(self, at):
        # Record the time at which all tasks are paused
        self.paused_at = at

    def resumeEverythingAt(self, at):
        # Record the time at which all tasks are resumed
        self.resumed_at = at

    def shutdownEverythingAt(self, at):
        # Record the time at which all tasks are shut down
        self.shutdown_at = at

    async def start(self):
        # Mark the scheduler as started
        self.started = True

    async def shutdown(self, wait=True):
        # Mark the scheduler as shutdown and record if waiting was requested
        self.shutdown_called = wait

    def pauseTask(self, signature):
        # Record the paused task and return True to indicate success
        self.paused_task = signature
        return True

    def resumeTask(self, signature):
        # Record the resumed task and return True to indicate success
        self.resumed_task = signature
        return True

    def removeTask(self, signature):
        # Record the removed task and return True to indicate success
        self.removed_task = signature
        return True

    def events(self):
        # Return a list with a single dummy event dictionary
        return [
            {
                'signature': 'foo',
                'args': [],
                'purpose': 'test',
                'random_delay': None,
                'start_date': None,
                'end_date': None,
                'details': {}
            }
        ]

    def cancelScheduledPause(self):
        # Mark that a scheduled pause was canceled and return True
        self.cancel_pause = True
        return True

    def cancelScheduledResume(self):
        # Mark that a scheduled resume was canceled and return True
        self.cancel_resume = True
        return True

    def cancelScheduledShutdown(self):
        # Mark that a scheduled shutdown was canceled and return True
        self.cancel_shutdown = True
        return True

    def isRunning(self):
        # Always return True to indicate the scheduler is running
        return True

    def forceStop(self):
        # Mark that a force stop was triggered
        self.forced_stop = True

    def stop(self):
        # Mark that the scheduler was stopped
        self.stopped = True