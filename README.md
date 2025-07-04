🤖 AIVA Chatbot

AIVA is a desktop chatbot application powered by Gemini 2.0 Flash. It allows for both text and voice input/output, includes a dark mode, and stores your chat history locally for a smooth user experience.

✨ Features

💬 Gemini-powered responses using the Gemini 2.0 Flash API

🎤 Voice input with microphone using SpeechRecognition

🔊 Optional voice output using pyttsx3

🕶️ Dark Mode toggle

📀 Persistent chat history saved locally

🔐 API key prompt at startup

📋 Menu with options like Clear History, Voice toggle, and Exit

📦 Requirements

Install the required dependencies with:

pip install -r requirements.txt

Or install manually:

pip install tk pyttsx3 SpeechRecognition google-generativeai

🚀 How to Run

Run from source (Python required):

python aiva.py

Run as standalone app (after build):

dist/AIVA.exe

Note: You must enter your Gemini API key when prompted the first time.

🛠 How to Build the App (.exe)

Use PyInstaller to convert the Python file into a standalone .exe:

pyinstaller --noconfirm --onefile --windowed aiva.py

This creates a folder called dist/ containing AIVA.exe.

🙈 .gitignore Contents

dist/
build/
__pycache__/
*.exe
*.log
chat_history.txt

🧠 Notes

Your API key is stored in memory only — not saved.

The app will crash if no internet connection is available during API calls.

Be sure to keep your .exe and AIVA.ico in the same folder if you use a custom icon.

📦 GitHub Release (Optional)

If you want to share your .exe file:

Go to your GitHub repo → Releases

Click "Draft a new release"

Tag: v1.0.0

Title: First Release

Description: Initial release of the AIVA chatbot

Upload your .exe file from dist/

Click Publish

👨‍💼 Author

Created by Emirhan HuseyinGitHub Profile

🔐 Disclaimer

This project uses the Google Gemini API via the google-generativeai package.You must supply your own API key to use the chatbot.
