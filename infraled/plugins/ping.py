
_plugin_name	= 'ping'
_plugin_version	= '0.1.0'
_plugin_type	= 'periodic'


import orion.plugin
import time



class ping(orion.plugin.Plugin):
	def initialize(self):
		return

	def task_pre(self):
		return super().task_pre()

	def task_post(self):
		return super().task_post()

	def task_check(self):
		return

	def task_report(self):
		self.mq_data_request('',"report i'm alive~!")
		return


# vim:set ts=4 sw=4:
