# OBELISK: Trans-model, self-adaptive multi-agent development OS

This project defines an agent system that automates creating complete software stacks:

- **Code Architect**: Uses the Anthropic API to generate high-level architecture plans.
- **Code Generator**: Invokes the Codex CLI to scaffold code based on the architecture plan.
- **Quality Checker**: Uses the OpenAI API to perform QA on the generated code.
- **Test Harness Agent**: Uses the OpenAI API to automatically generate pytest test files for the generated code.
- **Ideas Agent**: Uses the OpenAI API to brainstorm new features and improvements.
- **Creativity Agent**: Uses the Anthropic API to review and refine brainstormed ideas.
- **Self-Scoring Agent**: Uses the OpenAI API to evaluate generated outputs (code or text), assign a quality score and confidence level, and suggest concrete improvements.

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install and run `pre-commit` hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```
4. Copy `.env.example` to `.env` and populate with your API keys, Codex CLI path, and LLAMA_MODEL_PATH.
5. (Optional) Run the LLaMA setup script to download and configure a base model:
   ```bash
   scripts/setup_llama.py --model decapoda-research/llama-7b-hf --dest ./models/llama
   ```

## Usage

```bash
python main.py \
  --project "MyApp" \
  --requirements "High-level requirements" \
  --output-dir ./output \
  --architect-model claude-v1|lmstudio|llama \
  --ideas-model gpt-4|gpt-3.5-turbo|llama|lmstudio \
  --creativity-model claude-v1|lmstudio|llama \
  --qc-model gpt-4|gpt-3.5-turbo|llama|lmstudio \
  [--generate-tests] [--test-harness-model gpt-4] \
  [--sandbox] [--sandbox-docker-image my/image:tag] [--test-command "pytest --maxfail=1"]
```

At startup, the program will check access to each LLM and print availability (green = available, red = unavailable).

## Project Analysis Script

You can run a standalone project analysis to generate a JSON report via Anthropic:

```bash
scripts/analyze_project.py --model claude-v1 --output report.json
```

Alternatively, integrate analysis directly into the main workflow by passing
the report path with `--analysis-report`, which invokes Codex CLI to apply
suggested improvements:

## Prompt System

A flexible prompt template engine is provided via `agent_system/prompt_system.py`. Define
structured prompts in `config/task_templates.yaml` (override via `PROMPT_TEMPLATES_PATH`);
agents will load their templates for each action and render them with parameters. Edit the
YAML file to customize agent behavior without code changes.

## Agent Registry & Plugin API

Agent implementations are now pluggable via `config/agents.yaml`, loaded by `agent_system/agent_registry.py`.
You can add or swap core agents via `config/agents.yaml` and third‑party plugins via
`config/plugins.yaml`. Both are loaded by `agent_system/agent_registry.py` (plugins via
`agent_system/plugin_manager.py`). Edit these YAML files to extend OBELISK without code.

## Phase 2: FastAPI Service

We now offer a minimal FastAPI service in `service/api.py` for submitting tasks and viewing memory:

```bash
uvicorn service.api:app --reload
```

### Web Dashboard

Browse to http://localhost:5174 to access the React-based dashboard. The dashboard now supports:
- Submitting tasks and viewing live status/results
- Refreshable Task History table via `/tasks_all`
- Real-time log streaming via WebSocket at `/ws/logs`

```bash
cd web && npm install && npm run dev
```
Ensure you have Node.js and npm installed. The `start_all.sh` script will
automatically install these dependencies if `node_modules` is missing.

### Redis Requirement

Celery relies on Redis as its message broker and result backend. Make sure a
`redis-server` is installed and running on `localhost:6379` before starting the
API or worker processes. The `start_all.sh` script will try to launch Redis
automatically if the command is available. On Ubuntu you can install it via
`sudo apt-get install redis-server`; on macOS use `brew install redis`.

### Unified Startup Script

Instead of managing multiple terminals, use the provided `start_all.sh` script at the project root:
```bash
chmod +x start_all.sh
./start_all.sh
```

This will launch the API, Celery worker, Celery beat scheduler, and the React dashboard.
If Node dependencies are missing, the script installs them automatically before starting Vite.
Your browser will open to `http://localhost:5174` and logs will stream via WebSocket.

### Running Celery Worker

```bash
chmod +x service/celery_worker.sh
service/celery_worker.sh
```

### Celery Beat (Periodic Tasks)

Run the Celery scheduler to invoke MetaAgent periodically:
```bash
celery -A service.celery_app.celery_app beat --loglevel=info
```

Endpoints:
- `POST /tasks` to enqueue an agent task (specify `agent` and `params` JSON); returns a task ID immediately.
- `GET /tasks/{id}` to check status/result.
- `GET /memory/{agent_name}` to retrieve recent memory entries.
- `GET /healthz` for a simple health check.
- `GET /version` to retrieve the running commit hash.

## Prompt Chaining & Reasoning Logs

Agents can log intermediate reasoning steps via `agent_system/logging.py` (backed by Memory).
This enables prompt‑chaining and inspection of each agent’s thought process.

## Vector Store Integration

For semantic memory, see `agent_system/vector_memory.py`, a FAISS wrapper. Install `faiss-cpu`
and set `VECTOR_INDEX_PATH` to enable embedding-based recall.


## Relational & Vector Memory

Memory now supports SQLAlchemy-backed relational stores (MySQL/PostgreSQL) via the `RELATIONAL_DSN`
environment variable, or falls back to SQLite (`MEMORY_DB_PATH`). Vector store integration coming soon.

## Validation Stage

Optionally run code validation (`pylint` and `black --check`) after generation with `--validate`,
and pass additional flags via `--validate-flags`.

## Natural-Language CLI

You can invoke OBELISK directly with free-form commands via the `obelisk` script:

```bash
./obelisk.py "Generate a Flask microservice with JWT auth and SQLite ORM"
```

The CLI will auto-classify your request (Architect, Ideas, etc.) and route it appropriately.

```bash
python main.py \
  --project "MyApp" \
  --requirements "..." \
  --output-dir ./output \
  --architect-model llama \
  --ideas-model gpt-4 \
  --creativity-model claude-v1 \
  --qc-model gpt-4 \
  --analysis-report report.json
```

### Memory (optional)

You can enable persistent memory of all agent actions and outputs via SQLite:

```bash
python main.py \
  --project "MyApp" \
  --requirements "..." \
  --output-dir ./output \
  --architect-model llama \
  --ideas-model gpt-4 \
  --creativity-model claude-v1 \
  --qc-model gpt-4 \
  --use-memory \
  --memory-db ./memory.sqlite
```

This stores each agent’s decisions and content in the specified SQLite DB (`MEMORY_DB_PATH` if not overridden).

### Task Router (Intelligent dispatch)

The Task Router can automatically send a high-level task description to the appropriate engine (Claude, Codex, or ChatGPT) based on simple heuristics:

```python
from agent_system.task_router import TaskRouter

router = TaskRouter(
    anthro_model="claude-v1",
    openai_model="gpt-4",
    codex_cli_path="/path/to/codex"
)

# Automatic routing by keyword:
response = router.route_task("Design a microservices architecture for MyApp")
print(response)  # handled by Claude

response = router.route_task("Generate code for the REST API endpoints", spec=spec, output_dir="./services")
print(response)  # handled by Codex CLI

response = router.route_task("Explain security best practices in Python code")
print(response)  # handled by ChatGPT
```

This will scan code under the current directory, send it to Anthropic for review, and produce
a JSON report (`summary` and per-file `issues`) that Codex or other tools can ingest for
automated code improvements.

Run `python main.py --help` for more options, including sandbox test execution.
