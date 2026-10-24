# 🎓 CampusConnect AI

**An AI-Powered Campus Lost & Found Platform with a Natural-Language-to-SQL Assistant**

CampusConnect AI helps students report lost and found items on campus and query campus records using plain English.

This project is developed for **HackFest 2.0 — Track 1: Open-Source AI**, focusing on the *SQL in Plain English* problem statement.

## ✨ Features

* 🔎 **Lost & Found Board** — View reported lost and found items.
* 📝 **Report Items** — Submit details about lost or found belongings.
* ✅ **Resolve Reports** — Mark items as resolved.
* 🤖 **Ask Your Database** — Ask questions in plain English and view database results.
* 🧠 **Local AI Model** — Uses Ollama to run an AI model locally.
* 🗃️ **SQLite Database** — Stores item reports locally.
* 🖥️ **Interactive Web Interface** — Built with Streamlit.

## 💡 Example Questions

Try asking the AI assistant:

* Show all found items.
* List unresolved lost items.
* Show the latest reports.
* Count the number of lost items.

The assistant converts supported natural-language questions into SQL queries and displays the results.

## 🛠️ Technology Stack

| Technology  | Purpose                            |
| ----------- | ---------------------------------- |
| Python      | Application logic                  |
| Streamlit   | Web interface                      |
| SQLite      | Local database                     |
| Ollama      | Runs the AI model locally          |
| Qwen 2.5 3B | Natural-language-to-SQL generation |

## ⚙️ Prerequisites

Install the following before running the application:

* Python
* Ollama
* The `qwen2.5:3b` model

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/charishmareddi06-collab/CampusConnect-AI.git
cd CampusConnect-AI
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Download the AI Model

```bash
ollama pull qwen2.5:3b
```

### 4. Run the Application

Make sure Ollama is running, then execute:

```bash
python -m streamlit run app.py
```

Open the local address displayed in your terminal, usually:

`http://localhost:8501`

## 🔐 Safety and Privacy

* Generated SQL queries are checked before execution.
* The AI assistant is intended for read-only database queries.
* The database is stored locally.
* Never upload database files containing personal information or private records to a public repository.

## 🎯 HackFest Alignment

**Track:** Track 1 — Open-Source AI

**Problem Focus:** SQL in Plain English

CampusConnect AI demonstrates how users can interact with structured data using natural language instead of writing SQL manually.

## 🔮 Future Improvements

* Student authentication.
* Image uploads for lost and found items.
* Search and category filters.
* Notifications for matching items.
* Campus-wide deployment.
* Improved natural-language query accuracy.

## 📄 License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

---

**Built with ❤️ for smarter campus communities.**
