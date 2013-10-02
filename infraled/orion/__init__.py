"""
"""

__package_name__	= 'orion'
__package_version__	= '0.1.0'

import os
import logging
from xml.etree import ElementTree

def util_logger_setlevel(logger, level):
	if level == 'fatal':
		logger.setLevel(logging.FATAL)
	elif level == 'error':
		logger.setLevel(logging.ERROR)
	elif level == 'warn':
		logger.setLevel(logging.WARN)
	elif level == 'debug':
		logger.setLevel(logging.DEBUG)
	else:
		logger.setLevel(logging.INFO)
	return util_logger_getlevel(logger)

def util_logger_getlevel(logger):
	level = logger.getEffectiveLevel()
	if level == 50:
		str_level = 'fatal'
	elif level == 40:
		str_level = 'error'
	elif level == 30:
		str_level = 'warn'
	elif level == 20:
		str_level = 'info'
	elif level == 10:
		str_level = 'debug'
	else:
		str_level = 'notset'
	return str_level


### default logger	----------------------------------------------------------
class Logger:
	# local logger for fail-over.
	def __init__(self):
		return

	def error(self, string):
		return self.debug(string)

	def warn(self, string):
		return self.debug(string)

	def debug(self, string):
		import sys
		return sys.stderr.write("%s: %s\n" %(__package_name__, string))


### configuration holder	--------------------------------------------------
class orionError(Exception):
	"""Configuration Error"""
	def __init__(self, code, value):
		self.errno = code
		self.strerror = value

	def __str__(self):
		return repr(self.strerror)

class configError(orionError):
	def __str__(self):
		return repr('configError:%s' % self.strerror)


class Config:
	def __init__(self, element=None, filename=None, text=None, logger=None):
		self.filename = filename
		if logger:
			self.logger = logger
		else:
			self.logger = Logger()

		if text:
			try:
				self.doc = ElementTree.fromstring(text)
			except ElementTree.ParseError as e:
				raise configError(2, 'cannot parse config. (%s)' % text)
		elif self.filename:
			if os.access(filename, os.R_OK) == False:
				raise configError(3, 'cannot access file. (%s)' % filename)

			try:
				self.doc = ElementTree.ElementTree(file=filename)
			except ElementTree.ParseError as e:
				raise configError(4, 'cannot parse file. (%s)' % filename)
		elif element is not None:
			self.doc = ElementTree.ElementTree(element=element)
		else:
			raise configError(1, 'initializing failed. no file and text.')

		self.debug()
		return

	def set(self, key, value, save = False):
		"""Set configuration value on 'key'
		If argument 'save' is True, it call method save() too.
		If there is more than one node with save path, first on is used.
		"""
		el = None
		nodelist = self.doc.findall(key)
		if len(nodelist) > 1:
			self.logger.warn("eep! duplicated key found. using first!")
			el = nodelist[0]
		elif len(nodelist) < 1:
			self.logger.warn("eep! kay not found. add new element!")
			el = ElementTree.SubElement(self.doc.getroot(), "key")
		else:
			el = nodelist[0]

		el.text = str(value)

		self.debug()
		if save == True:
			self.save()
		return

	def get(self, key, default = None):
		"""Get configuration value on 'key'
		If there is more than one node with save path, first on is used.
		"""
		nodelist = self.doc.findall(key)
		if len(nodelist) > 1:
			self.logger.warn("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			self.logger.warn("eep! no value found for key!:%s" % key)
			return default
		return nodelist[0].text

	def get_branch(self, key, subtree = None):
		branch = Config(element = self.doc.find(key), logger = self.logger)
		if subtree != None:
			branch.doc.getroot().append(self.doc.find(subtree))
		branch.debug()
		return branch

	def get_branch_as_dict(self, key):
		return self.get_branch(key)

	def subkeys(self, key):
		keylist = list()
		for node in self.doc.findall(key):
			keylist.append(node.tag)
		return keylist

	def subnames(self, key):
		namelist = list()
		for node in self.doc.findall(key):
			namelist.append(node.attrib['name'])
		return namelist

	def save(self, filename = None):
		"""Save current configuration on xml file.
		If argument 'filename' is not given, write on current file.
		"""
		### FIXME save backup!
		if filename != None:
			self.filename = filename

		if self.filename:
			if ElementTree.VERSION >= "1.3.0":	# for python 3.x
				self.doc.write(self.filename, 'utf-8', xml_declaration=True)
			else:
				self.doc.write(self.filename, 'utf-8')
		else:
			self.logger.warn('filename is not defined. abort!')

		return

	def debug(self):
		if False:
			self.logger.debug('DEBUG for %s --------' % self)
			ElementTree.dump(self.doc)
		return

# vim:set ts=4 sw=4:
