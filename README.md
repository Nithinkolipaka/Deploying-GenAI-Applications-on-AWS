# Customer Support QA Evaluator 🤖

An AI-powered tool that automatically scores and evaluates customer support call transcripts using Large Language Models (LLMs). Upload a spreadsheet of call transcripts, and get back quality scores, reasoning, and improvement recommendations — all powered by AI.

---

## What This Project Does

This project reads customer support call transcripts, sends them through an AI pipeline, and produces a scored Excel report with:

- **Call Type Classification** — What kind of call was it? (billing, complaint, etc.)
- **Tone & Empathy Score** — Was the agent polite and caring? (1–5)
- **Knowledge Accuracy Score** — Did the agent give correct information? (1–5)
- **Resolution Quality Score** — Did the agent actually solve the problem? (1–5)
- **Final Summary** — A human-readable performance summary
- **Recommendations** — Specific tips for the agent to improve

---

## Project Structure

```
├── app.py                  # FastAPI web server — run this to start the API
├── main.py                 # Command-line runner — run this for batch processing
├── template.py             # One-time setup script — creates all folders and files
├── dockerfile              # Docker configuration for containerized deployment
├── requirements.txt        # Python dependencies
├── .env                    # Your secret API keys (never commit this to Git!)
│
├── config/
│   └── config.json         # App settings (model names, labels, score range)
│
├── data/
│   └── transcripts.xlsx    # Your input file (call transcripts)
│
├── src/
│   ├── components/
│   │   ├── classification.py   # Classifies each call into a category
│   │   ├── evaluation.py       # Scores tone, knowledge, and resolution
│   │   ├── router.py           # Decides which evaluations to run per call
│   │   └── reporting.py        # Generates final summary and recommendations
│   │
│   ├── pipeline/
│   │   ├── pipeline.py         # Core step-by-step pipeline logic
│   │   └── inference.py        # Full pipeline runner (used by the API)
│   │
│   └── utils/
│       ├── config_loader.py    # Loads .env and config.json
│       ├── data_loader.py      # Reads the transcripts Excel file
│       ├── llm_loader.py       # Connects to OpenAI or Gemini
│       └── helpers.py          # Saves results to Excel
```

---

## Key Libraries & Why We Use Them

### LangChain (`langchain`, `langchain-openai`, `langchain-google-genai`)
**What it is:** A framework for building applications with AI language models.  
**Why we use it:** Instead of writing raw HTTP calls to OpenAI or Gemini, LangChain gives us simple, reusable "chain" objects. You can connect prompts → AI → output parsers in one clean line: `prompt | llm | parser`.  
**Best practice:** Use LangChain when you need structured pipelines, not just single one-off AI calls.

### PromptTemplate
**What it is:** A reusable text template with placeholders like `{transcript}`.  
**Why we use it:** Keeps your prompts consistent across all calls. You define the prompt once and fill in the blanks per call — no duplicated strings.  
**Best practice:** Always use PromptTemplate instead of f-strings for prompts. It makes prompts easier to update and test.

### PydanticOutputParser
**What it is:** A parser that converts AI text output into a typed Python object.  
**Why we use it:** AI models return plain text. PydanticOutputParser tells the AI exactly what format to respond in and then parses the result into a clean Python object with proper types (e.g., `score: int`, `reasoning: str`).  
**Best practice:** Always use structured output parsers in production. They prevent crashes from unexpected AI response formats.

### Pydantic (`BaseModel`, `Field`)
**What it is:** A Python library for data validation and typing.  
**Why we use it:** We define the "shape" of AI output using `BaseModel`. Each field's `description` is sent to the AI, telling it what to fill in. This is how PydanticOutputParser knows what format to expect.  
**When to use:** Use Pydantic whenever you need to guarantee that data has the right types and structure — especially when dealing with AI responses.

### FastAPI
**What it is:** A modern Python web framework for building REST APIs.  
**Why we use it:** FastAPI is fast, easy to use, and automatically generates interactive documentation at `/docs`. It's perfect for wrapping AI pipelines as web APIs.  
**Best practice:** Use FastAPI when you want to expose your AI pipeline as an endpoint that a web app or another service can call.

### CORSMiddleware
**What it is:** Middleware that allows web browsers from other domains to call your API.  
**Why we use it:** By default, browsers block API calls from different domains for security. CORSMiddleware tells browsers it's okay to make these calls.  
**Best practice:** In production, replace `allow_origins=["*"]` with your specific frontend domain URL for better security.

### pandas
**What it is:** A Python library for working with table/spreadsheet data.  
**Why we use it:** We process transcripts row by row and store results as new columns. pandas makes it easy to read Excel files, loop through rows, merge result tables, and save the final output.  
**When to use:** Use pandas whenever you're working with structured, tabular data in Python.

