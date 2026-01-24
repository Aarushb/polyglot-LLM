# Configuration handling for the Polyglot-LLM NVDA add-on
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).


import logHandler
import config


log = logHandler.log

# Configuration specification for NVDA's config system
confspec = {
	"api_key": "string(default='')",
	"target_language": "string(default='en')",
	"system_prompt": "string(default='You are a professional translator. Automatically detect the source language of the input text and translate it to {target_language}. Respond ONLY with the translated text. Do not include the source language name, explanations, notes, or any other content.')",
	"conversation_mode": "boolean(default=False)",
	"conversation_history_length": "integer(default=10, min=5, max=20)",
	"thinking_budget": "string(default='low')",
	"max_tokens": "integer(default=2048, min=256, max=8192)",
	"cache_translations": "boolean(default=True)",
	"real_time_enabled": "boolean(default=False)",
	"copy_translations": "boolean(default=True)",
}


def initConfig():
	"""Initialize configuration in NVDA's config system."""
	config.conf.spec["polyglotLLM"] = confspec


def getConfig():
	"""Get the configuration dictionary."""
	return config.conf["polyglotLLM"]


def saveConfig():
	"""Save configuration to disk."""
	try:
		config.conf.save()
	except Exception as e:
		log.error(f"Failed to save configuration: {str(e)}")
