# DSAT Prep – Backend

FastAPI service behind an AI-assisted practice tool for the Digital SAT (DSAT).
A student pastes a DSAT question (and optionally their answer); the service asks
Google Gemini to solve it and returns a structured analysis: the section, the
question type, the correct choice, a short explanation, whether the student's
answer was right, the main "trap" the question sets, and a confidence score.

- Live app: https://dsatprep-frontend.vercel.app
- Frontend repo: https://github.com/bekhruzsuleyman/dsatprep-frontend

## Architecture

```
Next.js frontend ──POST /solve/──▶ FastAPI (main.py)
                                      │
                                      ├─ prompts.py   builds the prompt + system instruction
                                      ├─ engine.py    AIEngine: thin wrapper over google-genai
                                      │                (model: gemini-2.5-flash-lite)
                                      └─ schemas.py   Pydantic request/response models
```

- **main.py** defines the FastAPI app, CORS settings and routes.
- **prompts.py** holds the system instruction (a "DSAT mentor" with separate
  reasoning rules for English and Math) and `dsat_solve_prompt()`, which turns a
  `SolveRequest` into the user prompt.
- **engine.py** contains `AIEngine`, which calls Gemini with
  `response_mime_type="application/json"` and `response_schema=<Pydantic model>`,
  then validates the reply with `model_validate_json`. Gemini's structured-output
  mode constrains the answer to the schema, and Pydantic rejects anything that
  still doesn't fit.
- **schemas.py** defines the contract:
  - `SolveRequest`: `questionText` (≤ 2000 chars) and/or `questionImgRef`
    (at least one is required), optional `userAnswer`, `requestedAt`.
  - `SolveResult`: `section` (`english` | `math`), `questionType` (e.g.
    `inference`, `transition`, `quadratic`, `geometry`), `correctChoice`,
    `explanation` (≤ 500 chars), `wasUserCorrect` (`Correct` | `Incorrect` |
    `Neutral`), `trapType` (e.g. `too_broad`, `sign_error`), `confidence` (0–100).
  - `Attempt` / `AttemptPreview`: models for a future attempt history; not used
    by any route yet.

There is no database; the service is stateless.

## API

| Method | Path         | Description |
|--------|--------------|-------------|
| GET    | `/`          | Health/welcome message: `{"product": "Welcome to DSAT AI Platform!"}` |
| POST   | `/solve/`    | Body: `SolveRequest` JSON. Returns a `SolveResult`. Returns 422 if neither `questionText` nor `questionImgRef` is given. |
| GET    | `/attempts/` | Placeholder. Always returns `{"attempts": []}`; attempts are not stored yet. |

FastAPI also serves interactive docs at `/docs` (Swagger UI) and `/redoc`.

Example:

```bash
curl -X POST http://localhost:8000/solve/ \
  -H "Content-Type: application/json" \
  -d '{"questionText": "If 3x + 5 = 20, what is x?\nA) 3  B) 5  C) 15  D) 25", "userAnswer": "B"}'
```

## Configuration

Copy `.env.example` to `.env` and fill it in (`.env` is git-ignored):

| Variable          | Required | Description |
|-------------------|----------|-------------|
| `GEMINI_API_KEY`  | yes      | Google Gemini API key. |
| `ALLOWED_ORIGINS` | no       | Comma-separated list of origins allowed by CORS. Defaults to `https://dsatprep-frontend.vercel.app,http://localhost:3000`. |

## Run locally

Requires Python 3.10+ (the Docker image uses 3.14).

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then set GEMINI_API_KEY
uvicorn main:app --reload         # http://localhost:8000
```

The Docker image runs the same app with
`uvicorn main:app --host 0.0.0.0 --port 10000`.

## Docker

```bash
docker build -t dsatprep-backend .
docker run --rm -p 10000:10000 --env-file .env dsatprep-backend
# http://localhost:10000
```

The production instance used by the live frontend is hosted at
`https://dsatprep-backend.onrender.com`.

## Status / next steps

This is an early, working prototype. What exists today is the single
solve-and-explain flow. Not yet built:

- **Attempt history.** `/attempts/` is a stub and `Attempt` / `AttemptPreview`
  in `schemas.py` are unused; storing attempts needs a database and some notion
  of a user.
- **Image questions.** `questionImgRef` is accepted, but it is only inserted into
  the prompt as text; no image is sent to the model.
- **Error handling.** If the Gemini call fails or returns JSON that doesn't match
  `SolveResult`, the exception is not caught and the client gets a 500.
- **Tests.** There is no test suite yet.
- **Abuse protection.** `/solve/` has no authentication or rate limiting, so
  anyone who can reach it spends the API key's quota.
