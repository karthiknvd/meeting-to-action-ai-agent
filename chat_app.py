import streamlit as st
import requests
import json
import os
import time
import datetime
import dateparser
from google_calendar import add_event_to_calendar
from memory_manager import ChatMemory  # 🧠 Import your memory system

# ---------------------
# CONFIG
# ---------------------
API_URL = "http://127.0.0.1:8000/extract_tasks"
st.set_page_config(page_title="AI Meeting Assistant", page_icon="💬", layout="wide")

st.title("💬 AI Meeting Assistant")
st.write("Chat with your AI assistant to analyze meeting transcripts, auto-schedule tasks, and even remember previous conversations!")

# ---------------------
# 🧠 MEMORY CONTROLS SIDEBAR
# ---------------------
st.sidebar.header("🧠 Memory Controls")

if st.sidebar.button("🧹 Clear All Memory"):
    try:
        if os.path.exists("vector_store.faiss"):
            os.remove("vector_store.faiss")
        if os.path.exists("memory_texts.pkl"):
            os.remove("memory_texts.pkl")

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        with st.spinner("🧠 Wiping memory banks..."):
            time.sleep(1)

        st.success("✅ Memory cleared successfully! Reloading app...")
        time.sleep(1)

        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

    except Exception:
        pass  # no need to show any error


# ---------------------
# SESSION STATE
# ---------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_tasks" not in st.session_state:
    st.session_state["last_tasks"] = []


# ✅ Cached memory initialization
@st.cache_resource(show_spinner=False)
def get_memory():
    return ChatMemory()

if "memory" not in st.session_state:
    with st.spinner("⚙️ Loading AI memory system..."):
        st.session_state["memory"] = get_memory()


# ✅ Cached API call for faster response on same text
@st.cache_data(show_spinner=False)
def analyze_transcript_cached(transcript: str):
    """Cached API call to prevent repeated identical processing."""
    response = requests.post(API_URL, json={"transcript": transcript})
    return response.json()


