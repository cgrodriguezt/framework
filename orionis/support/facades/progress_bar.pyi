from orionis.console.dynamic.contracts.progress_bar import IProgressBar

class ProgressBar(IProgressBar):

    @classmethod
    async def init(cls) -> None:
        ...