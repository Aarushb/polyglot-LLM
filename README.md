# Polyglot-LLM: AI-Powered Translation for NVDA

Polyglot-LLM is an NVDA addon that provides AI-powered real-time and on-demand translation using Google Gemini. This addon enables seamless communication between blind screen reader users speaking different languages.

## Features

- **Real-Time Translation Mode**: Automatically translates all NVDA speech in real-time
- **On-Demand Translation Mode**: Selectively translate text, clipboard, or last spoken text
- **Conversation Mode**: Maintains conversation history for context-aware translations
- **AI-Powered**: Uses Google Gemini for intelligent, context-aware translations
- **Auto Language Detection**: Automatically detects source language
- **Smart Caching**: Reduces API calls and improves performance

## Setup

1. Install the addon
2. Open NVDA Preferences → Polyglot-LLM
3. Enter your Google Gemini API key (get one at https://ai.google.dev/)
4. Select your target language (the language you want translations in)
5. (Optional) Customize system prompt, thinking budget, and other settings

## Usage

### Real-Time Translation Mode

Press `NVDA+Shift+Control+T` to toggle real-time translation on/off. When enabled, all NVDA speech is automatically translated to your target language.

Perfect for:
- Live chat conversations
- Video streaming content
- Real-time communication

### On-Demand Translation Mode

Press `NVDA+Shift+T` to activate the translation layer, then:

- `T` - Translate selected text
- `Shift+T` - Translate clipboard content
- `L` - Translate last spoken text
- `C` - Copy last translation to clipboard
- `A` - Announce current language configuration
- `S` - Swap source and target languages

Perfect for:
- Reading emails or documents
- Non-urgent translation tasks
- Reviewing clipboard content

### Conversation Mode

Enable conversation mode in settings to maintain conversation history for better context-aware translations. The AI will remember recent messages to provide more accurate translations that understand pronouns, topic continuity, and conversational tone.

## Configuration Options

- **Target Language**: The language to translate into (required)
- **API Key**: Your Google Gemini API key (required)
- **System Prompt**: Customizable prompt for advanced users
- **Conversation Mode**: Toggle conversation history tracking
- **Conversation History Length**: Number of messages to remember (5-20)
- **Thinking Budget**: AI reasoning level (Minimal/Low/Medium/High)
- **Max Tokens**: Maximum text length (default: 2048)

## Important Notes

- **Text Length**: This addon is designed for translating paragraphs and short text, not long documents
- **API Costs**: While Gemini Flash is cost-effective, be mindful of API usage
- **Internet Required**: Requires internet connection for API calls
- **Privacy**: Text is sent to Google Gemini for translation

## Keyboard Shortcuts

All keyboard shortcuts are customizable in NVDA's Input Gestures dialog.

Default shortcuts:
- `NVDA+Shift+Control+T`: Toggle real-time translation
- `NVDA+Shift+T`: Open on-demand translation layer

## License

GPL v2

## Support

For issues, feature requests, or contributions, visit:
https://github.com/Aarushb/polyglot-LLM
