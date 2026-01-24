# Polyglot-LLM: NVDA AI Translation Addon

## 🎯 Project Goal

Create an NVDA addon that combines real-time translation and on-demand translation using **AI/LLM for context-aware translations**. This enables seamless communication between blind screen reader users speaking different languages.

**Why AI?** Context-aware translation (unlike Google Translate/DeepL) produces better results by understanding conversation flow, slang, and nuance.

---

## 📚 Learn from Existing Addons

**Three complete addon source codes are in `/learn/` folder:**

1. **AI Content Describer** - Shows how to integrate LLM APIs (Gemini, GPT, Claude) into NVDA
2. **Instant Translate** - Layer-based translation (NVDA+Shift+T, then single keys)
3. **Translate** - Real-time automatic translation of all NVDA speech

**CRITICAL: Copy extensively from these.** NVDA addon development is niche with limited docs. These working examples are your primary reference. Don't reinvent—adapt what already works.

---

## 🛠️ Technical Stack

**Language:** Python (NVDA's Python environment, not standard)  
**LLM Provider:** Google Gemini 3 Flash (lowest thinking budget)  
**Build Tool:** SCons (like AI Content Describer)  
**Settings Storage:** NVDA config system (NOT .env files)  
**Development:** Use `uv` for isolated venv if needed for testing  

---

## ✨ Core Features

### 1. Two Translation Modes

#### Mode A: Real-Time Translation (from Translate addon)
- **Behavior:** Translates all NVDA speech automatically
- **Use case:** Live chat, conversations, streaming content
- **Activation:** NVDA+Shift+Control+T (toggle on/off)
- **Tradeoff:** Slight delay as speech waits for translation

#### Mode B: On-Demand Translation (from Instant Translate addon)
- **Behavior:** Keyboard layer for selective translation
- **Use case:** Non-urgent translation (clipboard, selected text, last speech)
- **Activation:** NVDA+Shift+T (layer), then:
  - `T` - Translate selected text
  - `Shift+T` - Translate clipboard
  - `L` - Translate last spoken text
  - `C` - Copy last translation to clipboard
  - `A` - Announce current language config
  - `S` - Swap source/target languages

### 2. Conversation Mode (NEW FEATURE)

**Toggle:** Available in both modes via settings or gesture  
**Purpose:** Maintain conversation history for context-aware translation

**When ENABLED:**
- Stores last N messages (configurable, default 10)
- Sends conversation history to LLM with each translation
- LLM understands context: pronouns, topic continuity, tone

**When DISABLED:**
- Clears conversation history
- Translates each message independently (faster, less context)

**Example:**
```
User A (English): "I love that movie"
User B (Spanish): "¿Cuál?" 
Without context → "Which?"
With context → "Which movie?"
```

### 3. Language Configuration

**Settings Panel (NVDA Preferences → Polyglot-LLM):**
- Target language (required - what to translate into)
- API key (Gemini)
- System prompt (customizable for advanced users)
- Conversation mode toggle
- Conversation history length (5-20 messages)
- Thinking budget (Minimal/Low/Medium/High - research Gemini 3 Flash options)
- Max tokens (default: 2048 - allows paragraph-length text, configurable)

**Note:** Source language auto-detected by AI (not configurable).

---

## 🤖 LLM Integration

### Model: Google Gemini 3 Flash

**Why Gemini Flash?**
- Fast (low latency for real-time)
- Cheap (lowest cost per token)
- Good enough quality for translation
- Supports thinking budget configuration

**Thinking Budget:**
Research Gemini 3 Flash preview parameters for thinking modes:
- Options: `minimal`, `low`, `medium`, `high` (or similar)
- Use **minimal** or **low** by default (translation doesn't need deep reasoning)
- Make configurable in settings for advanced users

**System Prompt (Customizable in Settings):**

Default:
```
You are a professional translator. Automatically detect the source language of the input text and translate it to {target_language}. 

Respond ONLY with the translated text. Do not include the source language name, explanations, notes, or any other content.

{if conversation_mode}
Previous conversation context:
{conversation_history}
{endif}

Text to translate:
{input_text}
```

**API Parameters:**
- Temperature: 0.3 (consistency over creativity)
- Thinking budget: Minimal/Low (configurable)
- Max tokens: 2048 (allows paragraphs, configurable)
  - **Note:** Not designed for translating long documents
  - If text exceeds max tokens, show error: "Text too long. Please translate in smaller chunks."

### Conversation History Format

```python
# Example structure
conversation_history = [
    {"role": "user", "text": "Hello", "translated": "Hola"},
    {"role": "assistant", "text": "Hola", "original": "Hello"},
    # ... last N messages
]

# When sending to LLM:
context = "\n".join([f"{msg['role']}: {msg['text']}" for msg in conversation_history[-10:]])
```

---

## 📋 Implementation Guide

### Study These Files from `/learn/`:

**From AI Content Describer:**
- How to store API keys in NVDA settings
- How to make async LLM calls
- How to handle API errors gracefully
- Settings panel structure
- Build configuration (buildVars.py, sconstruct)

**From Instant Translate:**
- Keyboard layer implementation (NVDA+Shift+T)
- Language detection and swapping
- Clipboard translation
- Selected text translation
- Settings dialog for languages

**From Translate:**
- Real-time speech interception
- Caching translated text (for performance)
- Toggle gesture implementation
- Integration with NVDA's speech system

### Key NVDA Concepts

**Settings Storage:**
```python
# DON'T use .env or config files
# DO use NVDA's config system (see AI Content Describer)
config.conf["aiTranslator"]["apiKey"] = "..."
config.conf["aiTranslator"]["targetLanguage"] = "es"
```

**Speech Interception (Real-Time Mode):**
```python
# Hook NVDA's speech.speak function
# Translate before speech output
# See Translate addon for exact implementation
```

**Gestures:**
```python
# Define in __init__.py or globalPlugin file
__gestures = {
    "kb:NVDA+shift+control+t": "toggleRealTimeTranslation",
    "kb:NVDA+shift+t": "instantTranslateLayer",
}
```

**Caching:**
```python
# Smart caching to reduce API calls and improve speed
# Cache structure: Per-application or global (research best approach)

# Option A: String-based cache (simple)
cache = {
    "Hello": "Hola",
    "How are you?": "¿Cómo estás?"
}

# Option B: Context-aware cache
# Consider conversation mode - same string may have different translations in different contexts
# If conversation mode OFF: Cache by string only
# If conversation mode ON: Cache by (string + conversation_hash)

# Cache storage:
# - Per-application cache files (like Translate addon)
# - Store in NVDA config directory
# - Clear cache commands (per-app, all apps)

# Research best caching strategy:
# - Linguistic context: Same string can mean different things
# - Balance cache hits vs. storage size
# - Invalidation strategy (time-based? manual?)
```

---

## 🎨 User Experience

### First-Time Setup

1. Install addon
2. NVDA Preferences → Polyglot-LLM
3. Enter Gemini API key
4. Set target language (e.g., Spanish, French, English)
5. (Optional) Adjust thinking budget, max tokens, system prompt
6. Done

**No source language selection.** AI auto-detects what language you're translating from.

### Daily Usage

**Scenario 1: Live Chat (Real-Time Mode)**
- Press NVDA+Shift+Control+T (enable translation)
- Enable conversation mode in settings
- Chat normally—all incoming messages translated with context
- Press NVDA+Shift+Control+T again to disable

**Scenario 2: Reading Foreign Email (On-Demand)**
- Select text with Shift+Arrows
- Press NVDA+Shift+T, then T
- Translation spoken and copied to clipboard

---

## 🔧 Development Standards

### NVDA-Specific Practices

**Module Imports:**
- Use NVDA's bundled libraries where possible
- External modules: Include in addon package (see AI Content Describer's vendor/ folder)
- Don't assume standard Python packages available

**Coding Style:**
- Follow NVDA's code conventions (see their style guide)
- Use tabs, not spaces (NVDA standard)
- Class names: CamelCase
- Function names: camelCase (NVDA style, not snake_case)

**Logging:**
```python
import logHandler
log = logHandler.log
log.debug("Translation started")
log.error("API call failed", exc_info=True)
```

**Error Handling:**
- Never crash NVDA
- Log errors, show user-friendly messages
- Graceful degradation (if API fails, speak original text)

### General Standards

**Git Commits:**
- Format: `type: message` (one line)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`
- Examples: 
  - `feat: add conversation mode toggle`
  - `fix: resolve cache invalidation bug`
  - `chore: update dependencies`
  - `refactor: extract translation logic to separate module`
- **NO multiline commits** (terminal hangs)
- Commit frequently at logical checkpoints (small, atomic changes)
- **Not big chunks** - commit often enough to rollback easily for testing
- Good granularity: After implementing a single feature, fixing a bug, refactoring a function
- Don't push yet—I'll push when done

**Development Environment:**
- Use `uv venv` for isolated testing if needed
- Install dependencies with `uv pip install`
- Don't pollute main Python installation

**Comments:**
- Write for developers, not yourself
- Explain WHY, not WHAT (code shows what)
- No stream-of-consciousness notes
- Example:
  ```python
  # GOOD: Cache translations to reduce API costs
  # BAD: Here we cache stuff
  ```

---

## 📦 Build Configuration

**Use SCons (like AI Content Describer):**

**Files needed:**
- `buildVars.py` - Addon metadata (name: "polyglotLLM", version, author)
- `sconstruct` - Build script
- `manifest.ini` - Addon manifest

**Build command:**
```bash
scons
```

**Output:** `polyglotLLM-x.y.nvda-addon` file ready for installation

**Internationalization:**
```bash
scons pot  # Generate translation template
```

---

## 🚨 Critical Requirements

**Must-Have:**
- Works with Gemini 3 Flash (auto-detects source language)
- API key stored securely in NVDA config
- Customizable system prompt in settings
- Smart caching system (research best approach for context-aware caching)
- Both translation modes functional
- Conversation mode toggle
- Thinking budget configurable
- Max tokens configurable (default 2048)
- Error if text exceeds max tokens
- No crashes, even if API fails
- Fast enough for real-time use

**Nice-to-Have:**
- Language auto-detection
- Multiple LLM support (future)
- Custom system prompts (advanced users)
- Translation quality feedback

---

## 🎯 Success Criteria

**Addon is ready when:**
- Builds successfully with `scons`
- Installs in NVDA without errors
- Auto-detects source language accurately
- Real-time mode translates speech with <1 sec delay
- On-demand mode works for text/clipboard/last speech
- Conversation mode provides better context in multi-turn chats
- Smart caching reduces redundant API calls
- API errors handled gracefully (logs error, speaks original)
- Settings panel has all options (target lang, API key, system prompt, thinking budget, max tokens, conversation mode)
- Max token limit enforced with clear error message
- Git history shows frequent, atomic commits (easy to rollback)
- README explains this is for short text/paragraphs, not documents

---

## 📚 Resources

**In `/learn/` folder:**
- Full source code of 3 working addons
- Reference these constantly

**NVDA Developer Docs:**
- https://www.nvaccess.org/files/nvda/documentation/developerGuide.html
- API reference, addon structure, best practices

**Gemini API Docs:**
- https://ai.google.dev/docs
- Authentication, request format, error codes

---

## 💡 Development Approach

**Step 1:** Study `/learn/` addons
- Understand settings storage (AI Content Describer)
- Understand keyboard layer (Instant Translate)
- Understand speech interception (Translate)

**Step 2:** Set up project structure
- Copy buildVars.py, sconstruct from AI Content Describer
- Create globalPlugins/aiTranslator/ folder
- Create __init__.py with basic plugin class

**Step 3:** Implement settings panel
- Copy settings dialog from AI Content Describer
- Add target language dropdown (NO source language - AI auto-detects)
- Add API key field
- Add system prompt textbox (multi-line, with default)
- Add thinking budget dropdown (Minimal/Low/Medium/High)
- Add max tokens slider/spinbox (default 2048)
- Add conversation mode checkbox
- Add conversation history length slider

**Step 4:** Implement Gemini API integration
- Copy API client from AI Content Describer
- Research Gemini 3 Flash thinking budget parameters
- Implement auto-detect source language (let AI determine language)
- Adapt for translation with customizable system prompt
- Add conversation history handling
- Implement smart caching (research: string-based vs. context-aware)
- Add max token validation

**Step 5:** Implement real-time mode
- Copy speech interception from Translate addon
- Add translation call before speaking
- Implement caching to reduce API calls and delay
- Handle cache invalidation (research best approach)

**Step 6:** Implement on-demand mode
- Copy keyboard layer from Instant Translate
- Add gestures for T, Shift+T, L, C, A, S
- Wire up to Gemini API

**Step 7:** Test & debug
- Install in NVDA
- Check NVDA log for errors
- Test both modes
- Test conversation mode context

**Step 8:** Polish & document
- README with setup instructions
- Explain target language only (source auto-detected)
- Note max token limit and use case (paragraphs, not documents)
- Document customizable system prompt
- Comments in code
- Final testing
- Frequent, atomic commits throughout

---

## 🔥 Final Reminders

**Copy, don't reinvent.** The three addons in `/learn/` are proven, working code. Adapt them.

**NVDA is different.** Settings, imports, conventions—follow NVDA's way, not standard Python.

**Test in NVDA.** Errors show in NVDA log (`NVDA+Control+F1` → View Log). Use `log.debug()` liberally.

**Keep it simple.** Gemini Flash. Auto-detect source. One target language. Easy setup. Works out of the box.

**Cost-effective.** Smart caching system. Research context-aware caching strategies. Gemini Flash is cheap but API calls add up.

**Commit often.** Small, atomic commits. Easy to rollback for testing. Not big chunks.

Now build something that breaks down language barriers for blind people worldwide. 🌍🔊