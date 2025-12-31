Meeting to Action Agent
🧠 Overview

The Meeting to Action Agent is an AI-powered system that analyzes meeting transcripts (from text or uploaded .txt files), extracts action items with assignees and deadlines, and automatically syncs them with Google Calendar.
It can also answer contextual queries like:

What is Arjun’s task?

Who has the nearest deadline?

What did we discuss in the meeting?

What is Riya’s deadline?

Built using FastAPI, Streamlit, LangChain, and Google Generative AI, this agent bridges understanding and execution — turning team discussions into trackable actions.

👨‍💻 Team Members

N. Venkata Durga Karthik

D. Naga Pallavi

J. Sritha Reddy

⚙️ Tech Stack

Backend: FastAPI, Uvicorn

Frontend: Streamlit

AI/NLP: LangChain, Google Generative AI, Sentence Transformers

Calendar Integration: Google Calendar API

Storage & Parsing: FAISS, Dateparser, ics

Environment: Local

🧾 Input Example
{
  "input_mode": "text",
  "meeting_transcript": "Riya will finalize the EcoGlow campaign design...",
  "calendar_sync": true,
  "query": "Who has the nearest deadline?",
  "timezone": "Asia/Kolkata"
}

📤 Output Example
{
  "status": "success",
  "summary": "Meeting focused on finalizing the EcoGlow campaign.",
  "generated_tasks": [...],
  "query_response": {
    "user_query": "Who has the nearest deadline?",
    "answer": "Arjun has the nearest deadline."
  }
}

⚙️ How to Run

Install dependencies

pip install -r requirements.txt


Add your API keys in a .env file:

GOOGLE_API_KEY=AIzaSyAl70VTFyyvsv1LvjtE3swwLu_95057lWM


Run backend (FastAPI):

uvicorn main:app --reload


Run frontend (Streamlit):

streamlit run chat_app.py

🧩 How It Works

Upload or type your meeting transcript in the Streamlit UI.

The backend extracts tasks, deadlines, and people using NLP.

It syncs valid tasks to Google Calendar.

Ask follow-up questions in chat to get task summaries and deadlines.

🏁 License

Licensed under MIT License.