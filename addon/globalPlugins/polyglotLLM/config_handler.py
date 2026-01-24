# Configuration handling for the Polyglot-LLM NVDA add-on
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).


import os
import logHandler
from configobj import ConfigObj, ConfigObjError, flatten_errors
from configobj.validate import Validator
from .configspec import configspec
import globalVars


log = logHandler.log
config = None


def loadConfig():
	"""Loads the add-on's configuration."""
	global config
	path = os.path.abspath(os.path.join(globalVars.appArgs.configPath, "polyglotLLM.conf"))
	# Seek back to the beginning of the spec for every read, in case this is called twice
	configspec.seek(0)
	try:
		config = ConfigObj(
			infile=path, configspec=configspec, encoding="UTF8", create_empty=True
		)
	except ConfigObjError as exc:
		log.exception("While loading the configuration file")
		return
	validator = Validator()
	result = config.validate(validator, copy=True)
	if result != True:
		errors = reportValidationErrors(config, result)
		errors = "\n".join(errors)
		e = "error" + ("" if len(errors) == 1 else "s")
		log.error(e + " were encountered while validating the configuration.\n" + errors)


def reportValidationErrors(config, validation_result):
	"""Return any errors that were detected with the configuration file to display a friendly message."""
	errors = []
	for (section_list, key, _) in flatten_errors(config, validation_result):
		if key:
			errors.append(
				'"%s" key in section "%s" failed validation'
				% (key, ", ".join(section_list))
			)
		else:
			errors.append('missing required section "%s"' % (", ".join(section_list)))
	return errors


def saveConfig():
	"""Saves the configuration to disk."""
	global config
	if config is not None:
		config.write()
