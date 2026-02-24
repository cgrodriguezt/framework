import asyncio
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from orionis.console.base.command import BaseCommand
from orionis.console.contracts.schedule import ISchedule
from orionis.console.enums.events import SchedulerEvent
from orionis.foundation.contracts.application import IApplication
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.support.time.local import LocalDateTime

class ScheduleWorkCommand(BaseCommand):

    # ruff: noqa: TC001 (DI)

    # Indicates whether timestamps will be shown in the command output
    timestamps: bool = False

    # Command signature and description
    signature: str = "schedule:work"

    # Command description
    description: str = "Executes the scheduled tasks defined in the application."

    def __startPanel(self) -> None:
        """
        Display a formatted scheduler start message on the console.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return a value. It prints a panel to the console.
        """
        console = Console()
        tz: str = LocalDateTime.getTimezone()
        pid: int = os.getpid()
        loop_policy = asyncio.get_event_loop_policy() # Python <= 3.16
        loop_name = loop_policy.__class__.__name__.replace("_","")
        now: str = LocalDateTime.now().format("YYYY-MM-DD HH:mm:ss")

        # Print a start message for the scheduler worker using rich console.
        console.line()
        panel_content = Text.assemble(
            ("🚀 Orionis Scheduler ", "bold white on green"),
            ("\n\n", ""),
            ("✅ The scheduled tasks has started successfully.\n", "white"),
            (
                f"🕒 Started at: {now} | 🌐 Timezone: {tz} | 🆔 PID: {pid}\n",
                "dim",
            ),
            ("⚡ Reactor Loop Policy: ", "cyan"),
            (f"{loop_name}\n\n", "bold magenta"),
            ("🛑 To stop, press ", "white"),
            ("Ctrl+C", "bold yellow"),
        )

        # Print the message in a styled panel.
        console.print(
            Panel(
                panel_content,
                border_style="green",
                padding=(1, 2),
            ),
        )

        # Print a separating line.
        console.line()

    async def handle(
        self,
        app: IApplication,
    ) -> None:
        """
        Run the application's scheduled tasks worker.

        Parameters
        ----------
        app : IApplication
            Application instance for configuration and service resolution.

        Returns
        -------
        None
            Executes the scheduler worker until interrupted by user input.
        """
        # Retrieve the Scheduler instance from the application
        scheduler = await app.getScheduler()

        # Create a reflection instance for method inspection
        rf_scheduler = ReflectionInstance(scheduler)

        # Check if the Scheduler class defines the 'tasks' method
        if not rf_scheduler.hasMethod("tasks"):
            error_msg = (
                "Scheduler must define a 'tasks(self, schedule: ISchedule)' "
                "method."
            )
            raise ValueError(error_msg)

        # Create an instance of the ISchedule service
        schedule_service: ISchedule = await app.make(ISchedule)

        # Register scheduled tasks using the Scheduler's tasks method
        await app.call(scheduler, "tasks", schedule=schedule_service)

        # Map of listener methods to their corresponding scheduler events
        listeners_methods_map: dict[str, SchedulerEvent] = {
            "onStarted": SchedulerEvent.STARTED,
            "onPaused": SchedulerEvent.PAUSED,
            "onResumed": SchedulerEvent.RESUMED,
            "onShutdown": SchedulerEvent.SHUTDOWN,
        }

        # Register event listeners if the corresponding methods are defined
        for method_name, event in listeners_methods_map.items():
            if rf_scheduler.hasMethod(method_name):
                schedule_service.on(event, getattr(scheduler, method_name))

        # Boot the schedule service to prepare it for running scheduled tasks
        await schedule_service.boot()

        # Print the panel only if the application is in debug mode
        if app.isDebug():
            self.__startPanel()

        try:
            # Wait for scheduled tasks to run indefinitely
            await schedule_service.wait()

        except (KeyboardInterrupt, asyncio.CancelledError):
            # Gracefully shutdown the scheduler on interruption
            schedule_service.shutdown()
            await schedule_service.wait()
