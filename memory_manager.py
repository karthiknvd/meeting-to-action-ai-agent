import faiss
import pickle
import numpy as np
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import google.generativeai as genai  # 🧠 For natural rephrasing

load_dotenv()  # Load .env file (for GEMINI_API_KEY)


# ✅ Cache heavy models so they load only once per session
@st.cache_resource(show_spinner=False)
def get_embeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """Load and cache Hugging Face embeddings model."""
    return HuggingFaceEmbeddings(model_name=model_name)


@st.cache_resource(show_spinner=False)
def load_faiss_memory(db_path="vector_store.faiss"):
    """Load FAISS index and memory texts with caching."""
    try:
        index = faiss.read_index(db_path)
        with open("memory_texts.pkl", "rb") as f:
            texts = pickle.load(f)
        return index, texts
    except Exception:
        # Create new FAISS index if files not found
        return faiss.IndexFlatL2(384), []


class ChatMemory:
    def __init__(self, db_path="vector_store.faiss", embed_model="sentence-transformers/all-MiniLM-L6-v2"):
        # ✅ Cached resources
        self.db_path = db_path
        self.embeddings = get_embeddings(embed_model)
        self.index, self.texts = load_faiss_memory(db_path)

        # ✅ Lazy Gemini initialization
        self.model = None
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)

    def _save(self):
        """Save FAISS index and memory texts."""
        try:
            faiss.write_index(self.index, self.db_path)
            with open("memory_texts.pkl", "wb") as f:
                pickle.dump(self.texts, f)
        except Exception as e:
            print(f"⚠️ Warning: Failed to save memory - {e}")

    def add(self, text):
        """Add a chat message or meeting summary to memory."""
        if not text.strip():
            return

        # 🧠 Fix: replace pronouns like "I’ll" or "I'll" with the last mentioned name
        lines = text.split("\n")
        last_speaker = None
        fixed_lines = []
        for line in lines:
            # Detect who’s speaking
            if "→" in line or ":" in line:
                if ":" in line:
                    last_speaker = line.split(":")[0].strip()
                elif "→" in line:
                    last_speaker = line.split("→")[0].strip()

            # Replace “I’ll” or “I will” with the speaker’s name
            if last_speaker and any(word in line.lower() for word in ["i'll", "i’ll", "i will"]):
                line = line.replace("I’ll", f"{last_speaker} will").replace("I'll", f"{last_speaker} will").replace(
                    "I will", f"{last_speaker} will")

            fixed_lines.append(line)

        fixed_text = "\n".join(fixed_lines)

        # Continue the usual embedding process
        embedding = np.array(self.embeddings.embed_query(fixed_text)).astype("float32").reshape(1, -1)
        self.index.add(embedding)
        self.texts.append(fixed_text)
        self._save()

    def retrieve(self, query: str, top_k=3):
        """Retrieve relevant past context and rephrase naturally."""
        if not self.texts:
            return "I don’t have any prior memory yet."

        # Step 1: Search FAISS for top-k results
        query_vector = np.array(self.embeddings.embed_query(query)).astype("float32").reshape(1, -1)
        distances, indices = self.index.search(query_vector, top_k)
        results = [self.texts[i] for i in indices[0] if i < len(self.texts)]
        results = list(dict.fromkeys(results))  # Remove duplicates

        # Step 2: Extract relevant lines
        filtered_lines = []
        query_words = query.lower().split()

        for r in results:
            for line in r.split("\n"):
                line_lower = line.lower()
                # Skip irrelevant headers
                if line_lower.startswith(("meeting summary", "tasks:")):
                    continue
                # Match words
                if any(word in line_lower for word in query_words):
                    filtered_lines.append(line.strip())
                # Smart deadline filter
                if "deadline" in query.lower() and any(x in line_lower for x in ["(", "deadline", "by", "due"]):
                    if line not in filtered_lines:
                        filtered_lines.append(line.strip())

        # Step 3: Fallback if no direct matches
        if not filtered_lines:
            for r in results:
                for line in r.split("\n"):
                    if not line.lower().startswith(("meeting summary", "tasks:")):
                        filtered_lines.append(line.strip())
            if not filtered_lines:
                return "I searched my memory but couldn’t find anything specific about that."

        combined_text = "\n".join(filtered_lines[:3])

        # Step 4: Rephrase naturally with Gemini (lazy-loaded)
        try:
            if self.model is None:
                self.model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = (
                "You are a professional meeting assistant. Read the context below and answer the user's question "
                "in **one short, clear, natural sentence only.** "
                "Avoid lists, options, or restating the question.\n\n"
                f"Question: {query}\n"
                f"Context:\n{combined_text}"
            )

            response = self.model.generate_content(prompt)
            clean_reply = response.text.strip() if response.text else combined_text

            # Step 5: Final cleanup
            bad_phrases = [
                "Option", "option", "suggestion", "example",
                "Here are", "Here’s", "Alternative", "Let's refine"
            ]
            for phrase in bad_phrases:
                if phrase in clean_reply:
                    clean_reply = clean_reply.split("\n")[0].strip()

            return clean_reply.split("\n")[0].strip()  # Keep only first line
        except Exception:
            return combined_text
