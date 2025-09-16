# ScreenMind - AI-Powered Screenshot Question Solver

An intelligent screenshot-based question answering tool that uses AI to automatically identify and solve questions from screen captures.

## ✨ Features

- 🚀 **Global Hotkey**: `Cmd+Shift+Q` (macOS) / `Ctrl+Shift+Q` (Windows/Linux)
- 📷 **Smart Screenshot**: Drag-to-select area capture
- 🤖 **Multi-AI Support**: Supports Qwen, Google Gemini, and OpenAI GPT models
- 💡 **Multi-Question Types**: Multiple choice, fill-in-the-blank, true/false, etc.
- 🎯 **Real-time Results**: Instant popup with answers and explanations
- 🔧 **System Tray**: Background operation with tray management
- ⚙️ **Easy Configuration**: Graphical settings interface

## 🚀 Quick Start

### 1. Install Dependencies

Make sure you have Python 3.9+ and uv installed:

```bash
# Install dependencies with uv
uv sync
```

### 2. Configure AI Model and API Key

ScreenMind supports multiple AI models. Choose one and configure its API key:

**Qwen (Recommended):**
- Get API key: https://dashscope.console.aliyun.com/apiKey
- Set environment variables:
```bash
export AI_PROVIDER=qwen
export AI_MODEL=qwen-vl-plus
export QWEN_API_KEY="your_qwen_api_key_here"
```

**Google Gemini:**
- Get API key: https://makersuite.google.com/app/apikey
```bash
export AI_PROVIDER=gemini
export AI_MODEL=gemini-1.5-flash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

**OpenAI GPT:**
- Get API key: https://platform.openai.com/api-keys
```bash
export AI_PROVIDER=openai
export AI_MODEL=gpt-4o
export OPENAI_API_KEY="your_openai_api_key_here"
```

**Alternative - GUI Settings:**
1. Launch the application
2. Right-click tray icon → Settings
3. Select AI model and enter API key

### 3. Run Application

```bash
# Run with uv
uv run python main.py

# Or run directly
python main.py
```

## 📖 Usage

1. **Launch App**: Application runs in background and hides to system tray
2. **Take Screenshot**: Press `Cmd+Shift+Q` (macOS) or `Ctrl+Shift+Q` (Windows/Linux)
3. **Select Area**: Drag to select the question area, press Enter to confirm
4. **View Results**: Wait for AI analysis, results appear in popup window
5. **Copy Answer**: Click "Copy Answer" to copy result to clipboard

## 📁 Project Structure

```
ScreenMind/
├── screenmind/
│   ├── __init__.py
│   ├── main.py              # Main application
│   ├── config.py           # Configuration management
│   ├── modules/            # Core modules
│   │   ├── screenshot.py   # Screenshot functionality
│   │   ├── hotkey.py      # Global hotkey listener
│   │   └── ai_service.py  # AI service integration
│   └── gui/               # GUI components
│       ├── main_window.py # Main windows
│       └── system_tray.py # System tray
├── main.py                # Entry point
├── pyproject.toml        # Project configuration
├── .env.example         # Environment configuration example
└── README.md
```

## 🔧 System Requirements

- Python 3.9+
- macOS 10.15+ / Windows 10+ / Linux
- Internet connection (for AI service)

## 📦 Dependencies

- `pillow`: Image processing
- `pynput`: Global hotkey monitoring
- `google-generativeai`: Google Gemini AI service
- `openai`: OpenAI API client (also used for Qwen)
- `pystray`: System tray integration
- `tkinter`: GUI framework (built-in with Python)

## ⚠️ Important Notes

- First run may require screen recording permissions
- API calls require internet connection
- Recommend testing API key validity before use

## 🔧 Troubleshooting

### Hotkey Not Responding
- Check accessibility permissions granted (macOS)
- Try restarting the application
- Ensure no other apps use the same hotkey

### AI Analysis Failed
- Verify API key is correct
- Check internet connection
- Confirm API quota not exceeded

### Screenshot Issues
- Check screen recording permissions (macOS)
- Ensure no conflicting applications

## 🎯 How It Works

1. **Hotkey Detection**: Global listener monitors for the configured key combination
2. **Screenshot Capture**: Displays overlay for area selection and captures the chosen region
3. **AI Processing**: Sends image to selected AI model (Qwen/Gemini/OpenAI) with optimized prompts
4. **Result Parsing**: Extracts question type, content, answer, and explanation from AI response
5. **Display Results**: Shows formatted results in popup window with copy functionality

## 🤖 Supported AI Models

| Provider | Models | API Key Source |
|----------|--------|----------------|
| **Qwen (通义千问)** | qwen-vl-plus, qwen-vl-max | [DashScope Console](https://dashscope.console.aliyun.com/apiKey) |
| **Google Gemini** | gemini-1.5-flash, gemini-1.5-pro | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| **OpenAI GPT** | gpt-4o, gpt-4o-mini | [OpenAI Platform](https://platform.openai.com/api-keys) |

## 🛡️ Privacy & Security

- Screenshots are processed locally and sent only to selected AI service
- No data is stored on external servers beyond AI provider processing
- API keys are stored locally
- Application runs entirely on your machine
- You can choose which AI provider to trust with your data

## 🚀 Future Enhancements

- [x] Support for multiple AI models (Qwen, Gemini, OpenAI)
- [ ] Support for more AI models (Claude, local models)
- [ ] OCR text extraction capabilities
- [ ] Batch screenshot processing
- [ ] History and bookmarking features
- [ ] Custom prompt templates
- [ ] Mobile app companion

## 📄 License

This project is for educational and research purposes only. Please comply with relevant laws and regulations.