### tqdm
**What it is:** A progress bar library for Python loops.  
**Why we use it:** Processing hundreds of transcripts takes time. tqdm shows a live progress bar in the terminal so you can see how far along the pipeline is.  
**Best practice:** Always add progress bars to long-running loops — it makes the tool much more usable.

### python-dotenv
**What it is:** A library that loads `.env` files into environment variables.  
**Why we use it:** Keeps secret API keys out of your source code. You store keys in a `.env` file locally and `load_dotenv()` makes them accessible via `os.getenv()`.  
**Best practice:** Never hard-code API keys in Python files. Always use environment variables.

---

## Pipeline Flow

```
Input File (CSV / Excel)
        │
        ▼
1. Classification     → What type of call is this? (billing, complaint, etc.)
        │
        ▼
2. Routing            → Which evaluations should run for this call type?
        │
        ▼
3. Evaluations        → Score tone, knowledge accuracy, and resolution quality
        │
        ▼
4. Final Report       → Generate a summary and improvement recommendations
        │
        ▼
Output File (output.xlsx)
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Your API Keys

Copy `.env` and fill in your real credentials:

```env
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini

# OR use OpenAI:
# OPENAI_API_KEY=your_openai_api_key_here
# LLM_PROVIDER=openai
```

> ⚠️ **Never commit your `.env` file to Git.** It is already in `.gitignore`.

### 3. Prepare Your Input File

Place an Excel file at `data/transcripts.xlsx` with these columns:

| call_id | transcript |
|---------|------------|
| CALL001 | Agent: Hello, how can I help? Customer: I have a billing issue... |
| CALL002 | ... |

### 4. Run the Pipeline

**Option A — Command Line (batch processing):**
```bash
python main.py
```
Results are saved to `data/output.xlsx`.

**Option B — Web API:**
```bash
uvicorn app:app --reload
```
Then go to [http://localhost:8000/docs](http://localhost:8000/docs) to use the interactive API.  
Upload a CSV or Excel file via the `/evaluate-file` endpoint and download the result.

---

## Configuration (config/config.json)

```json
{
    "llm": {
        "openai_model": "gpt-4o-mini",
        "gemini_model": "gemini-1.5-flash",
        "temperature": 0.3
    },
    "evaluation": {
        "criteria": ["tone_empathy", "knowledge_accuracy", "resolution_quality"],
        "score_range": [1, 5]
    },
    "classification": {
        "labels": ["billing", "claims", "complaint", "general_query"]
    }
}
```

**`temperature: 0.3`** — Controls how creative the AI is. Lower = more consistent results (better for evaluation tasks). Higher = more varied responses.

---

## Routing Logic

Not every call needs every evaluation. The router assigns only the relevant checks:

| Call Type | Evaluations Run |
|-----------|----------------|
| `billing` | Knowledge Accuracy + Resolution Quality |
| `claims` | Knowledge Accuracy + Resolution Quality |
| `complaint` | Tone & Empathy + Resolution Quality |
| `general_query` | Knowledge Accuracy only |

This keeps costs low and results focused.

---

## Deploying with Docker

### Build the Image
```bash
docker build -t qa-evaluator-app .
```

### Run Locally with Docker
```bash
docker run -p 8000:8000 --env-file .env qa-evaluator-app
```
- `--env-file .env` injects your API keys into the container
- `-p 8000:8000` maps container port 8000 to your local port 8000

### Test It
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

## Deploying to AWS (ECS + Fargate)

The general deployment process is:

1. **Push Docker image to ECR** (Amazon's container registry)
2. **Create an ECS Cluster** using AWS Fargate (no server management needed)
3. **Create a Task Definition** — defines which image to run, how much CPU/memory
4. **Create an ECS Service** — keeps the container running continuously
5. **(Optional) Add a Load Balancer** — gives a stable URL for production use

> See `deployment-guide.txt` for the full step-by-step deployment walkthrough.

**Why AWS Fargate?**  
Fargate is "serverless containers" — AWS manages the servers for you. You only pay for what you use and don't need to manage EC2 instances.

---

## Security Best Practices

- ✅ Add `.env` to `.gitignore` — already done in this project
- ✅ Use `--env-file .env` to inject secrets into Docker — never bake them into the image
- ✅ In production, use **AWS Secrets Manager** instead of a `.env` file
- ✅ Restrict CORS origins to your specific frontend domain in production
- ✅ Use IAM roles with minimum required permissions for your AWS user

---

## Requirements

```
langchain
langchain-openai
langchain-google-genai
python-dotenv
pandas
openpyxl
pydantic
fastapi
uvicorn
python-multipart
tqdm
```