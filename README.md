# CampusConnect AI

A beginner-friendly hackathon project for **HackFest Track 1: Open-Source AI**, matching the **SQL in Plain English** problem statement.

## What it does
- Lost & Found board for campus items
- Report lost/found items and mark them resolved
- Ask questions in plain English
- A locally running open model (through Ollama) generates a SQL `SELECT` query and a simple explanation
- Displays the SQL and matching database results
- Read-only SQL checks help block write/admin statements

## Requirements
- Windows 10/11
- Python 3.10+
- Ollama installed
- Internet is needed only to install/download dependencies and the model. The AI inference itself runs locally after setup.

## Setup on Windows

1. Install Python from https://www.python.org/downloads/windows/ . During installation, tick **Add Python to PATH**.
2. Install Ollama from https://ollama.com/download/windows
3. Open **Command Prompt** and go to the folder containing `app.py`. Example:
   ```bat
   cd %USERPROFILE%\Downloads\CampusConnectAI
   ```
4. Install Python dependencies:
   ```bat
   py -m pip install -r requirements.txt
   ```
5. Download the model (this may take a few minutes):
   ```bat
   ollama pull qwen2.5:3b
   ```
6. Start the app:
   ```bat
   py -m streamlit run app.py
   ```
7. Your browser should open the app. If it doesn't, open the local URL printed in the terminal, usually `http://localhost:8501`.

Keep Ollama installed and running while using the AI tab. If needed, open another Command Prompt and run:
```bat
ollama serve
```
If the model is already downloaded, no extra download is needed.

## Demo questions
- Show found items near the library
- Which items are still open?
- List all electronics items
- Show lost items reported after October 20, 2026

## Important safety note
The app only intends to execute one read-only `SELECT` query, includes checks for unsafe SQL, and applies a SQLite authorizer during execution. This is a hackathon prototype, not a production security guarantee. Do not use real sensitive personal information in demos.

## GitHub checklist
- Create a public repository named `CampusConnectAI`
- Upload `app.py`, `requirements.txt`, and `README.md`
- Add a license (MIT is a reasonable choice if your team wants one)
- Include screenshots and a short demo video
- In your presentation, explain that the model runs locally using Ollama and that users can inspect generated SQL before results are shown.
