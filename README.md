# Polyglot-LLM: AI Translation for NVDA

**Break down language barriers with context-aware translation powered by Google Gemini.**

Polyglot-LLM is an NVDA addon that provides both real-time automatic translation and on-demand selective translation using AI. Unlike traditional translators, it understands conversation context for more natural translations.

## ✨ Features

### Two Translation Modes

**Real-Time Translation** - Automatically translates all NVDA speech
- Perfect for live chats, streaming content, or conversations
- Toggle with `NVDA+Shift+Control+T`
- Smart caching minimizes delays

**On-Demand Translation** - Selective translation when you need it
- Press `NVDA+Shift+T` to enter translation layer, then:
  - `T` - Translate selected text
  - `Shift+T` - Translate clipboard
  - `L` - Translate last spoken text
  - `C` - Copy last translation to clipboard
  - `A` - Announce current language settings
  - `V` - View conversation history
  - `H` - Help (list gestures)

### Conversation Mode

Enable in settings for context-aware translations:
- Remembers recent messages in the conversation
- AI understands pronouns, topic flow, and tone
- Example: "Which movie?" vs "Which?" - context matters

### Smart Features

- **Auto Language Detection** - No need to specify source language
- **Intelligent Caching** - Reduces API costs and delays
- **Customizable System Prompt** - Adjust translation behavior
- **Thinking Budget** - Balance speed vs quality
- **Max Token Limit** - Configurable with clear error messages

## 🚀 Quick Start

### Installation

1. Download the latest `.nvda-addon` file from releases
2. Open the file (NVDA will install it automatically)
3. Restart NVDA when prompted

### Setup

1. Go to `NVDA menu → Preferences → Settings → Polyglot-LLM`
2. Enter your Google Gemini API key ([get one free](https://aistudio.google.com/app/apikey))
3. Select your target language (e.g., Spanish, French, English)
4. Adjust settings if desired (defaults work great)
5. Click OK

### Usage

**For Live Conversations:**
- Enable conversation mode in settings
- Press `NVDA+Shift+Control+T` to turn on real-time translation
- Chat normally - everything is automatically translated
- Press `NVDA+Shift+Control+T` again to turn off

**For Reading Foreign Text:**
- Select text with `Shift+Arrows`
- Press `NVDA+Shift+T`, then `T`
- Translation is spoken and copied to clipboard
- Real-time communication

### On-Demand Translation Layer

You already have on-demand gestures listed above. The layer includes:
- `H` - Help (list all gestures)
- `V` - View conversation history

Perfect for:
- Reading emails or documents
- Non-urgent translation tasks
- Reviewing clipboard content

## ⚙️ Settings

**NVDA → Preferences → Settings → Polyglot-LLM**

- **API Key** - Your Google Gemini API key (required)
- **Target Language** - Language to translate into (required)
- **System Prompt** - Customize AI behavior (advanced)
- **Thinking Budget** - Trade speed for quality (Minimal/Low/Medium/High)
- **Max Tokens** - Maximum translation length (default: 2048)
- **Conversation Mode** - Enable context-aware translation
- **History Length** - Number of messages to remember (5-20)

## 🌍 Supported Languages

Over 40 languages including:
- English, Spanish, French, German, Italian, Portuguese
- Chinese (Simplified/Traditional), Japanese, Korean
- Arabic, Hebrew, Hindi, Russian, Turkish
- And many more...

**Note:** Source language is automatically detected - no configuration needed.

## 💡 Use Cases

- **International Gaming** - Communicate with players worldwide
- **Language Learning** - Understand native content while learning
- **Global Chat Rooms** - Participate in any language community
- **Foreign Websites** - Read content in your language
- **Cross-Language Support** - Help others in their native language

## 🎯 Important Notes

### This Addon is for Short Text

- **Perfect for:** Messages, paragraphs, chat, selected text
- **Not designed for:** Long documents, articles, books
- Max token limit prevents translating very long content
- Use document translation tools for large texts

### API Costs

Google Gemini Flash is extremely cheap:
- Free tier: 15 requests/minute, 1500 requests/day
- Paid tier: $0.075 per 1M input tokens
- Smart caching reduces redundant API calls significantly

### Privacy

- Translations are sent to Google Gemini API
- No data is stored by the addon except cached translations (local)
- Review Google's privacy policy if concerned

## 🔧 Troubleshooting

### "Translation failed" Error

1. Press `NVDA+Control+F1` → View Log
2. Look for error details from Polyglot-LLM
3. Common fixes:
   - Check API key is correct
   - Verify internet connection
   - Check if you hit rate limits (wait a minute)
   - Ensure target language is set

### Translations are Slow

1. Lower thinking budget to "Minimal" or "Low"
2. Ensure caching is working (try repeating text)
3. Check network speed
4. Disable conversation mode if not needed

### Addon Won't Load

1. Ensure NVDA version is compatible (2024.1+)
2. Check NVDA log for errors
3. Try reinstalling the addon
4. Check for conflicts with other translation addons

## 📚 Documentation

- **User Guide:** This README
- **Developer Guide:** See [DEVELOPMENT.md](DEVELOPMENT.md)
- **Copilot Instructions:** See [.github/copilot-instructions.md](.github/copilot-instructions.md)

## 🤝 Contributing

Contributions welcome! See [DEVELOPMENT.md](DEVELOPMENT.md) for technical details.

Key points:
- Follow NVDA coding conventions (tabs, camelCase)
- Test both SDK and REST API modes
- Commit frequently with descriptive messages
- Don't push - maintainer handles releases

## 📄 License

GPL v2 - See [LICENSE](LICENSE) file

## 🙏 Credits

**Inspired by and built upon:**
- [AI Content Describer](https://github.com/cartertemm/AI-content-describer) - API integration patterns
- [Instant Translate](https://github.com/nvda-addons/instantTranslate) - Keyboard layer design
- [Translate](https://github.com/yplassiard/nvda-translate) - Real-time speech interception

**Powered by:**
- [Google Gemini 3 Flash](https://ai.google.dev/) - Fast, cost-effective AI translation

## 🌟 Why Polyglot-LLM?

Traditional translation services translate word-by-word without understanding context. AI models understand:
- **Conversation flow** - "That's cool!" → Friendly tone preserved
- **Pronouns** - "Is it ready?" → Knows what "it" refers to
- **Slang and idioms** - Natural expressions, not literal translations
- **Cultural context** - Adapts to language norms

This creates more natural, human-like translations that make cross-language communication feel seamless.

---

**Made with ❤️ for the NVDA community**
