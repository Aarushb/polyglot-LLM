# Gemini API translator for Polyglot-LLM NVDA add-on
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).


import threading
import logHandler
from typing import Optional, Callable, List, Dict


log = logHandler.log


# Check if google-genai is available, fallback to REST if not
try:
	from google import genai
	from google.genai import types
	HAS_GOOGLE_GENAI = True
except ImportError:
	HAS_GOOGLE_GENAI = False
	log.warning("google-genai not available, will use REST API")
	import json
	import urllib.request
	import urllib.error


class GeminiTranslator:
	"""
	Translator using Google Gemini API.
	Supports both google-genai SDK and REST fallback.
	Designed to be easily modifiable for different models.
	"""
	
	# Model configuration - easily changeable
	DEFAULT_MODEL = "gemini-3-flash-preview"
	TEMPERATURE = 1.0  # Keep at 1.0 for Gemini 3 as recommended
	
	# Thinking level mapping for Gemini 3
	THINKING_LEVELS = {
		"minimal": "minimal",
		"low": "low",
		"medium": "medium",
		"high": "high"
	}
	
	def __init__(self, api_key: str, target_language: str, system_prompt: str, 
	             thinking_budget: str = "low", max_tokens: int = 2048, 
	             model: str = None):
		"""
		Initialize the Gemini translator.
		
		Args:
			api_key: Google Gemini API key
			target_language: Target language name (e.g., "Spanish", "French")
			system_prompt: System instruction for the model
			thinking_budget: Thinking level/budget ("minimal", "low", "medium", "high")
			max_tokens: Maximum output tokens
			model: Model name (defaults to gemini-3-flash-preview)
		"""
		self.api_key = api_key
		self.target_language = target_language
		self.system_prompt = system_prompt
		self.thinking_budget = thinking_budget
		self.max_tokens = max_tokens
		self.model = model or self.DEFAULT_MODEL
		
		# Conversation history for context-aware translation
		self.conversation_history: List[Dict[str, str]] = []
		
		# Initialize client if SDK available
		if HAS_GOOGLE_GENAI:
			try:
				self.client = genai.Client(api_key=api_key)
				log.info(f"Gemini translator initialized with {self.model}")
			except Exception as e:
				log.error(f"Failed to initialize Gemini client: {str(e)}")
				self.client = None
		else:
			self.client = None
			log.info("Using REST API for Gemini")
	
	def translate(self, text: str, use_conversation_mode: bool = False) -> Optional[str]:
		"""
		Translate text synchronously.
		
		Args:
			text: Text to translate
			use_conversation_mode: Whether to include conversation history
		
		Returns:
			Translated text or None if translation fails
		"""
		if not text or not text.strip():
			return None
		
		if not self.api_key:
			log.error("No API key configured")
			return None
		
		# Build the prompt with system instruction and conversation context
		prompt = self._buildPrompt(text, use_conversation_mode)
		
		try:
			if HAS_GOOGLE_GENAI and self.client:
				translated = self._translateWithSDK(prompt)
			else:
				translated = self._translateWithREST(prompt)
			
			# Update conversation history if in conversation mode
			if use_conversation_mode and translated:
				self._addToHistory(text, translated)
			
			return translated
		
		except Exception as e:
			log.error(f"Translation failed: {str(e)}", exc_info=True)
			return None
	
	def _buildPrompt(self, text: str, use_conversation_mode: bool) -> str:
		"""Build the complete prompt with system instruction and history."""
		# Format system prompt with target language
		formatted_prompt = self.system_prompt.format(target_language=self.target_language)
		
		prompt_parts = [formatted_prompt]
		
		# Add conversation history if enabled
		if use_conversation_mode and self.conversation_history:
			prompt_parts.append("\n\nPrevious conversation context:")
			for entry in self.conversation_history[-10:]:  # Last 10 messages
				prompt_parts.append(f"Original: {entry['original']}")
				prompt_parts.append(f"Translated: {entry['translated']}")
		
		# Add current text to translate
		prompt_parts.append(f"\n\nText to translate:\n{text}")
		
		return "\n".join(prompt_parts)
	
	def _translateWithSDK(self, prompt: str) -> Optional[str]:
		"""Translate using google-genai SDK."""
		try:
			# Map thinking budget to thinking level for Gemini 3
			thinking_level = self.THINKING_LEVELS.get(self.thinking_budget, "low")
			
			config = types.GenerateContentConfig(
				temperature=self.TEMPERATURE,
				max_output_tokens=self.max_tokens,
				thinking_config=types.ThinkingConfig(thinking_level=thinking_level)
			)
			
			response = self.client.models.generate_content(
				model=self.model,
				contents=prompt,
				config=config
			)
			
			if response and response.text:
				return response.text.strip()
			else:
				log.error("Empty response from Gemini API")
				return None
		
		except Exception as e:
			log.error(f"SDK translation error: {str(e)}", exc_info=True)
			return None
	
	def _translateWithREST(self, prompt: str) -> Optional[str]:
		"""Translate using REST API as fallback."""
		try:
			# Map thinking budget to thinking level
			thinking_level = self.THINKING_LEVELS.get(self.thinking_budget, "low")
			
			url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
			
			headers = {
				"x-goog-api-key": self.api_key,
				"Content-Type": "application/json"
			}
			
			data = {
				"contents": [{
					"parts": [{"text": prompt}]
				}],
				"generationConfig": {
					"temperature": self.TEMPERATURE,
					"maxOutputTokens": self.max_tokens,
					"thinkingConfig": {
						"thinkingLevel": thinking_level
					}
				}
			}
			
			req = urllib.request.Request(
				url,
				data=json.dumps(data).encode('utf-8'),
				headers=headers,
				method='POST'
			)
			
			with urllib.request.urlopen(req, timeout=30) as response:
				result = json.loads(response.read().decode('utf-8'))
				
				if 'candidates' in result and len(result['candidates']) > 0:
					candidate = result['candidates'][0]
					if 'content' in candidate and 'parts' in candidate['content']:
						parts = candidate['content']['parts']
						if len(parts) > 0 and 'text' in parts[0]:
							return parts[0]['text'].strip()
			
			log.error("Unexpected response structure from REST API")
			return None
		
		except urllib.error.HTTPError as e:
			log.error(f"HTTP error {e.code}: {e.reason}")
			return None
		except urllib.error.URLError as e:
			log.error(f"URL error: {str(e.reason)}")
			return None
		except Exception as e:
			log.error(f"REST translation error: {str(e)}", exc_info=True)
			return None
	
	def _addToHistory(self, original: str, translated: str):
		"""Add translation to conversation history."""
		self.conversation_history.append({
			"original": original,
			"translated": translated
		})
		
		# Keep only last 20 entries to prevent memory issues
		if len(self.conversation_history) > 20:
			self.conversation_history = self.conversation_history[-20:]
	
	def clearConversationHistory(self):
		"""Clear the conversation history."""
		self.conversation_history.clear()
		log.debug("Conversation history cleared")
	
	def updateSettings(self, api_key: str = None, target_language: str = None, 
	                   system_prompt: str = None, thinking_budget: str = None, 
	                   max_tokens: int = None, model: str = None):
		"""
		Update translator settings dynamically.
		Useful when user changes settings without restarting NVDA.
		"""
		if api_key:
			self.api_key = api_key
			# Reinitialize client with new API key
			if HAS_GOOGLE_GENAI:
				try:
					self.client = genai.Client(api_key=api_key)
				except Exception as e:
					log.error(f"Failed to reinitialize client: {str(e)}")
		
		if target_language:
			self.target_language = target_language
		
		if system_prompt:
			self.system_prompt = system_prompt
		
		if thinking_budget:
			self.thinking_budget = thinking_budget
		
		if max_tokens:
			self.max_tokens = max_tokens
		
		if model:
			self.model = model
			log.info(f"Model changed to: {model}")


