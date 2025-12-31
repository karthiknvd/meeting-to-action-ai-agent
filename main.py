from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent_utils import extract_tasks_from_text

app = FastAPI(title="Meeting-to-Action Agent")

# CORS setup (so Streamlit or any frontend can call it later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Meeting-to-Action Agent backend is running ✅"}


@app.post("/extract_tasks")
async def extract_tasks(request: Request):
    """
    API endpoint to extract tasks from meeting transcripts
    """
    data = await request.json()
    transcript = data.get("transcript", "")
    if not transcript:
        return {"error": "No transcript provided!"}

    try:
        extracted = extract_tasks_from_text(transcript)
        return {"tasks": extracted}
    except Exception as e:
        return {"error": str(e)}
