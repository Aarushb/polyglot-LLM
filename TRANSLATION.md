# Translation Guide for Polyglot-LLM

Thank you for your interest in translating Polyglot-LLM!

## For Translators

### Getting Started

1. **Get the template file:**
   - Download `polyglotLLM.pot` from the repository
   - This contains all translatable strings

2. **Create your translation:**
   - Copy the `.pot` file to `addon/locale/YOUR_LANG/LC_MESSAGES/nvda.po`
   - Replace `YOUR_LANG` with your language code (e.g., `es`, `fr`, `de`)
   - Edit the `.po` file with a translation tool like:
     - [Poedit](https://poedit.net/) (recommended)
     - [Lokalize](https://userbase.kde.org/Lokalize)
     - Any text editor

3. **Submit your translation:**
   - Create a pull request with your `.po` file
   - Or send it to the maintainer

### Translation Tools

**Poedit (Recommended):**
- Free and easy to use
- Available for Windows, Mac, Linux
- Download: https://poedit.net/

**Online Tools:**
- Weblate, Crowdin, or similar platforms (if set up for this project)

### Important Notes

- **Preserve placeholders:** Keep `{variable}` exactly as is
- **Keyboard shortcuts:** Keep key names like `NVDA+Shift+T` unchanged
- **UI consistency:** Match NVDA's translation style in your language
- **Test your translation:** Install the addon and check that everything displays correctly

### Translation Context

The addon has these main areas:

1. **Settings panel** - Configuration options
2. **Layer commands** - Translation layer help text
3. **Status messages** - Feedback to users
4. **Documentation** - Help files (separate from .po files)

## For Developers

### Generating the POT Template

To extract all translatable strings:

```bash
python -m SCons pot
```

This creates `polyglotLLM.pot` with all `_("string")` calls.

### Updating Translations

When strings change:

```bash
python -m SCons mergePot
```

This updates existing `.po` files with new strings while preserving translations.

### Building with Translations

**Requirements:**
- gettext tools (provides `msgfmt` command)
- Install on Windows: https://mlocati.github.io/articles/gettext-iconv-windows.html

**Build:**

```bash
python -m SCons
```

**Without gettext:**
The build will work but skip translations with a warning.

### Translation File Structure

```
addon/
  locale/
    en/
      LC_MESSAGES/
        nvda.po        # English (source)
    es/
      LC_MESSAGES/
        nvda.po        # Spanish
        nvda.mo        # Compiled (auto-generated)
    fr/
      LC_MESSAGES/
        nvda.po        # French
        nvda.mo        # Compiled (auto-generated)
```

### Marking Strings for Translation

In Python code:

```python
# Simple string
ui.message(_("Translation enabled"))

# String with variables
ui.message(_("Target: {lang}").format(lang=target_lang))

# Multi-line strings
help_text = _(
    "T: Translate selection, "
    "L: Last speech, "
    "H: Help"
)
```

### Documentation Translation

Documentation files (README, help) are separate:

```
addon/
  doc/
    en/
      readme.md      # English documentation
    es/
      readme.md      # Spanish documentation
```

These are translated separately from the UI strings.

## Current Translation Status

- ✅ English (source language) - Complete
- ⬜ Spanish - Needed
- ⬜ French - Needed
- ⬜ German - Needed
- ⬜ Portuguese - Needed
- ⬜ Italian - Needed
- ⬜ Chinese - Needed
- ⬜ Japanese - Needed
- ⬜ Russian - Needed
- ⬜ Arabic - Needed

Want to help? Pick a language and contribute!

## Translation Guidelines

### Style

- **Be concise** - Screen reader users prefer brief messages
- **Be consistent** - Use the same terms throughout
- **Match NVDA** - Use terminology consistent with NVDA's translation
- **Test with speech** - Ensure translations sound natural when spoken

### Common Terms

| English | Notes |
|---------|-------|
| Layer | Translation layer - keep consistent |
| Real-time | Automatic/live translation mode |
| Conversation mode | Context-aware translation |
| Cache | Stored translations |
| Target language | Language to translate into |
| Settings | Configuration panel |

### Keyboard Shortcuts

**Do NOT translate:**
- `NVDA+Shift+T`
- `Escape`
- Key names: `T`, `L`, `M`, `R`, `X`, `S`, `H`, `C`

These should remain in English for consistency.

### Variables in Strings

Keep placeholder format intact:

```
English: "Target: {lang}, Conversation: {convo}"
Spanish: "Destino: {lang}, Conversación: {convo}"
         ^^^^^^^ translate this ^^^^^ not this ^^^
```

## Testing Translations

1. **Build the addon** with your translation
2. **Install in NVDA**
3. **Change NVDA language** to your language
4. **Test all features:**
   - Settings panel labels
   - Layer help text
   - Status messages
   - Error messages

5. **Check for:**
   - Truncated text
   - Awkward phrasing when spoken
   - Missing translations
   - Incorrect variables

## Questions?

- Open an issue on GitHub
- Contact the maintainer
- Ask in NVDA translation mailing list

## Credits

Translations are a community effort. Contributors will be credited in:
- Addon documentation
- Release notes
- Translation files themselves

Thank you for making Polyglot-LLM accessible to more users worldwide! 🌍
