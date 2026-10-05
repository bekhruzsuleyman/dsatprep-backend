from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import SolveRequest, SolveResult
from engine import AIEngine
from prompts import SYSTEM_INSTRUCTION, dsat_solve_prompt
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
aiengine = AIEngine(api_key=os.getenv("GEMINI_API_KEY"), system_instructions=SYSTEM_INSTRUCTION)

DEFAULT_ALLOWED_ORIGINS = "https://dsatprep-frontend.vercel.app,http://localhost:3000"
origins = [
    origin.strip()
    for origin in (os.getenv("ALLOWED_ORIGINS") or DEFAULT_ALLOWED_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"product": "Welcome to DSAT AI Platform!"}

@app.post("/solve/")
async def solve_request(solve_request: SolveRequest):
    generated_prompt = dsat_solve_prompt(solve_request)

    result = aiengine.generate_content(
        prompt=generated_prompt,
        output_model=SolveResult
    )

    return result

@app.get("/attempts/")
async def attempts():
    # Placeholder: attempt history is not stored yet, so this always returns an empty list.
    return {"attempts": []}

if __name__ == "__main__":
    pass