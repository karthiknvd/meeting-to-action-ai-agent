# 🧠 Meeting to Action Agent

## 📌 Overview

**Meeting to Action Agent** is an AI-powered system that transforms meeting discussions into **structured action items** and seamlessly syncs them with **Google Calendar**.

It analyzes meeting transcripts (entered as text or uploaded as `.txt` files), extracts **tasks, assignees, and deadlines**, and enables users to ask **context-aware follow-up questions** such as:

* *What is Arjun’s task?*
* *Who has the nearest deadline?*
* *What did we discuss in the meeting?*
* *What is Riya’s deadline?*

Built using **FastAPI**, **Streamlit**, **LangChain**, and **Google Generative AI**, this project bridges the gap between **discussion and execution**, turning meetings into actionable, trackable outcomes.

---

## 👨‍💻 Team Members

* **N. Venkata Durga Karthik** — Backend Development & AI Integration
* **D. Naga Pallavi** — Frontend Development (Streamlit UI)
* **J. Sritha Reddy** — API Integration & LLM-based Text Processing

---

## ⚙️ Tech Stack

### Backend

* FastAPI
* Uvicorn

### Frontend

* Streamlit

### AI & Text Processing

* LangChain
* Google Generative AI
* Sentence Transformers

### Calendar Integration

* Google Calendar API

### Storage & Parsing

* FAISS
* Dateparser
* `ics`

### Environment

* Local Development

---

## 🧾 Input Example

```json
{
  "input_mode": "text",
  "meeting_transcript": "Riya will finalize the EcoGlow campaign design by Friday. Arjun will prepare the budget proposal by Wednesday.",
  "calendar_sync": true,
  "query": "Who has the nearest deadline?",
  "timezone": "Asia/Kolkata"
}
```

---

## 📤 Output Example

```json
{
  "status": "success",
  "summary": "Meeting focused on finalizing the EcoGlow campaign and budget planning.",
  "generated_tasks": [
    {
      "assignee": "Arjun",
      "task": "Prepare the budget proposal",
      "deadline": "Wednesday"
    },
    {
      "assignee": "Riya",
      "task": "Finalize the EcoGlow campaign design",
      "deadline": "Friday"
    }
  ],
  "query_response": {
    "user_query": "Who has the nearest deadline?",
    "answer": "Arjun has the nearest deadline."
  }
}
```

---

## ⚙️ How to Run

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY = YOUR_GEMINI_API_KEY
```

> ⚠️ **Do not commit your `.env` or credential files to GitHub**

---

### 3️⃣ Run Backend (FastAPI)

```bash
uvicorn main:app --reload
```

---

### 4️⃣ Run Frontend (Streamlit)

```bash
streamlit run chat_app.py
```

---

## 🧩 How It Works

1. Users upload or paste meeting transcripts via the Streamlit interface.
2. The FastAPI backend processes the text using **LLM-based analysis**.
3. Tasks, assignees, and deadlines are extracted and structured.
4. Valid tasks are optionally synced to **Google Calendar**.
5. Users can ask follow-up questions to retrieve summaries, responsibilities, and deadlines.

---

## 🔐 Security Notes

* OAuth credentials and API keys are **not included** in the repository.
* Sensitive files are managed using `.env` and `credentials.json`.
* Only example configuration files are committed.

---

## 🏁 License

This is an open-source project, and contributions, experimentation, and learning are welcome.
