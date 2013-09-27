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

import orion.runner
import orion.plugin

class StarLight(orion.runner.Daemon):
	def initialize(self):
		self.logger.info("initializing %s..." % _my_name)
		# first call. it can be call again.
		self.init_more()

		if not self.opts.debug:
			self.daemonize()
		self.logger.info('%s[%d] started!' % (_my_name, os.getpid()));
		return

	def init_more(self):
		# initialize configurations...
		self.logger.debug("  config with '%s'..." % self.opts.config)
		try:
			self.conf = orion.Config(filename = self.opts.config,
					logger = self.logger)
		except orion.configError as e:
			self.logger.error('  configuration error! abort!')
			sys.exit()

		self.conf.set('honcheonui/name', 'honcheonui-%s' % _my_name)
		self.conf.set('honcheonui/version', _version)
		self.logger.debug('  loglevel: %s' %
				self.conf.get('honcheonui/loglevel'))

		self.logger.info('  %s configured!' % self.conf.get('honcheonui/name'))
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

		self.logger.debug('ready! jump into the universe...')
		while not self.interrupted:
			#self.logger.debug("i'm running")
			plugin_manager.clean()
			try:
				plugin_manager.tick_at(5)	# FIXME HARD-CODING
			except KeyboardInterrupt:
				break;
			# printed at every tick + 1sec. since sleep on tick.
			self.logger.debug('consums %.1f%% (%.2f/%.1f)' %
					(time.clock() / self.runtime() * 100,
						time.clock(), self.runtime()))

		self.logger.debug('loop exited. interrupted?')
		plugin_manager.shutdown()



if __name__ == '__main__':
	starlight = StarLight(_my_name)
	starlight.run()

# vim:set ts=4 sw=4:
