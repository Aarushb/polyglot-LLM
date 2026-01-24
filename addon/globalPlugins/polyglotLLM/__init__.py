# Polyglot-LLM Global Plugin for NVDA
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).


import sys
import os
import threading
import logHandler

log = logHandler.log

import api
import addonHandler

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Couldn't initialise translations.")

import wx
import globalVars
import gui
from gui.settingsDialogs import NVDASettingsDialog
import ui
import globalPluginHandler
import scriptHandler
import textInfos
import speech
import queueHandler
import config

# Import our modules
from . import config_handler as ch
from . import languages
from .gemini_translator import GeminiTranslator, AsyncTranslator
from .cache import TranslationCache
from .settings_panel import PolyglotLLMSettingsPanel


# Global variables
_nvdaSpeak = None
_translator = None
_async_translator = None
_cache = None
_lastTranslatedText = None


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Polyglot-LLM")
	
	def __init__(self):
		"""Initializes the global plugin object."""
		super(GlobalPlugin, self).__init__()
		
		# If on a secure Desktop, disable the add-on
		if globalVars.appArgs.secure:
			return
		
		global _nvdaSpeak, _translator, _async_translator, _cache
		
		# Initialize configuration
		ch.initConfig()
		
		# Initialize cache
		_cache = TranslationCache()
		
		# Initialize translator
		self._initializeTranslator()
		
		# Hook NVDA's speak function for real-time translation
		_nvdaSpeak = speech._manager.speak
		speech._manager.speak = self._speak
		
		# Register settings panel
		NVDASettingsDialog.categoryClasses.append(PolyglotLLMSettingsPanel)
		
		# Variables for on-demand translation
		self.lastSpokenText = None
		self.lastTranslation = None
		
		log.info("Polyglot-LLM initialized")
	
	def _initializeTranslator(self):
		"""Initialize or reinitialize the translator with current settings."""
		global _translator, _async_translator
		
		cfg = ch.getConfig()
		api_key = cfg["api_key"]
		target_language = cfg["target_language"]
		system_prompt = cfg["system_prompt"]
		thinking_budget = cfg["thinking_budget"]
		max_tokens = cfg["max_tokens"]
		
		_translator = GeminiTranslator(
			api_key=api_key,
			target_language=languages.getLanguageName(target_language),
			system_prompt=system_prompt,
			thinking_budget=thinking_budget,
			max_tokens=max_tokens
		)
		
		_async_translator = AsyncTranslator(_translator)
	
	def terminate(self):
		"""Called when this plugin is terminated."""
		global _nvdaSpeak
		
		# Restore original speak function
		if _nvdaSpeak:
			speech._manager.speak = _nvdaSpeak
		
		# Remove settings panel
		try:
			NVDASettingsDialog.categoryClasses.remove(PolyglotLLMSettingsPanel)
		except (ValueError, AttributeError):
			pass
		
		log.info("Polyglot-LLM terminated")
	
	def _speak(self, speechSequence, priority=None):
		"""
		Override NVDA's speak function for real-time translation.
		"""
		global _translator, _cache, _lastTranslatedText
		
		cfg = ch.getConfig()
		real_time_enabled = cfg["real_time_enabled"]
		
		# If real-time translation is disabled, use original speak
		if not real_time_enabled or not _translator:
			return _nvdaSpeak(speechSequence=speechSequence, priority=priority)
		
		# Extract text from speech sequence
		text_items = [x for x in speechSequence if isinstance(x, str)]
		if not text_items:
			return _nvdaSpeak(speechSequence=speechSequence, priority=priority)
		
		# Store for later reference
		self.lastSpokenText = " ".join(text_items)
		text_to_translate = self.lastSpokenText
		
		# Get app name for cache
		try:
			app_name = globalVars.focusObject.appModule.appName
		except:
			app_name = "__global__"
		
		# Check cache first
		conversation_mode = cfg["conversation_mode"]
		conversation_history = _translator.conversation_history if conversation_mode else None
		
		cached_translation = None
		if cfg["cache_translations"]:
			cached_translation = _cache.get(
				text_to_translate,
				cfg["target_language"],
				app_name,
				conversation_mode,
				conversation_history
			)
		
		if cached_translation:
			# Use cached translation
			translated_text = cached_translation
			_lastTranslatedText = translated_text
			
			# Create new speech sequence with translated text
			newSpeechSequence = [translated_text if isinstance(x, str) else x for x in speechSequence]
			return _nvdaSpeak(speechSequence=newSpeechSequence, priority=priority)
		
		# Translate synchronously for real-time mode
		translated_text = _translator.translate(text_to_translate, conversation_mode)
		
		if translated_text:
			_lastTranslatedText = translated_text
			
			# Cache the translation
			if cfg["cache_translations"]:
				_cache.set(
					text_to_translate,
					translated_text,
					cfg["target_language"],
					app_name,
					conversation_mode,
					conversation_history
				)
			
			# Create new speech sequence with translated text
			newSpeechSequence = [translated_text if isinstance(x, str) else x for x in speechSequence]
			return _nvdaSpeak(speechSequence=newSpeechSequence, priority=priority)
		else:
			# Translation failed, use original text
			return _nvdaSpeak(speechSequence=speechSequence, priority=priority)
	
	def _getSelectedText(self):
		"""Get currently selected text."""
		obj = api.getCaretObject()
		try:
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
			if info and not info.isCollapsed:
				return info.text
		except (RuntimeError, NotImplementedError):
			return None
		return None
	
	def _translateAsync(self, text, callback_message=None, skip_speech=False):
		"""Translate text asynchronously and announce result."""
		global _async_translator, _cache
		
		if not _translator:
			if not skip_speech:
				ui.message(_("Translation not configured. Please set API key in settings."))
			return
		
		if not text or not text.strip():
			if not skip_speech:
				ui.message(_("No text to translate"))
			return
		
		cfg = ch.getConfig()
		
		# Get app name for cache
		try:
			app_name = globalVars.focusObject.appModule.appName
		except:
			app_name = "__global__"
		
		# Check cache
		conversation_mode = cfg["conversation_mode"]
		conversation_history = _translator.conversation_history if conversation_mode else None
		
		cached_translation = None
		if cfg["cache_translations"]:
			cached_translation = _cache.get(
				text,
				cfg["target_language"],
				app_name,
				conversation_mode,
				conversation_history
			)
		
		if cached_translation:
			self.lastTranslation = cached_translation
			if not skip_speech:
				ui.message(cached_translation)
			if cfg["copy_translations"]:
				api.copyToClip(cached_translation)
			return
		
		# Translate asynchronously
		def on_success(translated_text):
			self.lastTranslation = translated_text
			
			# Cache the translation
			if cfg["cache_translations"]:
				_cache.set(
					text,
					translated_text,
					cfg["target_language"],
					app_name,
					conversation_mode,
					conversation_history
				)
			
			# Announce and optionally copy
			if not skip_speech:
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, translated_text)
			if cfg["copy_translations"]:
				queueHandler.queueFunction(queueHandler.eventQueue, api.copyToClip, translated_text)
		
		def on_error(error_msg):
			if not skip_speech:
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Translation failed"))
		
		_async_translator.translate(text, conversation_mode, on_success, on_error)
	
	# Translation Layer Scripts
	
	@scriptHandler.script(
		description=_("Activate translation layer"),
		gesture="kb:NVDA+shift+t",
		category=_("Polyglot-LLM")
	)
	def script_activateTranslationLayer(self, gesture):
		"""Activate the translation layer."""
		# Bind layer gestures
		self.bindGestures(self.__layerGestures)
		# Play sound instead of speech to avoid translation
		import tones
		tones.beep(500, 50)
	
	@scriptHandler.script(
		description=_("Translate selected text"),
		category=_("Polyglot-LLM")
	)
	def script_translateSelection(self, gesture):
		"""Translate selected text."""
		text = self._getSelectedText()
		if not text:
			ui.message(_("No selection"))
			# Stay in layer
			return
		self._translateAsync(text)
		# Exit layer after translation
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Translate clipboard text"),
		category=_("Polyglot-LLM")
	)
	def script_translateClipboard(self, gesture):
		"""Translate clipboard content."""
		try:
			text = api.getClipData()
		except:
			text = None
		
		if not text or not isinstance(text, str) or text.isspace():
			ui.message(_("Clipboard is empty"))
			# Stay in layer
			return
		
		self._translateAsync(text)
		# Exit layer after translation
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Translate last spoken text"),
		category=_("Polyglot-LLM")
	)
	def script_translateLastSpoken(self, gesture):
		"""Translate the last spoken text."""
		if self.lastSpokenText:
			self._translateAsync(self.lastSpokenText)
		else:
			ui.message(_("No last spoken text"))
			# Stay in layer
			return
		# Exit layer after translation
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Copy last translation to clipboard"),
		category=_("Polyglot-LLM")
	)
	def script_copyLastTranslation(self, gesture):
		"""Copy last translation to clipboard."""
		if self.lastTranslation:
			api.copyToClip(self.lastTranslation)
			ui.message(_("Translation copied"))
		else:
			ui.message(_("No translation to copy"))
		# Stay in layer for more commands
	
	@scriptHandler.script(
		description=_("Announce current translation settings"),
		category=_("Polyglot-LLM")
	)
	def script_announceSettings(self, gesture):
		"""Announce current translation settings."""
		cfg = ch.getConfig()
		target_lang = languages.getLanguageName(cfg["target_language"])
		convo_status = _("on") if cfg["conversation_mode"] else _("off")
		realtime_status = _("on") if cfg["real_time_enabled"] else _("off")
		message = _("Target: {lang}, Conversation: {convo}, Real-time: {rt}").format(
			lang=target_lang, convo=convo_status, rt=realtime_status
		)
		ui.message(message)
		# Stay in layer
	
	@scriptHandler.script(
		description=_("Toggle conversation mode"),
		category=_("Polyglot-LLM")
	)
	def script_toggleConversationMode(self, gesture):
		"""Toggle conversation mode."""
		cfg = ch.getConfig()
		cfg["conversation_mode"] = not cfg["conversation_mode"]
		ch.saveConfig()
		
		if cfg["conversation_mode"]:
			ui.message(_("Conversation mode on"))
		else:
			# Clear conversation history when disabling
			if _translator:
				_translator.clearConversationHistory()
			ui.message(_("Conversation mode off"))
		# Stay in layer for more commands
	
	@scriptHandler.script(
		description=_("Toggle real-time translation mode"),
		category=_("Polyglot-LLM")
	)
	def script_toggleRealTimeTranslation(self, gesture):
		"""Toggle real-time translation on/off."""
		cfg = ch.getConfig()
		cfg["real_time_enabled"] = not cfg["real_time_enabled"]
		ch.saveConfig()
		
		if cfg["real_time_enabled"]:
			ui.message(_("Real-time on"))
		else:
			ui.message(_("Real-time off"))
		# Stay in layer for more commands
	
	@scriptHandler.script(
		description=_("Clear translation cache for current application"),
		category=_("Polyglot-LLM")
	)
	def script_clearCache(self, gesture):
		"""Clear translation cache for current application."""
		global _cache
		try:
			app_name = globalVars.focusObject.appModule.appName
		except:
			app_name = "__global__"
		
		if _cache:
			_cache.clearApp(app_name)
			ui.message(_("Cache cleared"))
		else:
			ui.message(_("Cache not initialized"))
		# Stay in layer
	
	@scriptHandler.script(
		description=_("Show translation layer help"),
		category=_("Polyglot-LLM")
	)
	def script_layerHelp(self, gesture):
		"""Display help for translation layer commands."""
		help_text = _(
			"T: Translate selection, "
			"Shift+T: Clipboard, "
			"L: Last speech, "
			"C: Copy last, "
			"M: Toggle conversation mode, "
			"R: Toggle real-time, "
			"X: Clear cache, "
			"S: Settings, "
			"Escape: Exit layer"
		)
		ui.message(help_text)
		# Stay in layer
	
	@scriptHandler.script(
		description=_("Exit translation layer"),
		category=_("Polyglot-LLM")
	)
	def script_exitLayer(self, gesture):
		"""Exit the translation layer."""
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
		import tones
		tones.beep(400, 50)
	
	# Layer gestures (active after NVDA+Shift+T)
	__layerGestures = {
		"kb:t": "translateSelection",
		"kb:shift+t": "translateClipboard",
		"kb:l": "translateLastSpoken",
		"kb:c": "copyLastTranslation",
		"kb:m": "toggleConversationMode",
		"kb:r": "toggleRealTimeTranslation",
		"kb:x": "clearCache",
		"kb:s": "announceSettings",
		"kb:h": "layerHelp",
		"kb:escape": "exitLayer",
	}
	
	# Main gestures
	__gestures = {
		"kb:NVDA+shift+t": "activateTranslationLayer",
	}
