# Polyglot-LLM Development Guide

## Building the Addon

### Prerequisites

1. **Python 3.9+** (NVDA uses Python 3.11 as of 2024)
2. **Build dependencies:**
   ```bash
   pip install -r requirements-build.txt
   ```

### Build Command

```bash
scons
```

This will create `polyglotLLM-{version}.nvda-addon` in the project root.

## Dependencies

### Runtime Dependencies

The addon requires **no bundled dependencies** to function - it uses only Python standard library for REST API calls.

#### Optional Enhancement: google-genai SDK

For better performance, the addon can optionally use the `google-genai` SDK. If not available, it automatically falls back to REST API.

**Installation (optional):**
```bash
pip install google-genai
```

**Note:** If you want to bundle this with the addon, you would need to:
1. Install google-genai in a separate directory
2. Copy the package to `addon/globalPlugins/polyglotLLM/vendor/`
3. Add path manipulation in __init__.py (see AI Content Describer for example)

For simplicity, the current implementation uses REST API fallback, which works without any bundled dependencies.

## Model Configuration

### Changing the Model

The translator is designed to be easily modified for different Gemini models or even future models.

**In `gemini_translator.py`:**

```python
# Change the default model
DEFAULT_MODEL = "gemini-3-flash-preview"  # Change this

# Available Gemini 3 models:
# - gemini-3-pro-preview (most intelligent, slower)
# - gemini-3-flash-preview (balanced, recommended)

# Gemini 2.5 models (if needed):
# - gemini-2.5-flash
# - gemini-2.5-pro
```

### Thinking Budget

Gemini 3 uses `thinkingLevel` parameter:
- `minimal` - Fastest, minimal reasoning
- `low` - Default, good balance
- `medium` - More reasoning
- `high` - Maximum reasoning (slowest)

Gemini 2.5 uses `thinkingBudget` (token count):
- `0` - No thinking
- `-1` - Dynamic (default)
- `128-32768` - Specific token budget

### Temperature

**Keep temperature at 1.0 for Gemini 3 models** as recommended by Google. Changing it can cause unexpected behavior.

## API Integration

### SDK Mode (Preferred)

When `google-genai` is available:
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=1.0,
        max_output_tokens=2048,
        thinking_config=types.ThinkingConfig(thinking_level="low")
    )
)
```

### REST Mode (Fallback)

When SDK not available:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent" \
  -H "x-goog-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "..."}]}],
    "generationConfig": {
      "temperature": 1.0,
      "maxOutputTokens": 2048,
      "thinkingConfig": {"thinkingLevel": "low"}
    }
  }'
```

## Testing

### Manual Testing

1. Build the addon: `scons`
2. Install in NVDA (double-click the .nvda-addon file)
3. Configure API key in NVDA Preferences → Polyglot-LLM
4. Test real-time mode: `NVDA+Shift+Control+T`
5. Test on-demand mode: `NVDA+Shift+T`, then `T` on selected text

### Testing Without NVDA

You can test the translator standalone:

```python
import sys
sys.path.insert(0, 'addon/globalPlugins/polyglotLLM')

from gemini_translator import GeminiTranslator

translator = GeminiTranslator(
    api_key="YOUR_API_KEY",
    target_language="Spanish",
    system_prompt="Translate to {target_language}. Output only the translation.",
    thinking_budget="low",
    max_tokens=2048
)

result = translator.translate("Hello, how are you?")
print(result)
```

## Architecture

### Main Components

1. **`__init__.py`** - Main plugin, hooks NVDA speech, handles gestures
2. **`gemini_translator.py`** - API integration (SDK + REST)
3. **`config_handler.py`** - NVDA config system integration
4. **`settings_panel.py`** - Settings GUI
5. **`cache.py`** - Translation caching system
6. **`languages.py`** - Language definitions

### Translation Flow

#### Real-Time Mode:
```
NVDA speech → _speak() → Check cache → Translate → Update cache → Speak translated
```

#### On-Demand Mode:
```
User gesture → Get text → AsyncTranslator → Translate in thread → Announce result
```

### Conversation Mode

When enabled:
1. Stores last N translations in `conversation_history`
2. Includes history in prompt for context
3. Cache keys include conversation hash
4. Better for multi-turn conversations

When disabled:
- Faster (no context overhead)
- Lower API costs
- Each translation independent

## Future Improvements

### Supporting New Models

To add a new model provider (e.g., Claude, GPT):

1. Create new translator class (e.g., `claude_translator.py`)
2. Implement same interface as `GeminiTranslator`
3. Update settings panel with model selection dropdown
4. Initialize appropriate translator in `__init__.py`

### Bundling Dependencies

If you want to bundle `google-genai`:

1. Create `addon/globalPlugins/polyglotLLM/vendor/` directory
2. Install package: `pip install google-genai -t vendor/`
3. Add to `__init__.py`:
   ```python
   vendor_path = os.path.join(os.path.dirname(__file__), "vendor")
   if os.path.exists(vendor_path):
       sys.path.insert(0, vendor_path)
   ```

### Streaming Support

The API supports streaming, but for NVDA use:
- Real-time mode: Synchronous translation (wait for full result)
- On-demand mode: Async but still wait for full result

Streaming would complicate speech output without much benefit.

## Troubleshooting

### "Translation failed" errors

1. Check NVDA log: `NVDA+Control+F1` → View Log
2. Look for error details from `gemini_translator.py`
3. Common issues:
   - Invalid API key
   - Network connection
   - Rate limits
   - Model not available

### Addon won't load

1. Check Python version compatibility
2. Check NVDA log for import errors
3. Verify all required files are in `addon/globalPlugins/polyglotLLM/`

### Slow translations

1. Use `minimal` or `low` thinking level
2. Enable caching (default)
3. Check network latency
4. Consider using Gemini 3 Flash instead of Pro

## Contributing

When modifying:

1. Follow NVDA coding conventions (tabs, camelCase for functions)
2. Add logging for debugging: `log.debug()`, `log.error()`
3. Test both SDK and REST modes
4. Test with and without conversation mode
5. Commit frequently with descriptive messages
6. Don't push - maintainer will handle releases

## License

GPL v2 - See LICENSE file
