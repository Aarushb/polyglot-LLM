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
	
	def _translateAsync(self, text, callback_message=None):
		"""Translate text asynchronously and announce result."""
		global _async_translator, _cache
		
		if not _translator:
			ui.message(_("Translation not configured. Please set API key in settings."))
			return
		
		if not text or not text.strip():
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
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, translated_text)
			if cfg["copy_translations"]:
				queueHandler.queueFunction(queueHandler.eventQueue, api.copyToClip, translated_text)
		
		def on_error(error_msg):
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Translation failed"))
		
		_async_translator.translate(text, conversation_mode, on_success, on_error)
	
	# Real-Time Translation Mode Scripts
	
	@scriptHandler.script(
		description=_("Toggle real-time translation mode"),
		gesture="kb:NVDA+shift+control+t"
	)
	def script_toggleRealTimeTranslation(self, gesture):
		"""Toggle real-time translation on/off."""
		cfg = ch.getConfig()
		cfg["real_time_enabled"] = not cfg["real_time_enabled"]
		ch.saveConfig()
		
		if cfg["real_time_enabled"]:
			ui.message(_("Real-time translation enabled"))
		else:
			ui.message(_("Real-time translation disabled"))
	
	# On-Demand Translation Mode Scripts (Layer)
	
	@scriptHandler.script(
		description=_("Activate instant translate layer"),
		gesture="kb:NVDA+shift+t"
	)
	def script_instantTranslateLayer(self, gesture):
		"""Activate the instant translate layer."""
		# Bind layer gestures
		self.bindGestures(self.__ITGestures)
		ui.message(_("Instant translate"))
	
	@scriptHandler.script(
		description=_("Translate selected text")
	)
	def script_translateSelection(self, gesture):
		"""Translate selected text."""
		text = self._getSelectedText()
		if not text:
			ui.message(_("No selection"))
			return
		self._translateAsync(text)
		# Clear layer
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Translate clipboard text")
	)
	def script_translateClipboard(self, gesture):
		"""Translate clipboard content."""
		try:
			text = api.getClipData()
		except:
			text = None
		
		if not text or not isinstance(text, str) or text.isspace():
			ui.message(_("Clipboard is empty"))
			return
		
		self._translateAsync(text)
		# Clear layer
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Translate last spoken text")
	)
	def script_translateLastSpoken(self, gesture):
		"""Translate the last spoken text."""
		if self.lastSpokenText:
			self._translateAsync(self.lastSpokenText)
		else:
			ui.message(_("No last spoken text"))
		# Clear layer
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Copy last translation to clipboard")
	)
	def script_copyLastTranslation(self, gesture):
		"""Copy last translation to clipboard."""
		if self.lastTranslation:
			api.copyToClip(self.lastTranslation)
			ui.message(_("Translation copied to clipboard"))
		else:
			ui.message(_("No translation to copy"))
		# Clear layer
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Announce current language configuration")
	)
	def script_announceLanguages(self, gesture):
		"""Announce current language configuration."""
		cfg = ch.getConfig()
		target_lang = languages.getLanguageName(cfg["target_language"])
		ui.message(_("Translating to {language}").format(language=target_lang))
		# Clear layer
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Toggle conversation mode")
	)
	def script_toggleConversationMode(self, gesture):
		"""Toggle conversation mode."""
		cfg = ch.getConfig()
		cfg["conversation_mode"] = not cfg["conversation_mode"]
		ch.saveConfig()
		
		if cfg["conversation_mode"]:
			ui.message(_("Conversation mode enabled"))
		else:
			# Clear conversation history
			if _translator:
				_translator.clearConversationHistory()
			ui.message(_("Conversation mode disabled"))
		# Clear layer
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	@scriptHandler.script(
		description=_("Clear conversation history")
	)
	def script_clearConversationHistory(self, gesture):
		"""Clear the conversation history."""
		if _translator:
			_translator.clearConversationHistory()
			ui.message(_("Conversation history cleared"))
		else:
			ui.message(_("Translator not initialized"))
		# Clear layer
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
	
	# Layer gestures (active after NVDA+Shift+T)
	__ITGestures = {
		"kb:t": "translateSelection",
		"kb:shift+t": "translateClipboard",
		"kb:l": "translateLastSpoken",
		"kb:c": "copyLastTranslation",
		"kb:a": "announceLanguages",
		"kb:v": "toggleConversationMode",
		"kb:h": "clearConversationHistory",
	}
	
	# Main gestures
	__gestures = {
		"kb:NVDA+shift+control+t": "toggleRealTimeTranslation",
		"kb:NVDA+shift+t": "instantTranslateLayer",
	}