class AsyncTranslator:
	"""
	Wrapper for asynchronous translation operations.
	Runs translations in background threads to avoid blocking NVDA.
	Includes request queue management to prevent flooding.
	"""
	
	def __init__(self, translator: GeminiTranslator):
		"""
		Initialize async translator.
		
		Args:
			translator: GeminiTranslator instance to use
		"""
		self.translator = translator
		self.pending_requests = {}  # Track pending requests by ID
		self.request_counter = 0
		self._lock = threading.Lock()
	
	def translate(self, text: str, use_conversation_mode: bool, 
	              on_success: Callable[[str], None], 
	              on_error: Callable[[str], None],
	              request_type: str = "on_demand",
	              cancel_previous: bool = False) -> int:
		"""
		Translate text asynchronously with queue management.
		
		Args:
			text: Text to translate
			use_conversation_mode: Whether to use conversation history
			on_success: Callback function called with translated text
			on_error: Callback function called with error message
			request_type: Type of request ("real_time" or "on_demand")
			cancel_previous: If True, cancel previous requests of same type
		
		Returns:
			Request ID for tracking
		"""
		with self._lock:
			self.request_counter += 1
			request_id = self.request_counter
			
			# Cancel previous requests of same type if requested
			if cancel_previous:
				for rid, req_info in list(self.pending_requests.items()):
					if req_info["type"] == request_type:
						req_info["cancelled"] = True
						log.debug(f"Cancelled request {rid} (type: {request_type})")
			
			# Register this request
			self.pending_requests[request_id] = {
				"type": request_type,
				"cancelled": False,
				"text": text
			}
		
		def _translate_thread():
			try:
				# Check if cancelled before starting
				with self._lock:
					if self.pending_requests.get(request_id, {}).get("cancelled", False):
						log.debug(f"Skipping cancelled request {request_id}")
						return
				
				result = self.translator.translate(text, use_conversation_mode)
				
				# Check if cancelled after translation
				with self._lock:
					if self.pending_requests.get(request_id, {}).get("cancelled", False):
						log.debug(f"Discarding result for cancelled request {request_id}")
						return
				
				if result:
					on_success(result)
				else:
					on_error("Translation returned empty result")
			except Exception as e:
				log.error(f"Async translation error: {str(e)}", exc_info=True)
				with self._lock:
					if not self.pending_requests.get(request_id, {}).get("cancelled", False):
						on_error(str(e))
			finally:
				# Clean up request tracking
				with self._lock:
					self.pending_requests.pop(request_id, None)
		
		thread = threading.Thread(target=_translate_thread, daemon=True)
		thread.start()
		return request_id
	
	def cancel_all(self, request_type: str = None):
		"""
		Cancel all pending requests, optionally filtered by type.
		
		Args:
			request_type: If specified, only cancel requests of this type
		"""
		with self._lock:
			for rid, req_info in list(self.pending_requests.items()):
				if request_type is None or req_info["type"] == request_type:
					req_info["cancelled"] = True
					log.debug(f"Cancelled request {rid}")
	
	def get_pending_count(self, request_type: str = None) -> int:
		"""
		Get count of pending requests.
		
		Args:
			request_type: If specified, only count requests of this type
		
		Returns:
			Number of pending requests
		"""
		with self._lock:
			if request_type is None:
				return len([r for r in self.pending_requests.values() if not r["cancelled"]])
			else:
				return len([r for r in self.pending_requests.values() 
				           if r["type"] == request_type and not r["cancelled"]])
