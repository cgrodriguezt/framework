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