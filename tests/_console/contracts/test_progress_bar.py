from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_progress_bar import DummyProgressBar

class TestIProgressBar(AsyncTestCase):

	async def testStartInitializesProgressBar(self):
		"""
		Test that start() initializes the progress bar.

		Ensures that calling start() sets the started flag to True and resets progress to 0.
		"""
		bar = DummyProgressBar()
		bar.start()
		self.assertTrue(bar.started)
		self.assertEqual(bar.progress, 0)

	async def testAdvanceIncreasesProgress(self):
		"""
		Test that advance() increases the progress value.

		Ensures that calling advance() with a positive increment increases the progress accordingly.
		"""
		bar = DummyProgressBar()
		bar.start()
		bar.advance(5)
		self.assertEqual(bar.progress, 5)
		bar.advance(3)
		self.assertEqual(bar.progress, 8)

	async def testFinishMarksAsFinished(self):
		"""
		Test that finish() marks the progress bar as finished.

		Ensures that calling finish() sets the finished flag to True.
		"""
		bar = DummyProgressBar()
		bar.start()
		bar.finish()
		self.assertTrue(bar.finished)

	async def testAdvanceWithoutStart(self):
		"""
		Test advancing progress without starting the bar.

		Ensures that advance() can be called before start(), and progress is updated.
		"""
		bar = DummyProgressBar()
		bar.advance(2)
		self.assertEqual(bar.progress, 2)

	async def testMultipleStartResetsProgress(self):
		"""
		Test that calling start() multiple times resets progress.

		Ensures that progress is reset to 0 every time start() is called.
		"""
		bar = DummyProgressBar()
		bar.start()
		bar.advance(10)
		bar.start()
		self.assertEqual(bar.progress, 0)
