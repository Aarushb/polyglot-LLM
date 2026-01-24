# Gemini API integration for Polyglot-LLM NVDA add-on
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).


import json
import threading
import logHandler
try:
	from urllib import request, error
except ImportError:
	import urllib2 as request
	import urllib2 as error


log = logHandler.log


class GeminiTranslator:
	"""Handles translation via Google Gemini API."""
	
	BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
	
	def __init__(self, api_key, target_language, system_prompt, thinking_budget="low", max_tokens=2048):
		self.api_key = api_key
		self.target_language = target_language
		self.system_prompt = system_prompt
		self.thinking_budget = thinking_budget
		self.max_tokens = max_tokens
		self.conversation_history = []
	
	def translate(self, text, use_conversation_history=False):
		"""
		Translate text using Gemini API.
		Returns translated text or None on error.
		"""
		if not self.api_key:
			log.error("Gemini API key not configured")
			return None
		
		if not text or not text.strip():
			return text
		
		# Build prompt with conversation history if enabled
		prompt = self._buildPrompt(text, use_conversation_history)
		
		# Prepare API request
		url = f"{self.BASE_URL}?key={self.api_key}"
		headers = {
			"Content-Type": "application/json"
		}
		
		# Build request body
		body = {
			"contents": [{
				"parts": [{
					"text": prompt
				}]
			}],
			"generationConfig": {
				"temperature": 0.3,
				"maxOutputTokens": self.max_tokens,
			}
		}
		
		# Add thinking budget if supported (research exact parameter name)
		# Note: This may need adjustment based on Gemini API documentation
		if self.thinking_budget:
			body["generationConfig"]["thinkingBudget"] = self.thinking_budget
		
		try:
			req = request.Request(
				url,
				data=json.dumps(body).encode('utf-8'),
				headers=headers
			)
			
			log.debug(f"Sending translation request to Gemini API")
			response = request.urlopen(req, timeout=30)
			response_data = json.loads(response.read().decode('utf-8'))
			
			# Extract translated text from response
			if "candidates" in response_data and len(response_data["candidates"]) > 0:
				candidate = response_data["candidates"][0]
				if "content" in candidate and "parts" in candidate["content"]:
					translated_text = candidate["content"]["parts"][0]["text"].strip()
					
					# Update conversation history if enabled
					if use_conversation_history:
						self._updateConversationHistory(text, translated_text)
					
					log.debug(f"Translation successful")
					return translated_text
			
			log.error("Unexpected response format from Gemini API")
			return None
			
		except error.HTTPError as e:
			log.error(f"HTTP error during translation: {e.code} - {e.reason}")
			return None
		except error.URLError as e:
			log.error(f"URL error during translation: {e.reason}")
			return None
		except Exception as e:
			log.error(f"Error during translation: {str(e)}", exc_info=True)
			return None
	
	def _buildPrompt(self, text, use_conversation_history):
		"""Build the prompt to send to Gemini."""
		prompt = self.system_prompt.format(target_language=self.target_language)
		
		if use_conversation_history and self.conversation_history:
			prompt += "\n\nPrevious conversation context:\n"
			for entry in self.conversation_history:
				prompt += f"{entry['role']}: {entry['text']}\n"
		
		prompt += f"\n\nText to translate:\n{text}"
		return prompt
	
	def _updateConversationHistory(self, original, translated):
		"""Update the conversation history with the latest exchange."""
		self.conversation_history.append({
			"role": "user",
			"text": original
		})
		self.conversation_history.append({
			"role": "assistant",
			"text": translated
		})
	
	def clearConversationHistory(self):
		"""Clear the conversation history."""
		self.conversation_history = []
	
	def setConversationHistoryLength(self, length):
		"""Limit conversation history to specified length."""
		if len(self.conversation_history) > length * 2:  # *2 because each exchange has 2 entries
			self.conversation_history = self.conversation_history[-(length * 2):]


class AsyncTranslator:
	"""Handles asynchronous translation requests."""
	
	def __init__(self, translator):
		self.translator = translator
		self.callback = None
		self.error_callback = None
	
	def translate(self, text, use_conversation_history=False, callback=None, error_callback=None):
		"""Translate text asynchronously."""
		self.callback = callback
		self.error_callback = error_callback
		
		thread = threading.Thread(
			target=self._translateWorker,
			args=(text, use_conversation_history)
		)
		thread.daemon = True
		thread.start()
	
	def _translateWorker(self, text, use_conversation_history):
		"""Worker thread for translation."""
		try:
			result = self.translator.translate(text, use_conversation_history)
			if result is not None and self.callback:
				self.callback(result)
			elif result is None and self.error_callback:
				self.error_callback("Translation failed")
		except Exception as e:
			log.error(f"Error in translation worker: {str(e)}", exc_info=True)
			if self.error_callback:
				self.error_callback(str(e))
