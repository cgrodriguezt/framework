from orionis.console.contracts.schedule_event_listener import IScheduleEventListener

class DummyEventJob:
    # Dummy class representing a scheduled event job
    pass

class DummySchedule:
    # Dummy class representing a schedule
    pass

class DummyScheduleEventListener(IScheduleEventListener):
    async def before(self, event, schedule):
        """
        Called before the scheduled event is executed.

        Parameters
        ----------
        event : object
            The event object that is about to be executed.
        schedule : object
            The schedule associated with the event.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is typically used to perform any setup or logging before the scheduled event runs.
        It sets internal flags and stores the event and schedule for later inspection.
        """
        # Mark that the 'before' event was called and store the arguments
        self.before_called = True
        self.before_event = event
        self.before_schedule = schedule

    async def after(self, event, schedule):
        """
        Called after a scheduled event has been executed.

        Parameters
        ----------
        event : object
            The event object that was executed.
        schedule : object
            The schedule associated with the event.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is used to perform any cleanup or logging after the scheduled event completes.
        It sets internal flags and stores the event and schedule for later inspection.
        """
        # Mark that the 'after' event was called and store the arguments
        self.after_called = True
        self.after_event = event
        self.after_schedule = schedule

    async def onFailure(self, event, schedule):
        """
        Handles the failure event for a scheduled task.

        Parameters
        ----------
        event : object
            The event object associated with the failure.
        schedule : object
            The schedule object related to the failed event.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is called when a scheduled event fails. It sets internal flags and stores the event and schedule for further inspection.
        """
        # Mark that the 'onFailure' event was called and store the arguments
        self.failure_called = True
        self.failure_event = event
        self.failure_schedule = schedule

    async def onMissed(self, event, schedule):
        """
        Handles the event when a scheduled task is missed.

        Parameters
        ----------
        event : object
            The event object associated with the missed schedule.
        schedule : object
            The schedule object that was missed.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is called when a scheduled event is missed. It sets internal flags and stores the event and schedule for later reference.
        """
        # Mark that the 'onMissed' event was called and store the arguments
        self.missed_called = True
        self.missed_event = event
        self.missed_schedule = schedule

    async def onMaxInstances(self, event, schedule):
        """
        Handles the event triggered when the maximum number of schedule instances is reached.

        Parameters
        ----------
        event : object
            The event object associated with reaching the maximum instances.
        schedule : object
            The schedule object related to the event.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is called when the maximum number of concurrent schedule instances is reached.
        It sets internal flags and stores the event and schedule for later inspection.
        """
        # Mark that the 'onMaxInstances' event was called and store the arguments
        self.max_instances_called = True
        self.max_instances_event = event
        self.max_instances_schedule = schedule

    async def onPaused(self, event, schedule):
        """
        Handles the event when a schedule is paused.

        Parameters
        ----------
        event : object
            The event object associated with the pause action.
        schedule : object
            The schedule instance that has been paused.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is called when a schedule is paused. It sets internal flags and stores the event and schedule for later reference.
        """
        # Mark that the 'onPaused' event was called and store the arguments
        self.paused_called = True
        self.paused_event = event
        self.paused_schedule = schedule

    async def onResumed(self, event, schedule):
        """
        Handles the event when a schedule is resumed.

        Parameters
        ----------
        event : object
            The event object associated with the resume action.
        schedule : object
            The schedule instance that was resumed.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is called when a schedule is resumed. It sets internal flags and stores the event and schedule for later reference.
        """
        # Mark that the 'onResumed' event was called and store the arguments
        self.resumed_called = True
        self.resumed_event = event
        self.resumed_schedule = schedule

    async def onRemoved(self, event, schedule):
        """
        Handles the event when a schedule is removed.

        Parameters
        ----------
        event : object
            The event object associated with the removal.
        schedule : object
            The schedule object that was removed.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        This method is called when a schedule is removed. It sets internal flags and stores the event and schedule for later reference.
        """
        # Mark that the 'onRemoved' event was called and store the arguments
        self.removed_called = True
        self.removed_event = event
        self.removed_schedule = schedule