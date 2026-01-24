# Translation cache for Polyglot-LLM NVDA add-on
# Copyright (C) 2025, Polyglot-LLM Contributors
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).


import os
import json
import hashlib
import logHandler
import globalVars


log = logHandler.log


class TranslationCache:
	"""
	Manages caching of translations to reduce API calls.
	Uses per-application cache files stored in NVDA config directory.
	"""
	
	def __init__(self):
		self.cache_dir = os.path.join(globalVars.appArgs.configPath, "polyglotLLM_cache")
		self.memory_cache = {}
		self._ensureCacheDir()
	
	def _ensureCacheDir(self):
		"""Create cache directory if it doesn't exist."""
		if not os.path.exists(self.cache_dir):
			try:
				os.makedirs(self.cache_dir)
			except Exception as e:
				log.error(f"Failed to create cache directory: {str(e)}")
	
	def _getCacheKey(self, text, target_language, conversation_mode, conversation_hash=None):
		"""
		Generate cache key for a translation.
		When conversation mode is enabled, includes conversation context hash.
		"""
		if conversation_mode and conversation_hash:
			key_string = f"{text}|{target_language}|{conversation_hash}"
		else:
			key_string = f"{text}|{target_language}"
		
		# Use hash to keep keys manageable
		return hashlib.md5(key_string.encode('utf-8')).hexdigest()
	
	def _getConversationHash(self, conversation_history):
		"""Generate hash of conversation history for cache key."""
		if not conversation_history:
			return None
		
		# Hash the last few messages to create context signature
		context_string = json.dumps(conversation_history[-10:])
		return hashlib.md5(context_string.encode('utf-8')).hexdigest()[:8]
	
	def _getCacheFilePath(self, app_name):
		"""Get path to cache file for specific application."""
		safe_app_name = "".join(c for c in app_name if c.isalnum() or c in "_-")
		return os.path.join(self.cache_dir, f"{safe_app_name}.json")
	
	def get(self, text, target_language, app_name="__global__", conversation_mode=False, conversation_history=None):
		"""
		Retrieve translation from cache.
		Returns cached translation or None if not found.
		"""
		conversation_hash = self._getConversationHash(conversation_history) if conversation_mode else None
		cache_key = self._getCacheKey(text, target_language, conversation_mode, conversation_hash)
		
		# Check memory cache first
		memory_key = f"{app_name}:{cache_key}"
		if memory_key in self.memory_cache:
			log.debug(f"Cache hit (memory) for app: {app_name}")
			return self.memory_cache[memory_key]
		
		# Check disk cache
		cache_file = self._getCacheFilePath(app_name)
		if os.path.exists(cache_file):
			try:
				with open(cache_file, 'r', encoding='utf-8') as f:
					cache_data = json.load(f)
				
				if cache_key in cache_data:
					translation = cache_data[cache_key]
					# Store in memory cache for faster access
					self.memory_cache[memory_key] = translation
					log.debug(f"Cache hit (disk) for app: {app_name}")
					return translation
			except Exception as e:
				log.error(f"Error reading cache file: {str(e)}")
		
		log.debug(f"Cache miss for app: {app_name}")
		return None
	
	def set(self, text, translation, target_language, app_name="__global__", conversation_mode=False, conversation_history=None):
		"""
		Store translation in cache.
		"""
		conversation_hash = self._getConversationHash(conversation_history) if conversation_mode else None
		cache_key = self._getCacheKey(text, target_language, conversation_mode, conversation_hash)
		
		# Store in memory cache
		memory_key = f"{app_name}:{cache_key}"
		self.memory_cache[memory_key] = translation
		
		# Store in disk cache
		cache_file = self._getCacheFilePath(app_name)
		cache_data = {}
		
		# Load existing cache
		if os.path.exists(cache_file):
			try:
				with open(cache_file, 'r', encoding='utf-8') as f:
					cache_data = json.load(f)
			except Exception as e:
				log.error(f"Error reading cache file for update: {str(e)}")
		
		# Add new translation
		cache_data[cache_key] = translation
		
		# Limit cache size (keep last 1000 entries per app)
		if len(cache_data) > 1000:
			# Remove oldest entries (simple approach: keep last 800)
			cache_data = dict(list(cache_data.items())[-800:])
		
		# Save to disk
		try:
			with open(cache_file, 'w', encoding='utf-8') as f:
				json.dump(cache_data, f, ensure_ascii=False, indent=2)
			log.debug(f"Translation cached for app: {app_name}")
		except Exception as e:
			log.error(f"Error writing cache file: {str(e)}")
	
	def clearApp(self, app_name):
		"""Clear cache for specific application."""
		# Clear from memory
		keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{app_name}:")]
		for key in keys_to_remove:
			del self.memory_cache[key]
		
		# Clear from disk
		cache_file = self._getCacheFilePath(app_name)
		if os.path.exists(cache_file):
			try:
				os.remove(cache_file)
				log.info(f"Cache cleared for app: {app_name}")
			except Exception as e:
				log.error(f"Error clearing cache file: {str(e)}")
	
	def clearAll(self):
		"""Clear all caches."""
		# Clear memory cache
		self.memory_cache.clear()
		
		# Clear all disk caches
		if os.path.exists(self.cache_dir):
			try:
				for filename in os.listdir(self.cache_dir):
					if filename.endswith('.json'):
						os.remove(os.path.join(self.cache_dir, filename))
				log.info("All caches cleared")
			except Exception as e:
				log.error(f"Error clearing cache directory: {str(e)}")
