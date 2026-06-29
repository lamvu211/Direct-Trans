# Direct-Trans

**Direct-Trans** is an AI-powered translation tool that allows you to translate text on the fly using customizable hotkeys. It runs quietly in your system tray and provides seamless translation across any application.

## Features
- **Instant Translation:** Select text anywhere on your screen and translate it immediately using hotkeys.
- **Multiple AI Backends:** Supports translation through powerful AI models, including Gemini, Groq, DeepL, and Google Translate.
- **Clipboard Utility:** Seamlessly copies and restores your clipboard content during the translation process so your workflow isn't interrupted.
- **System Tray Integration:** Runs quietly in your system tray with a built-in settings window for easy configuration.
- **Popup UI:** Displays translated text in a convenient, non-intrusive popup window.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lamvu211/Direct-Trans.git
   cd Direct-Trans
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python src/main.py
   ```

4. **Configure API Keys:** 
   Right-click the Direct-Trans icon in your system tray, open Settings, and set up your preferred AI API keys (e.g., Gemini, Groq) for the best translation quality.

## Build from Source
Use the provided batch file to create a standalone executable for Windows using PyInstaller:
```bash
.\build.bat
```
The compiled executable will be available in the `dist` folder.

## License
This project is open-sourced under the MIT license.
