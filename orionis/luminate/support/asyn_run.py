import asyncio

class AsyncExecutor:

    @staticmethod
    def run(callback: asyncio.coroutine) -> None:
        """
        Runs a coroutine synchronously.

        Parameters
        ----------
        callback : asyncio.coroutine
            The coroutine to run.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(callback)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(callback)