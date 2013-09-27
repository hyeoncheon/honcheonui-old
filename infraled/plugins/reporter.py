
_plugin_name	= 'reporter'
_plugin_version	= '0.0.1'
_plugin_type	= 'handler'


import orion.plugin
import time
import queue


class reporter(orion.plugin.Plugin):
	def initialize(self):
		return

	def task_pre(self):
		return super().task_pre()

	def task_post(self):
		return super().task_post()

	def task_handler(self):
		try:
			message = self.mqueue.dq.get(True, 0.5)
		except queue.Empty:
			pass
		else:
			self.logger.debug('message is %s.' % message)
		return

# vim:set ts=4 sw=4:
