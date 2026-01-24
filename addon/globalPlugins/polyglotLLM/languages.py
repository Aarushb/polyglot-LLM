# Language list for Polyglot-LLM NVDA add-on
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).

# Common languages supported for translation
LANGUAGES = {
	"en": "English",
	"es": "Spanish",
	"fr": "French",
	"de": "German",
	"it": "Italian",
	"pt": "Portuguese",
	"ru": "Russian",
	"ja": "Japanese",
	"zh": "Chinese (Simplified)",
	"zh-TW": "Chinese (Traditional)",
	"ko": "Korean",
	"ar": "Arabic",
	"hi": "Hindi",
	"nl": "Dutch",
	"pl": "Polish",
	"tr": "Turkish",
	"sv": "Swedish",
	"da": "Danish",
	"fi": "Finnish",
	"no": "Norwegian",
	"cs": "Czech",
	"el": "Greek",
	"he": "Hebrew",
	"th": "Thai",
	"vi": "Vietnamese",
	"id": "Indonesian",
	"ms": "Malay",
	"uk": "Ukrainian",
	"ro": "Romanian",
	"hu": "Hungarian",
	"sk": "Slovak",
	"bg": "Bulgarian",
	"hr": "Croatian",
	"sr": "Serbian",
	"sl": "Slovenian",
	"lt": "Lithuanian",
	"lv": "Latvian",
	"et": "Estonian",
}


def getLanguageName(code):
	"""Get the display name for a language code."""
	return LANGUAGES.get(code, code)


def getLanguageList():
	"""Get a sorted list of (code, name) tuples."""
	return sorted(LANGUAGES.items(), key=lambda x: x[1])
