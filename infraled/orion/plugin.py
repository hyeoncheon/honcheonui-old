"""Orion plugin, plugin management module for orion project.
"""

__mod_name__	= 'plugin'
__mod_version__	= '0.1.0'

import threading, queue
import time
import orion

class pluginError(orion.orionError):
	def __str__(self):
		return repr('pluginError:%s' % self.strerror)

class Plugin(threading.Thread):
	def __init__(self, pname, pver, ptype, conf, message_queue, logger):
		threading.Thread.__init__(self)
		self.plugin_type = ptype
		self.conf = conf
		self.mqueue = message_queue
		self.report_path = self.conf.get('report_path', None)
		self.logger = logger
		self.__stop = threading.Event()
		self.__chk = threading.Event()
		self.__rpt = threading.Event()

		self.setName('%s-%s' % (ptype, pname))
		loglevel = self.conf.get('loglevel')
		self.logger.debug(' configured loglevel is %s' % loglevel)
		loglevel = orion.util_logger_setlevel(self.logger, loglevel)
		self.logger.info('effective loglevel is %s' % loglevel)

		if self.plugin_type == 'periodic':
			self.int_chk = int(self.conf.get('check_interval', 0))
			self.int_rpt = int(self.conf.get('report_interval', 0))
			self.logger.info("check every %d, report every %d." %
					(self.int_chk, self.int_rpt))

		self.initialize()
		self.logger.info('<%s> initialized!' % self.name)
		return

	def initialize(self):
		self.logger.warn('OVERRIDE IT ----')
		return

	def run(self):
		time.sleep(1)	# startup delay.
		self.logger.info('running <%s>...' % self.name)
		self.task_pre()
		if self.plugin_type == 'periodic':
			self.periodic()
		elif self.plugin_type == 'handler':
			self.handler_loop()
		self.task_post()
		self.logger.info('<%s> finished!' % self.getName())
		return

	def handler_loop(self):
		self.logger.info('starting handling loop...')
		while not self.__stop.is_set():
			self.task_handler()
			time.sleep(0.2)
		self.logger.info('finished handling loop...')
		return

	def periodic(self):
		self.logger.info('jump into the fire!')
		while not self.__stop.is_set():
			if self.__chk.is_set():
				self.__chk.clear()
				self.task_check()
				if self.__rpt.is_set():
					self.__rpt.clear()
					self.task_report()
			else:
				time.sleep(0.2)	# XXX HARD-CODING, PERFORMANCE
		# XXX check no-more-queue!
		self.logger.debug('come out from the duty!')
		return

	def task_pre(self):
		return self.logger.debug('has no task_pre. _PH_')

	def task_check(self):
		return self.logger.debug('has no task_check. _PH_')

	def task_report(self):
		return self.logger.debug('has no task_report. _PH_')

	def task_post(self):
		return self.logger.debug('has no task_post. _PH_')

	def task_handler(self):
		if self.plugin_type == 'handler':
			self.logger.error('handler need to implement this!')
		return

	def stop(self):
		return self.__stop.set()

	def tick(self, now_ts):
		if (now_ts % self.int_chk) == 0:
			self.__chk.set()
		if (now_ts % self.int_rpt) == 0:
			self.__rpt.set()
		return


	def mq_data_request(self, message, path = ''):
		if path == '':
			path = self.report_path
		msg = { 'type':'data_request', 'from':self.getName(), 'path':path,
				'message':message}
		return self.mqueue.dq.put(msg)



class PluginManager():
	def __init__(self, conf, logger):
		self.conf = conf
		self.logger = logger.getChild('p')	# short!

		self.mqueue = mQueue()
		self.plugins = list()

		self.logger.info('plugin manager initialized!')
		return

	def load_plugin(self, plugin, wait_until_done):
		self.logger.debug('  - trying to load <%s>...' % plugin)
		try:
			mod = __import__('plugins.%s' % plugin, fromlist = ['plugins'])
			mclass = getattr(mod, plugin)
			pn = getattr(mod, '_plugin_name')
			pv = getattr(mod, '_plugin_version')
			pt = getattr(mod, '_plugin_type')
			self.logger.debug('  - %s %s (%s)...' % (pn, pv, pt))
			logger = self.logger.getChild(plugin)
			conf = self.conf.get_branch('plugins/plugin[@name="%s"]' % plugin,
					'honcheonui')
			plugin_thread = mclass(pn, pv, pt, conf, self.mqueue, logger)
			plugin_thread.start()
		except (ImportError, AttributeError) as e:
			self.logger.error('- cannot import plugin <%s>' % plugin)
			self.logger.error('-- E(%s)' % e)
			raise
		except:
			self.logger.info('UNKNOWN EXCEPTION.')
			raise
		else:
			self.plugins.append(plugin_thread)
			self.logger.info('  <%s> registered.' % plugin)

		if wait_until_done:
			self.logger.debug('blocking mode. wait until done.')
			plugin_thread.join(30)
			if plugin_thread.is_alive():
				self.logger.warn('what is happen? still alive!')
			else:
				self.plugins.remove(plugin_thread)
				self.logger.debug('ok, blocked thread finished.')

		return

	def load_plugins(self, ptype, block = False):
		self.logger.debug(' loading %s plugins...', ptype)
		cnt = 0
		for plugin in self.conf.subnames('plugins/plugin[@type="%s"]' % ptype):
			self.logger.debug(' - loading plugin <%s>...' % plugin)
			self.load_plugin(plugin, block)
			cnt += 1
		self.logger.info(' ... %d %s module(s) loaded.' % (cnt, ptype))
		return

	def get_list(self):
		return self.plugins

	def tick_at(self, interval):
		while True:
			now_ts = int(time.time())
			if (now_ts % interval) == 0:
				for p in self.plugins:
					if p.is_alive() and p.plugin_type == 'periodic':
						p.tick(now_ts)
				time.sleep(1)	# important! prevent double working.
				return
			else:
				time.sleep(0.1)	# XXX HARD-CODING, PERFORMANCE
		return

	def clean(self):
		for p in self.plugins:
			# XXX KeyboardInterrupt
			p.join(0.1)
			if not p.is_alive():
				self.logger.info('   <%s> is done.' % p.getName())
				self.plugins.remove(p)
			else:
				#self.logger.debug('<%s> is alive.' % p.getName())
				pass
		return

	def clean_all(self):
		while len(self.plugins) > 0:
			self.logger.info(' %d plugin(s) remind...' % len(self.plugins))
			self.clean()
			time.sleep(0.5)
		return

	def shutdown(self):
		self.logger.info('final lap...')
		for p in self.plugins:
			p.stop()
		self.clean_all()
		return




import queue
from collections import namedtuple
class mQueue:
	def __init__(self):
		self.dq = queue.Queue(-1)
		self.mq = dict()
		self.hq = dict()


# vim:set ts=4 sw=4:
