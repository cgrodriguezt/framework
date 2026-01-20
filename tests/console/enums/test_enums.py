from orionis.console.enums.actions import ArgumentAction
from orionis.console.enums.listener import ListeningEvent
from orionis.console.enums.styles import ANSIColors
from orionis.test.cases.synchronous import SyncTestCase

class TestConsoleEnums(SyncTestCase):

	def testArgumentActionValues(self):
		"""
		Test that ArgumentAction enum members have correct string values.

		Returns
		-------
		None
		"""
		self.assertEqual(ArgumentAction.STORE.value, "store")
		self.assertEqual(ArgumentAction.STORE_CONST.value, "store_const")
		self.assertEqual(ArgumentAction.STORE_TRUE.value, "store_true")
		self.assertEqual(ArgumentAction.STORE_FALSE.value, "store_false")
		self.assertEqual(ArgumentAction.APPEND.value, "append")
		self.assertEqual(ArgumentAction.APPEND_CONST.value, "append_const")
		self.assertEqual(ArgumentAction.COUNT.value, "count")
		self.assertEqual(ArgumentAction.HELP.value, "help")
		self.assertEqual(ArgumentAction.VERSION.value, "version")

	def testArgumentActionMembership(self):
		"""
		Test that all expected members exist in ArgumentAction enum.

		Returns
		-------
		None
		"""
		expected = {
			"STORE", "STORE_CONST", "STORE_TRUE", "STORE_FALSE",
			"APPEND", "APPEND_CONST", "COUNT", "HELP", "VERSION",
		}
		self.assertSetEqual(set(ArgumentAction.__members__.keys()), expected)

	def testListeningEventValues(self):
		"""
		Test that ListeningEvent enum members have correct string values.

		Returns
		-------
		None
		"""
		self.assertEqual(ListeningEvent.SCHEDULER_STARTED.value, "schedulerStarted")
		self.assertEqual(ListeningEvent.SCHEDULER_SHUTDOWN.value, "schedulerShutdown")
		self.assertEqual(ListeningEvent.SCHEDULER_PAUSED.value, "schedulerPaused")
		self.assertEqual(ListeningEvent.SCHEDULER_RESUMED.value, "schedulerResumed")
		self.assertEqual(ListeningEvent.SCHEDULER_ERROR.value, "schedulerError")
		self.assertEqual(ListeningEvent.JOB_BEFORE.value, "before")
		self.assertEqual(ListeningEvent.JOB_AFTER.value, "after")
		self.assertEqual(ListeningEvent.JOB_ON_FAILURE.value, "onFailure")
		self.assertEqual(ListeningEvent.JOB_ON_MISSED.value, "onMissed")
		self.assertEqual(ListeningEvent.JOB_ON_MAXINSTANCES.value, "onMaxInstances")
		self.assertEqual(ListeningEvent.JOB_ON_PAUSED.value, "onPaused")
		self.assertEqual(ListeningEvent.JOB_ON_RESUMED.value, "onResumed")
		self.assertEqual(ListeningEvent.JOB_ON_REMOVED.value, "onRemoved")

	def testListeningEventMembership(self):
		"""
		Test that all expected members exist in ListeningEvent enum.

		Returns
		-------
		None
		"""
		expected = {
			"SCHEDULER_STARTED", "SCHEDULER_SHUTDOWN", "SCHEDULER_PAUSED", "SCHEDULER_RESUMED", "SCHEDULER_ERROR",
			"JOB_BEFORE", "JOB_AFTER", "JOB_ON_FAILURE", "JOB_ON_MISSED", "JOB_ON_MAXINSTANCES", "JOB_ON_PAUSED", "JOB_ON_RESUMED", "JOB_ON_REMOVED",
		}
		self.assertSetEqual(set(ListeningEvent.__members__.keys()), expected)

	def testANSIColorsValues(self):
		"""
		Test that ANSIColors enum members have correct ANSI escape code values.

		Returns
		-------
		None
		"""
		self.assertEqual(ANSIColors.DEFAULT.value, "\033[0m")
		self.assertEqual(ANSIColors.BG_INFO.value, "\033[44m")
		self.assertEqual(ANSIColors.BG_ERROR.value, "\033[41m")
		self.assertEqual(ANSIColors.BG_FAIL.value, "\033[48;5;166m")
		self.assertEqual(ANSIColors.BG_WARNING.value, "\033[43m")
		self.assertEqual(ANSIColors.BG_SUCCESS.value, "\033[42m")
		self.assertEqual(ANSIColors.TEXT_INFO.value, "\033[34m")
		self.assertEqual(ANSIColors.TEXT_ERROR.value, "\033[91m")
		self.assertEqual(ANSIColors.TEXT_WARNING.value, "\033[33m")
		self.assertEqual(ANSIColors.TEXT_SUCCESS.value, "\033[32m")
		self.assertEqual(ANSIColors.TEXT_WHITE.value, "\033[97m")
		self.assertEqual(ANSIColors.TEXT_MUTED.value, "\033[90m")
		self.assertEqual(ANSIColors.TEXT_BOLD_INFO.value, "\033[1;34m")
		self.assertEqual(ANSIColors.TEXT_BOLD_ERROR.value, "\033[1;91m")
		self.assertEqual(ANSIColors.TEXT_BOLD_WARNING.value, "\033[1;33m")
		self.assertEqual(ANSIColors.TEXT_BOLD_SUCCESS.value, "\033[1;32m")
		self.assertEqual(ANSIColors.TEXT_BOLD_WHITE.value, "\033[1;97m")
		self.assertEqual(ANSIColors.TEXT_BOLD_MUTED.value, "\033[1;90m")
		self.assertEqual(ANSIColors.TEXT_BOLD.value, "\033[1m")
		self.assertEqual(ANSIColors.TEXT_STYLE_UNDERLINE.value, "\033[4m")
		self.assertEqual(ANSIColors.DEFAULT.value, "\033[0m")
		self.assertEqual(ANSIColors.CYAN.value, "\033[36m")
		self.assertEqual(ANSIColors.DIM.value, "\033[2m")
		self.assertEqual(ANSIColors.MAGENTA.value, "\033[35m")
		self.assertEqual(ANSIColors.ITALIC.value, "\033[3m")

	def testANSIColorsMembership(self):
		"""
		Test that all expected members exist in ANSIColors enum.

		Returns
		-------
		None
		"""
		expected = {
			"DEFAULT", "BG_INFO", "BG_ERROR", "BG_FAIL", "BG_WARNING", "BG_SUCCESS",
			"TEXT_INFO", "TEXT_ERROR", "TEXT_WARNING", "TEXT_SUCCESS", "TEXT_WHITE", "TEXT_MUTED",
			"TEXT_BOLD_INFO", "TEXT_BOLD_ERROR", "TEXT_BOLD_WARNING", "TEXT_BOLD_SUCCESS", "TEXT_BOLD_WHITE", "TEXT_BOLD_MUTED",
			"TEXT_BOLD", "TEXT_STYLE_UNDERLINE", "CYAN", "DIM", "MAGENTA", "ITALIC",
		}
		self.assertSetEqual(set(ANSIColors.__members__.keys()), expected)

	def testEnumStringConversion(self):
		"""
		Test that enums can be converted to string and compared to their values.

		Returns
		-------
		None
		"""
		self.assertEqual(str(ArgumentAction.STORE), "ArgumentAction.STORE")
		self.assertEqual(str(ListeningEvent.JOB_AFTER), "ListeningEvent.JOB_AFTER")
		self.assertEqual(str(ANSIColors.TEXT_BOLD), "ANSIColors.TEXT_BOLD")
