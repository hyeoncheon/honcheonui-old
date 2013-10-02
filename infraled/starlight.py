#!/usr/bin/env python3
#
# starlight - honcheonui agent for managed server.
#
#	written by Yonghwan SO <sio4@users.sf.net>
#
# -c `pwd`/new.xml -l `pwd`/tmp/agent.log -e `pwd`/tmp/stderr.log -d --start

_my_name	= 'starlight'
_version	= '0.0.1'

import sys,os
import time
import uuid

import orion.runner
import orion.plugin

class StarLight(orion.runner.Daemon):
	def initialize(self):
		self.logger.info('starting engines...')
		# first call. it can be call again.
		self.configure()

		if not self.opts.debug:
			self.daemonize()
		self.logger.info('gear on the dee! [%d]' % os.getpid());
		return

	def configure(self):
		# initialize configurations...
		#
		self.logger.debug(" configuration with '%s'..." % self.opts.config)
		try:
			self.conf = orion.Config(filename = self.opts.config,
					logger = self.logger)
		except orion.configError as e:
			self.logger.error('  configuration error! abort!')
			sys.exit()

		self.conf.set('honcheonui/name', 'honcheonui-%s' % _my_name)
		self.conf.set('honcheonui/version', _version)

		loglevel = self.conf.get('honcheonui/loglevel')
		self.logger.debug('  - configured loglevel is %s' % loglevel)
		loglevel = orion.util_logger_setlevel(self.logger, loglevel)
		self.logger.info('  - effective loglevel is %s' % loglevel)

		try:
			uuid_str = self.conf.get('honcheonui/uuid', 'noset')
			self.uuid = uuid.UUID(uuid_str)
		except (ValueError, TypeError):
			self.logger.warn('invalid uuid: %s' % uuid_str)
			self.uuid = uuid.uuid1()
			self.logger.warn('new uuid generated: %s' % str(self.uuid))
			self.conf.set('honcheonui/uuid', str(self.uuid), True)

		self.logger.info(' configured!' % self.uuid)
		return

	def run(self):
		plugin_manager = orion.plugin.PluginManager(self.conf, self.logger)
		plugin_manager.load_plugins('controller')
		plugin_manager.load_plugins('handler')
		plugin_manager.load_plugins('run-once', True)
		plugin_manager.load_plugins('periodic')

		if self.opts.debug:
			self.logger.debug('### plugin list: ----------')
			for m in plugin_manager.get_list():
				self.logger.debug('-- plugin <%s>' % m.name)
			self.logger.debug('### plugin list: ----------')

		self.logger.info('ready! jump into the fire race!')
		while not self.interrupted:
			plugin_manager.clean()
			try:
				plugin_manager.tick_at(5)	# FIXME HARD-CODING
			except KeyboardInterrupt:
				break;
			# printed at every tick + 1sec. since sleep on tick.
			self.logger.debug('consums %.1f%% (%.2f/%.1f)' %
					(time.clock() / self.runtime() * 100,
						time.clock(), self.runtime()))

		self.logger.debug('loop exited. maybe interrupted?')
		plugin_manager.shutdown()
		self.logger.info('bye.')



if __name__ == '__main__':
	starlight = StarLight(_my_name)
	starlight.run()

# vim:set ts=4 sw=4:
