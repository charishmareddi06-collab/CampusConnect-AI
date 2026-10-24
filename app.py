import sqlite3
import re
import requests
import streamlit as st
from datetime import datetime

APP_TITLE = "CampusConnect AI"
DB_PATH = "campusconnect.db"
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"

st.set_page_config(page_title=APP_TITLE, page_icon="🎓", layout="wide")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('Lost', 'Found')),
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            contact TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    if count == 0:
        samples = [
            ("Found", "Blue water bottle", "Bottle", "Library", "Blue bottle left on a study table.", "student1@college.edu", "Open", "2026-10-20 10:30"),
            ("Lost", "Black wallet", "Wallet", "Canteen", "Small black wallet, may contain student ID.", "student2@college.edu", "Open", "2026-10-21 12:15"),
            ("Found", "Scientific calculator", "Electronics", "Room 204", "Calculator found after maths lecture.", "student3@college.edu", "Open", "2026-10-22 14:00"),
            ("Lost", "USB drive", "Electronics", "Library", "Silver 32GB USB drive.", "student4@college.edu", "Open", "2026-10-23 09:20"),
        ]
        conn.executemany("""
            INSERT INTO items (item_type, item_name, category, location, description, contact, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, samples)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

def fetch_items(search="", item_type="All", status="Open"):
    conn = get_conn()
    sql = "SELECT id, item_type, item_name, category, location, description, contact, status, created_at FROM items WHERE 1=1"
    params = []
    if search.strip():
        like = f"%{search.strip()}%"
        sql += " AND (item_name LIKE ? OR category LIKE ? OR location LIKE ? OR description LIKE ?)"
        params.extend([like, like, like, like])
    if item_type != "All":
        sql += " AND item_type = ?"
        params.append(item_type)
    if status != "All":
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows

def add_item(item_type, item_name, category, location, description, contact):
    conn = get_conn()
    conn.execute("""
        INSERT INTO items (item_type, item_name, category, location, description, contact, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)
    """, (item_type, item_name.strip(), category, location.strip(), description.strip(), contact.strip(),
          datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def resolve_item(item_id):
    conn = get_conn()
    conn.execute("UPDATE items SET status='Resolved' WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

SCHEMA_TEXT = """
Table: items
Columns:
- id (integer): unique item ID
- item_type (text): 'Lost' or 'Found'
- item_name (text): name of the item
- category (text): item category
- location (text): where it was lost/found
- description (text): extra details
- contact (text): contact information
- status (text): 'Open' or 'Resolved'
- created_at (text): date and time submitted
"""

def ask_ollama(question, model):
    prompt = f"""
You convert a user's question into ONE safe SQLite SELECT query for the CampusConnect database.
Return ONLY valid JSON with keys "sql" and "explanation".
No markdown fences. Do not include any text outside JSON.
Allowed table: items
Allowed columns: id, item_type, item_name, category, location, description, contact, status, created_at
Schema:
{SCHEMA_TEXT}
Rules:
- Generate exactly one SELECT statement, no semicolon.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, ATTACH, or other write/admin statements.
- Use case-insensitive matching with LOWER(column) LIKE LOWER('%word%') where useful.
- Limit results to 50 rows.
- Explanation should be short and beginner-friendly.
User question: {question}
"""
    response = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt, "stream": False, "format": "json"},
        timeout=90
    )
    response.raise_for_status()
    outer = response.json()
    import json
    return json.loads(outer.get("response", "{}"))

def run_readonly_query(sql):
    cleaned = sql.strip()
    if not re.match(r"(?is)^select\b", cleaned):
        raise ValueError("Safety check blocked this query: only SELECT queries are allowed.")
    cleaned = cleaned.rstrip(";").strip()
    if ";" in cleaned:
        raise ValueError("Safety check blocked multiple SQL statements.")
    forbidden = re.compile(r"(?is)\b(insert|update|delete|drop|alter|create|replace|pragma|attach|detach|vacuum|reindex|truncate)\b")
    if forbidden.search(cleaned):
        raise ValueError("Safety check blocked a potentially unsafe SQL keyword.")
    conn = get_conn()
    # SQLite authorizer provides an additional read-only layer for this query.
    allowed_actions = {
        sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
        getattr(sqlite3, "SQLITE_RECURSIVE", -1)
    }
    def authorizer(action, arg1, arg2, db_name, trigger_name):
        return sqlite3.SQLITE_OK if action in allowed_actions else sqlite3.SQLITE_DENY
    conn.set_authorizer(authorizer)
    try:
        cur = conn.execute(cleaned)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(50)
        return columns, rows
    finally:
        conn.close()

init_db()

st.title("🎓 CampusConnect AI")
st.caption("Campus Lost & Found + Open-Source AI that turns plain-English questions into SQL.")
with st.sidebar:
    st.header("About this project")
    st.write("**HackFest Track:** Open-Source AI")
    st.write("**Challenge match:** SQL in Plain English")
    st.write("Ask questions in normal language, inspect the generated SQL, and see real database results.")
    st.divider()
    model_name = st.text_input("Ollama model name", value=DEFAULT_MODEL)
    st.caption("Default: qwen2.5:3b. You can change this to a model installed in Ollama.")

tab_items, tab_add, tab_ai = st.tabs(["🔎 Browse items", "➕ Report an item", "🤖 Ask database (AI)"])

with tab_items:
    st.subheader("Lost & Found board")
    c1, c2, c3 = st.columns([2, 1, 1])
    search_text = c1.text_input("Search items", placeholder="e.g. bottle, library, wallet")
    type_filter = c2.selectbox("Type", ["All", "Lost", "Found"])
    status_filter = c3.selectbox("Status", ["Open", "Resolved", "All"])
    rows = fetch_items(search_text, type_filter, status_filter)
    if not rows:
        st.info("No matching items yet.")
    else:
        for row in rows:
            item_id, item_type, name, category, location, desc, contact, status, created = row
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(f"**{item_type}: {name}**  ·  `{status}`")
                left.write(f"📍 **Location:** {location}  |  **Category:** {category}")
                if desc:
                    left.write(desc)
                left.caption(f"Contact: {contact} · Posted: {created} · Item ID: {item_id}")
                if status == "Open" and right.button("Mark resolved", key=f"resolve_{item_id}"):
                    resolve_item(item_id)
                    st.rerun()

with tab_add:
    st.subheader("Report a lost or found item")
    with st.form("item_form", clear_on_submit=True):
        item_type = st.radio("Report type", ["Lost", "Found"], horizontal=True)
        item_name = st.text_input("Item name", placeholder="e.g. Blue water bottle")
        category = st.selectbox("Category", ["Electronics", "ID Card", "Bag", "Bottle", "Wallet", "Books", "Keys", "Clothing", "Other"])
        location = st.text_input("Location", placeholder="e.g. Library, Canteen, Room 204")
        description = st.text_area("Description")
        contact = st.text_input("Contact (email or phone)")
        submitted = st.form_submit_button("Submit report", type="primary")
        if submitted:
            if not item_name.strip() or not location.strip() or not contact.strip():
                st.error("Please fill in item name, location, and contact.")
            else:
                add_item(item_type, item_name, category, location, description, contact)
                st.success("Report added successfully!")
                st.rerun()

with tab_ai:
    st.subheader("Ask your database in plain English")
    st.write("Examples: “Show found items near the library” · “Which items are still open?” · “List electronics items.”")
    st.info("AI needs Ollama running locally. Install a model first; instructions are in README.md.")
    question = st.text_input("Your question", placeholder="Show all found items near the library")
    if st.button("Generate SQL and answer", type="primary"):
        if not question.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("Asking the local AI model..."):
                try:
                    answer = ask_ollama(question, model_name.strip() or DEFAULT_MODEL)
                    sql = answer.get("sql", "").strip()
                    explanation = answer.get("explanation", "This query searches the items table.")
                    st.markdown("**AI explanation**")
                    st.write(explanation)
                    st.markdown("**Generated SQL**")
                    st.code(sql, language="sql")
                    columns, result_rows = run_readonly_query(sql)
                    st.markdown("**Database results**")
                    if result_rows:
                        st.dataframe([dict(zip(columns, row)) for row in result_rows], use_container_width=True)
                    else:
                        st.info("The query ran safely, but no matching records were found.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to Ollama. Open Ollama and make sure it is running, then try again.")
                except requests.exceptions.Timeout:
                    st.error("The AI took too long to respond. Try again or use a smaller model.")
                except Exception as exc:
                    st.error(f"Could not complete the query: {exc}")
                    st.caption("Tip: Try a simple question such as “Show all found items near the library.”")

st.divider()
st.caption("Hackathon demo note: sample records are added automatically on first run. Use fictional contact details in demos.")
