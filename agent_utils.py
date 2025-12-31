import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load Gemini API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_tasks_from_text(transcript: str):
    """
    Uses Gemini to extract action items (who, task, deadline, status)
    from meeting transcripts or notes.
    """
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    prompt = f"""
    You are an AI agent that extracts actionable tasks from meeting notes.
    Return the output in **valid JSON format** as a list of objects with keys:
    person, task, deadline, and status (default status is 'Pending').

    Example:
    Input:
    Riya will finalize the campaign by Friday.
    Arjun to contact vendors tomorrow.

    Output:
    [
      {{"person": "Riya", "task": "Finalize the campaign", "deadline": "Friday", "status": "Pending"}},
      {{"person": "Arjun", "task": "Contact vendors", "deadline": "Tomorrow", "status": "Pending"}}
    ]

    Now extract tasks from this transcript:
    {transcript}
    """

    response = model.generate_content(prompt)
    return response.text.strip()
