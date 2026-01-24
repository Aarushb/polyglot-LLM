# Quick Start Guide for Developers

## 🚀 Get Started in 5 Minutes

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd polyglot-LLM
```

### 2. Build the Addon

**Option A: Using the build script (recommended)**
```powershell
.\build.ps1
```

**Option B: Manual build**
```bash
pip install -r requirements-build.txt
scons
```

This creates `polyglotLLM-{version}.nvda-addon`

### 3. Install in NVDA

1. Double-click the `.nvda-addon` file
2. NVDA will prompt to install
3. Restart NVDA when prompted

### 4. Configure

1. Open `NVDA menu → Preferences → Settings`
2. Navigate to `Polyglot-LLM` category
3. Enter your Gemini API key ([get one free](https://aistudio.google.com/app/apikey))
4. Select target language (e.g., "Spanish")
5. Click OK

### 5. Test It!

**Translation layer:**
- Press `NVDA+Shift+T` (layer activated - beep sound)
- Press `H` to hear available commands
- Press `S` to hear current settings

**Real-time translation:**
- Press `NVDA+Shift+T` then `R` to toggle real-time on
- Navigate to any text - it will auto-translate
- Press `NVDA+Shift+T` then `R` again to toggle off

**Conversation mode:**
- Press `NVDA+Shift+T` then `M` to toggle conversation mode
- Combine with real-time (`R`) for context-aware live translation

**On-demand translation:**
- Select some text with `Shift+Arrows`
- Press `NVDA+Shift+T` (layer activated)
- Press `T` (translate selected)
- Translation is spoken and copied to clipboard

## 📁 Project Structure

```
polyglot-LLM/
├── addon/
│   └── globalPlugins/
│       └── polyglotLLM/
│           ├── __init__.py           # Main plugin
│           ├── gemini_translator.py  # API integration
│           ├── config_handler.py     # NVDA config system
│           ├── settings_panel.py     # Settings GUI
│           ├── cache.py              # Translation caching
│           └── languages.py          # Language definitions
├── buildVars.py                      # Addon metadata
├── sconstruct                        # Build script
├── manifest.ini.tpl                  # Addon manifest
├── requirements.txt                  # Runtime deps (optional)
├── requirements-build.txt            # Build deps
├── README.md                         # User documentation
├── DEVELOPMENT.md                    # Developer guide
├── STATUS.md                         # Implementation status
└── build.ps1                         # Build helper script
```

## 🔧 Development Workflow

### Making Changes

1. **Edit code** in `addon/globalPlugins/polyglotLLM/`
2. **Rebuild:** Run `scons` or `.\build.ps1`
3. **Reinstall:** Double-click new `.nvda-addon` file
4. **Test in NVDA**
5. **Check logs:** Press `NVDA+Control+F1` → View Log

### Debugging

**Add logging:**
```python
import logHandler
log = logHandler.log

log.debug("Debug message")
log.info("Info message")
log.warning("Warning message")
log.error("Error message", exc_info=True)
```

**View logs:**
- Press `NVDA+Control+F1`
- Click "View Log"
- Look for `[globalPlugins.polyglotLLM]` entries

### Testing Without NVDA

You can test the translator standalone:

```python
import sys
sys.path.insert(0, 'addon/globalPlugins/polyglotLLM')

from gemini_translator import GeminiTranslator

translator = GeminiTranslator(
    api_key="YOUR_API_KEY",
    target_language="Spanish",
    system_prompt="Translate to {target_language}.",
    thinking_budget="low",
    max_tokens=2048
)

result = translator.translate("Hello, how are you?")
print(result)
```

## 🎯 Key Files to Modify

### Changing Translation Behavior

**File:** `gemini_translator.py`

- `DEFAULT_MODEL` - Change AI model
- `DEFAULT_SYSTEM_PROMPT` - Change default prompt
- `_buildPrompt()` - Modify prompt construction
- `translate()` - Core translation logic

### Adding Settings

**File:** `settings_panel.py`

1. Add control in `makeSettings()`
2. Save value in `onSave()`
3. Update config spec in `config_handler.py`

### Modifying Gestures

**File:** `__init__.py`

Look for `__layerGestures` dictionary and `script_*` methods.

**Current layer gestures:**
```python
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
```

**Note:** Users can customize these in NVDA's Input Gestures dialog without editing code.

### Adjusting Cache Behavior

**File:** `cache.py`

- `_getCacheKey()` - How cache keys are generated
- `MAX_ENTRIES` - Cache size limit
- `_saveToDisk()` - Persistence logic

## 📚 Essential Reading

1. **STATUS.md** - Implementation status and testing checklist
2. **DEVELOPMENT.md** - Detailed technical documentation
3. **README.md** - User-facing documentation
4. **.github/copilot-instructions.md** - Original requirements

## 🛠️ Common Tasks

### Change the AI Model

Edit `gemini_translator.py`:
```python
DEFAULT_MODEL = "gemini-3-flash-preview"  # Change this
```

See DEVELOPMENT.md for model options.

### Add a New Language

Edit `languages.py`:
```python
LANGUAGES = [
    ("Your Language Name", "your_language_code"),
    # ...
]
```

### Modify Default Settings

Edit `config_handler.py`:
```python
CONFSPEC = {
    "targetLanguage": "string(default='English')",  # Change default
    # ...
}
```

### Bundle google-genai SDK

See "Bundling Dependencies" section in DEVELOPMENT.md.

## 🐛 Troubleshooting

**Build fails:**
- Check SCons is installed: `scons --version`
- Install build deps: `pip install -r requirements-build.txt`

**Addon won't load in NVDA:**
- Check NVDA log for Python errors
- Verify all files are in correct locations
- Check Python version compatibility (3.9+)

**Imports not resolving (red squiggles):**
- This is normal! NVDA modules only exist when running in NVDA
- Modules like `logHandler`, `gui`, `ui` are NVDA-specific
- Code will work fine when installed in NVDA

**Translation fails:**
- Verify API key is correct
- Check internet connection
- Look for errors in NVDA log
- Test API key with standalone script (see "Testing Without NVDA")

## 📞 Getting Help

1. Check **STATUS.md** for known issues
2. Review **DEVELOPMENT.md** for technical details
3. Search NVDA logs for error messages
4. Review reference addons in `/learn/` folder

## 🎓 Learning Resources

**NVDA Development:**
- [NVDA Developer Guide](https://www.nvaccess.org/files/nvda/documentation/developerGuide.html)
- Reference addons in `/learn/` folder

**Gemini API:**
- [Google AI Documentation](https://ai.google.dev/docs)
- [Gemini API Reference](https://ai.google.dev/api)

---

**Ready to build? Run `.\build.ps1` and you're off! 🚀**
