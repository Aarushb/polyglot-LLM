# Settings panel for Polyglot-LLM NVDA add-on
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).


import wx
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel
import addonHandler
from . import config_handler as ch
from . import languages


addonHandler.initTranslation()


class PolyglotLLMSettingsPanel(SettingsPanel):
	# Translators: The label for the category in NVDA settings
	title = _("Polyglot-LLM")
	
	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		
		# API Key
		# Translators: Label for API key field
		self.api_key_text = sHelper.addLabeledControl(_("Google Gemini API &Key:"), wx.TextCtrl)
		
		# Target Language
		# Translators: Label for target language dropdown
		language_list = languages.getLanguageList()
		language_choices = [name for code, name in language_list]
		self.language_codes = [code for code, name in language_list]
		self.target_language = sHelper.addLabeledControl(_("&Target Language:"), wx.Choice, choices=language_choices)
		
		# System Prompt
		# Translators: Label for system prompt
		system_prompt_label = wx.StaticText(self, label=_("System &Prompt (advanced):"))
		sHelper.sizer.Add(system_prompt_label)
		self.system_prompt = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(400, 100))
		sHelper.sizer.Add(self.system_prompt, flag=wx.EXPAND)
		
		# Conversation Mode
		# Translators: Label for conversation mode checkbox
		self.conversation_mode = sHelper.addItem(wx.CheckBox(self, label=_("Enable &conversation mode (context-aware)")))
		
		# Conversation History Length
		# Translators: Label for conversation history length
		self.history_length = sHelper.addLabeledControl(
			_("Conversation history &length (messages):"),
			wx.SpinCtrl,
			min=5,
			max=20
		)
		
		# Thinking Budget
		# Translators: Label for thinking budget
		thinking_choices = ["minimal", "low", "medium", "high"]
		self.thinking_budget = sHelper.addLabeledControl(_("Thinking &budget:"), wx.Choice, choices=thinking_choices)
		
		# Max Tokens
		# Translators: Label for max tokens
		self.max_tokens = sHelper.addLabeledControl(
			_("Ma&x tokens:"),
			wx.SpinCtrl,
			min=256,
			max=8192
		)
		
		# Cache Translations
		# Translators: Label for cache translations checkbox
		self.cache_translations = sHelper.addItem(wx.CheckBox(self, label=_("&Cache translations to reduce API calls")))
		
		# Copy Translations
		# Translators: Label for copy translations checkbox
		self.copy_translations = sHelper.addItem(wx.CheckBox(self, label=_("C&opy translations to clipboard")))
		
		self.populateValues()
	
	def populateValues(self):
		"""Populate controls with current settings."""
		cfg = ch.getConfig()
		
		# API Key
		self.api_key_text.SetValue(cfg["api_key"])
		
		# Target Language
		target_lang = cfg["target_language"]
		if target_lang in self.language_codes:
			self.target_language.SetSelection(self.language_codes.index(target_lang))
		else:
			self.target_language.SetSelection(0)
		
		# System Prompt
		self.system_prompt.SetValue(cfg["system_prompt"])
		
		# Conversation Mode
		self.conversation_mode.SetValue(cfg["conversation_mode"])
		
		# History Length
		self.history_length.SetValue(cfg["conversation_history_length"])
		
		# Thinking Budget
		thinking_budget = cfg["thinking_budget"]
		thinking_choices = ["minimal", "low", "medium", "high"]
		if thinking_budget in thinking_choices:
			self.thinking_budget.SetSelection(thinking_choices.index(thinking_budget))
		else:
			self.thinking_budget.SetSelection(1)  # Default to "low"
		
		# Max Tokens
		self.max_tokens.SetValue(cfg["max_tokens"])
		
		# Cache Translations
		self.cache_translations.SetValue(cfg["cache_translations"])
		
		# Copy Translations
		self.copy_translations.SetValue(cfg["copy_translations"])
	
	def onSave(self):
		"""Save settings when user clicks OK."""
		cfg = ch.getConfig()
		
		# API Key
		cfg["api_key"] = self.api_key_text.GetValue()
		
		# Target Language
		selection = self.target_language.GetSelection()
		if selection != wx.NOT_FOUND:
			cfg["target_language"] = self.language_codes[selection]
		
		# System Prompt
		cfg["system_prompt"] = self.system_prompt.GetValue()
		
		# Conversation Mode
		cfg["conversation_mode"] = self.conversation_mode.GetValue()
		
		# History Length
		cfg["conversation_history_length"] = self.history_length.GetValue()
		
		# Thinking Budget
		thinking_choices = ["minimal", "low", "medium", "high"]
		selection = self.thinking_budget.GetSelection()
		if selection != wx.NOT_FOUND:
			cfg["thinking_budget"] = thinking_choices[selection]
		
		# Max Tokens
		cfg["max_tokens"] = self.max_tokens.GetValue()
		
		# Cache Translations
		cfg["cache_translations"] = self.cache_translations.GetValue()
		
		# Copy Translations
		cfg["copy_translations"] = self.copy_translations.GetValue()
		
		# Save to disk
		ch.saveConfig()
	
	def postSave(self):
		"""Called after settings are saved. Reinitialize translator with new settings."""
		# Get the global plugin instance and reinitialize translator
		import globalPluginHandler
		for plugin in globalPluginHandler.runningPlugins:
			if plugin.__class__.__name__ == "GlobalPlugin" and hasattr(plugin, '_initializeTranslator'):
				plugin._initializeTranslator()
				break