# ✅ Cached parsing of task data (since it's done often)
@st.cache_data(show_spinner=False)
def parse_tasks_data(tasks_raw):
    """Safely parse task JSONs and cache results."""
    if isinstance(tasks_raw, str):
        try:
            cleaned = tasks_raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`").replace("json", "", 1).strip()
            tasks = json.loads(cleaned)
        except Exception:
            tasks = []
    elif isinstance(tasks_raw, list):
        tasks = tasks_raw
    else:
        tasks = []
    return tasks


# ---------------------
# 📄 FILE UPLOAD OPTION
# ---------------------
st.subheader("📁 Upload Meeting Transcript (Optional)")

uploaded_file = st.file_uploader(
    "Upload a `.txt` meeting transcript file:",
    type=["txt"],
    help="You can upload your meeting transcript here. It will be automatically analyzed."
)

if uploaded_file is not None:
    try:
        transcript_text = uploaded_file.read().decode("utf-8").strip()

        if transcript_text:
            st.success("✅ File uploaded successfully! Analyzing it now...")

            with st.expander("📝 View Transcript Preview"):
                st.text_area("Transcript Preview", transcript_text, height=200, disabled=True)

            with st.spinner("Analyzing meeting transcript from file... 🤖"):
                data = analyze_transcript_cached(transcript_text)

                if "error" in data:
                    st.error(f"⚠️ Error: {data['error']}")
                else:
                    summary = data.get("summary", "Here's what I understood from your meeting.")
                    tasks = parse_tasks_data(data.get("tasks", []))

                    st.session_state["last_tasks"] = tasks

                    # 🧠 Add to memory
                    if tasks:
                        memory_text = f"Meeting Summary: {summary}\nTasks:\n"
                        for t in tasks:
                            memory_text += f"{t.get('person', 'Someone')} → {t.get('task', '')} (Deadline: {t.get('deadline', 'N/A')})\n"
                        st.session_state["memory"].add(memory_text)
                        st.success("💾 Meeting has been added to memory successfully!")

                    st.write("### 🧠 Summary:")
                    st.write(summary)

                    if tasks:
                        st.write("### 🧾 Extracted Tasks:")
                        st.table(tasks)
                        st.info("✅ You can now ask questions like *'Who has the nearest deadline?'* or *'Add the tasks to the Google Calendar'*")
                    else:
                        st.warning("No clear tasks found. Try a more detailed transcript.")
        else:
            st.warning("⚠️ Uploaded file is empty. Please check and try again.")
    except Exception as e:
        st.error(f"Error reading file: {e}")


# ---------------------
# DISPLAY CHAT HISTORY
# ---------------------
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------------
# INPUT BOX
# ---------------------
if prompt := st.chat_input("Paste your meeting transcript, ask about tasks, or say hi..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    user_text = prompt.lower().strip()

    # ✅ CASE 0: Greeting detection
    greetings = ["hi", "hello", "hey", "yo", "sup", "good morning", "good evening", "good afternoon"]
    if user_text in greetings:
        reply = (
            "👋 Hey there! I’m your **Meeting AI Assistant**.\n\n"
            "You can **paste or upload** your meeting transcript and I’ll analyze it — "
            "summarizing key points, extracting tasks, and remembering them for later 🧠\n\n"
            "Once ready, I can even add them directly to your Google Calendar automatically 📅✨"
        )
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ CASE 1: Add tasks to Google Calendar
    elif user_text in ["yes", "add", "yes please", "add to calendar", "sure", "confirm"]:
        if st.session_state["last_tasks"]:
            reply = "📅 Adding your tasks to Google Calendar...\n\n"
            success = 0
            for task in st.session_state["last_tasks"]:
                try:
                    person = task.get("person", "Someone")
                    desc = task.get("task", "No description")
                    deadline = task.get("deadline", "tomorrow")

                    parsed_date = dateparser.parse(deadline, settings={"PREFER_DATES_FROM": "future"})
                    if not parsed_date:
                        parsed_date = datetime.datetime.now() + datetime.timedelta(days=1)

                    summary = f"{person} - {desc}"
                    event_link = add_event_to_calendar(summary, "Task assigned by AI agent", parsed_date)
                    reply += f"✅ {summary} — [View Event]({event_link})\n"
                    success += 1
                except Exception as e:
                    reply += f"⚠️ Failed to add task: {e}\n"

            reply += f"\n🎉 Successfully added {success} tasks to Google Calendar!"
        else:
            reply = "⚠️ No tasks available to add. Please share a meeting transcript first."
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ CASE 2: Memory retrieval queries
    elif any(word in user_text.split() for word in ["what", "who", "when", "show", "list", "remind", "task", "deadline"]) and len(user_text.split()) < 15:
        result = st.session_state["memory"].retrieve(user_text)
        reply = f"🧠 Based on my memory:\n\n{result}"
        st.session_state["messages"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # ✅ CASE 3: Normal chat/transcript input
    else:
        with st.spinner("Analyzing your meeting transcript... 🤖"):
            try:
                data = analyze_transcript_cached(prompt)

                if "error" in data:
                    reply = f"⚠️ Error: {data['error']}"
                else:
                    summary = data.get("summary", "Here's what I understood from your meeting.")
                    tasks = parse_tasks_data(data.get("tasks", []))
                    st.session_state["last_tasks"] = tasks

                    if tasks:
                        memory_text = f"Meeting Summary: {summary}\nTasks:\n"
                        for t in tasks:
                            memory_text += f"{t.get('person', 'Someone')} → {t.get('task', '')} (Deadline: {t.get('deadline', 'N/A')})\n"
                        st.session_state["memory"].add(memory_text)
                        memory_note = "💾 Got it! I’ve saved this meeting in my memory."
                    else:
                        memory_note = ""

                    reply = f"**🧠 Summary:**\n{summary}\n\n"
                    if tasks:
                        reply += "**🧾 Extracted Tasks:**\n"
                        for t in tasks:
                            if isinstance(t, dict):
                                reply += f"- {t.get('person', 'Someone')} → {t.get('task', '')} (Deadline: {t.get('deadline', 'N/A')})\n"
                        reply += f"\n{memory_note}\n✅ Shall I add these tasks to your Google Calendar?"
                    else:
                        reply += "_No clear tasks found in this transcript._"

                st.session_state["messages"].append({"role": "assistant", "content": reply})
                with st.chat_message("assistant"):
                    st.markdown(reply)
            except Exception as e:
                error_msg = f"Request failed: {e}"
                st.session_state["messages"].append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.error(error_msg)
