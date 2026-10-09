# Stay Updated Current

A production-oriented AI news briefing application that collects recent news from RSS feeds, filters and deduplicates articles, uses LLM-based structured analysis to rank and categorize stories, generates a concise daily briefing, and can deliver the result by email or expose the workflow through a FastAPI service.

The project is also designed as a hands-on AI engineering learning project, covering testing, type checking, linting, security scanning, CI/CD, Docker, API serving, and cloud deployment.

---

## Features

- Fetches articles from multiple RSS feeds
- Normalizes article metadata into a common internal model
- Filters articles by recency
- Removes duplicate URLs
- Supports semantic similarity analysis using sentence-transformers
- Uses OpenAI structured outputs for article analysis
- Scores articles by:
  - relevance
  - importance
  - novelty
- Selects top articles by category
- Generates a structured daily briefing
- Renders the briefing as HTML
- Sends briefings through the Gmail API
- Exposes application functionality through FastAPI
- Supports Docker-based deployment
- Includes automated testing and code-quality checks
- Includes local pre-commit hooks and GitHub Actions CI

---

## Briefing Categories

Articles are classified into the following categories:

1. India
2. Interesting Practices Around the World
3. Stories & Human Experience
4. AI & Technology
5. Education
6. Business & Economics
7. International Relations
8. Books & Ideas
9. Generational Culture
10. Mental Development
11. Other

---

## Architecture

```text
RSS feeds
   ↓
Fetch + normalize
   ↓
Recent article filtering
   ↓
Exact URL deduplication
   ↓
Optional semantic similarity / clustering
   ↓
Batch LLM analysis
   ↓
Structured category + scoring output
   ↓
Deterministic ranking
   ↓
Top article selection
   ↓
Final briefing generation
   ↓
HTML rendering
   ↓
Gmail delivery / FastAPI response
```

The project intentionally separates deterministic processing from LLM-based reasoning.

The LLM performs tasks such as classification and structured content generation, while ranking and selection rules remain explicit in Python.

---

## Technology Stack

### Core

- Python 3.11
- Poetry
- OpenAI Python SDK
- Pydantic
- feedparser
- sentence-transformers
- pandas
- FastAPI
- Uvicorn

### Email

- Gmail API
- Google OAuth 2.0

### Engineering and Quality

- pytest
- pytest-asyncio
- Ruff
- Pyright
- Bandit
- pip-audit
- pre-commit
- GitHub Actions

### Deployment

- Docker
- Render
- AWS planned as a later deployment target

---

## Project Structure

A simplified structure is shown below.

```text
stay_updated_current/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── daily-briefing.yml
│
├── credentials/
│   └── google-credentials.json
│
├── src/
│   ├── api.py
│   ├── processing.py
│   ├── news.py
│   ├── sources.py
│   ├── models.py
│   ├── ranking.py
│   ├── deduplication.py
│   ├── llm.py
│   ├── utils.py
│   ├── logging_config.py
│   ├── email_renderer.py
│   ├── email_service.py
│   └── prompts/
│       ├── article_analysis.py
│       └── daily_briefing.py
│
├── tests/
│
├── .dockerignore
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── poetry.lock
├── pyproject.toml
├── token.json
└── README.md
```

> The exact filenames may evolve as the project is refactored.

---

## Core Data Models

### NewsArticle

Internal normalized article representation.

```python
@dataclass
class NewsArticle:
    title: str
    url: str
    published_at: datetime
    summary: str
    source: str
    embedding_text: str
```

A dataclass is used because this object is primarily internal application data.

### ArticleAnalysis

Structured LLM output is validated using Pydantic.

```python
class ArticleAnalysis(BaseModel):
    article_id: str
    category: ArticleCategory
    importance_score: int = Field(ge=1, le=10)
    relevance_score: int = Field(ge=1, le=10)
    novelty_score: int = Field(ge=1, le=10)
    reason: str
```

Pydantic is used at the LLM boundary because it provides runtime validation and structured schema enforcement.

---

## Article IDs

Each article receives a deterministic ID based on its URL.

```python
import hashlib

def create_article_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()
```

This allows LLM analysis results to be mapped back to their original `NewsArticle` objects.

The application should validate that IDs returned by the LLM exactly match the IDs supplied in the request.

---

## Ranking

Articles are ranked deterministically after LLM analysis.

A representative scoring function is:

```python
def calculate_final_score(analysis: ArticleAnalysis) -> float:
    return (
        0.4 * analysis.relevance_score
        + 0.35 * analysis.importance_score
        + 0.25 * analysis.novelty_score
    )
```

The LLM supplies structured signals, while Python controls the final ranking behavior.

---

## Async LLM Processing

Article batches are processed concurrently using `AsyncOpenAI` and `asyncio`.

Conceptually:

```text
articles
   ↓
create batches
   ↓
async API requests
   ↓
Semaphore limits concurrency
   ↓
structured ArticleAnalysis results
```

A semaphore is used to prevent an uncontrolled number of simultaneous API calls.

Example:

```python
semaphore = asyncio.Semaphore(3)
```

This means no more than three protected LLM operations are allowed to execute concurrently.

---

## RSS Sources

Current or planned sources include:

- Press Information Bureau, India
- The Hindu
- BBC News
- TechCrunch
- Towards Data Science

RSS sources are represented using a small internal model:

```python
@dataclass
class RSSSource:
    name: str
    url: str
```

---

## Environment Setup

### Prerequisites

Install:

- Python 3.11
- Poetry
- Git
- Docker Desktop

Verify:

```bash
python --version
poetry --version
git --version
docker --version
```

---

## Install Dependencies

Clone the repository and enter the project directory.

```bash
git clone <repository-url>
cd stay_updated_current
```

Install dependencies:

```bash
poetry install --no-root
```

This project currently uses Poetry primarily for dependency management rather than as an installable Python package.

---

## Environment Variables

Create a local `.env` file.

```env
OPENAI_API_KEY=your_openai_api_key
BRIEFING_RECIPIENTS=recipient@example.com
```

Never commit `.env`.

Recommended `.gitignore` entries include:

```text
.env
token.json
credentials/
__pycache__/
.pytest_cache/
.ruff_cache/
```

---

## Gmail API Setup

The application uses the Gmail API rather than SMTP.

Required local files:

```text
token.json
credentials/google-credentials.json
```

Typical OAuth scope:

```text
https://www.googleapis.com/auth/gmail.send
```

The credentials and token files must never be committed to Git.

For local Docker usage, they are mounted at runtime rather than copied into the image.

---

## Run the Daily Briefing Pipeline

A typical local execution is:

```bash
poetry run python src/processing.py
```

The pipeline performs:

```text
fetch
→ filter
→ deduplicate
→ analyze
→ rank
→ select
→ generate briefing
→ render HTML
→ send email
```

---

## FastAPI

The project exposes selected functionality through FastAPI.

Start the development API:

```bash
poetry run uvicorn api:app --app-dir src --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically generates interactive OpenAPI documentation.

### Health Endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Example Request Endpoint

```http
POST /echo
```

Example request:

```json
{
  "text": "AI engineering is fun"
}
```

### Article Filtering

```http
POST /articles/filter
```

Example:

```json
{
  "hours": 24
}
```

### Briefing Generation

The application can expose the full asynchronous briefing pipeline through an endpoint such as:

```http
POST /briefing/generate
```

FastAPI should call async pipeline code using `await`, rather than starting a new event loop with `asyncio.run()`.

---

## Testing

Run all tests:

```bash
poetry run pytest
```

The test suite covers areas such as:

- deterministic article ID generation
- batch creation
- recency filtering
- URL deduplication
- ranking
- per-category selection
- mocked OpenAI calls
- mocked Gmail API calls

External services are mocked so that unit tests do not make real API calls.

---

## Code Quality

### Ruff

Check code:

```bash
poetry run ruff check .
```

Auto-fix safe issues:

```bash
poetry run ruff check . --fix
```

Check formatting:

```bash
poetry run ruff format --check .
```

Format code:

```bash
poetry run ruff format .
```

---

## Type Checking

Run Pyright:

```bash
poetry run pyright
```

Pyright helps catch problems such as:

- optional values accessed without checks
- incorrect return types
- invalid argument types
- inconsistent collection types

---

## Security Checks

### Bandit

Bandit scans Python source code for potentially unsafe coding patterns.

```bash
poetry run bandit -r src
```

Examples of issues Bandit may identify include:

- hard-coded secrets
- unsafe `eval`
- insecure subprocess usage
- unsafe deserialization
- weak cryptographic patterns

### pip-audit

`pip-audit` checks installed Python dependencies for known published vulnerabilities.

```bash
poetry run pip-audit
```

Bandit and pip-audit solve different problems:

```text
Bandit
→ scans our source code

pip-audit
→ scans our dependencies
```

---

## Pre-commit Hooks

Local pre-commit hooks run before a Git commit is accepted.

Current checks include:

```text
Ruff
Pyright
pytest
Bandit
```

Install hooks:

```bash
poetry run pre-commit install
```

Run them manually:

```bash
poetry run pre-commit run --all-files
```

A successful run should resemble:

```text
ruff check........................Passed
ruff format.......................Passed
pyright...........................Passed
pytest............................Passed
bandit............................Passed
```

`pip-audit` is intentionally better suited to CI because dependency auditing may be slower than normal local pre-commit checks.

---

## Continuous Integration

GitHub Actions runs independent quality checks after code is pushed.

The CI pipeline includes:

```text
Ruff
Ruff formatting check
Pyright
pytest
Bandit
pip-audit
```

Typical development flow:

```text
write code
   ↓
pre-commit
   ↓
git commit
   ↓
git push
   ↓
GitHub Actions CI
```

This protects the repository even if local hooks are skipped.

---

## Scheduled Briefing

GitHub Actions can also run the briefing on a schedule.

Conceptually:

```text
GitHub Actions cron
   ↓
restore runtime credentials
   ↓
install dependencies
   ↓
run briefing pipeline
   ↓
send Gmail briefing
```

Sensitive values are stored using GitHub Secrets rather than committed files.

Examples:

```text
OPENAI_API_KEY
GMAIL_TOKEN_B64
GMAIL_CREDENTIALS_B64
```

Recipient configuration can be stored as a GitHub Actions variable.

---

## Docker

Build the application image:

```bash
docker build -t stay-updated-current .
```

The image name is arbitrary and does not need to match the Git repository name.

### Docker Architecture

```text
Dockerfile
   ↓
docker build
   ↓
Docker image
   ↓
docker run
   ↓
Container
```

The image contains:

- Python
- application code
- runtime Python dependencies
- startup command

Secrets are not baked into the image.

---

## CPU-only Machine Learning Dependencies

The application performs sentence-transformer inference on CPU.

A CPU-only PyTorch installation is preferred because CUDA-enabled PyTorch dependencies can make Docker images extremely large.

This project previously encountered a dependency layer exceeding 12 GB because CUDA/NVIDIA packages were included unnecessarily.

Production containers should avoid GPU dependencies unless GPU execution is actually required.

---

## Run the Briefing Job in Docker

For local execution:

```powershell
docker run --rm `
  --env-file .env `
  -v "${PWD}\token.json:/app/token.json:ro" `
  -v "${PWD}\credentials:/app/credentials:ro" `
  stay-updated-current
```

Key concepts:

```text
--env-file
→ inject environment variables at runtime

-v
→ mount host files/directories

:ro
→ mount as read-only

--rm
→ delete the stopped container automatically
```

---

## Run FastAPI in Docker

The container can run Uvicorn as its startup process.

Example Docker command:

```dockerfile
CMD uvicorn api:app --app-dir src --host 0.0.0.0 --port ${PORT:-8000}
```

Build:

```bash
docker build -t stay-updated-current .
```

Run:

```powershell
docker run --rm `
  --env-file .env `
  -v "${PWD}\token.json:/app/token.json:ro" `
  -v "${PWD}\credentials:/app/credentials:ro" `
  -p 8000:8000 `
  stay-updated-current
```

Then open:

```text
http://127.0.0.1:8000/docs
```

### Port Mapping

```text
Browser
   ↓
localhost:8000
   ↓
Docker port mapping
   ↓
container:8000
   ↓
Uvicorn
   ↓
FastAPI
```

---

## Runtime Configuration

The Docker image contains application code and dependencies.

Runtime configuration is supplied when the container starts.

```text
Image
→ what the application is

Runtime configuration
→ how this instance should run
```

Examples of runtime configuration include:

- API keys
- recipient lists
- environment names
- logging levels
- file paths
- service configuration

Local development may use `.env`.

CI/CD systems should use secret stores such as GitHub Secrets.

Cloud deployments should use the platform's managed secrets solution.

---

## Logging

The application uses Python's standard logging module.

A typical format is:

```text
timestamp | level | module | message
```

Recommended levels:

```text
DEBUG
→ implementation details

INFO
→ normal pipeline milestones

WARNING
→ recoverable unusual behavior

ERROR
→ operation failed

CRITICAL
→ application cannot continue
```

Application modules should create their own logger:

```python
logger = logging.getLogger(__name__)
```

Logging configuration should be initialized once at the application entry point.

---

## Retry Strategy

Transient OpenAI failures can be retried using Tenacity.

Retry logic should generally target temporary failures such as:

- network connection failures
- timeouts
- rate limits
- temporary server errors

Permanent failures such as authentication or invalid requests should not normally be retried.

Conceptually:

```text
retry
→ WHAT errors qualify

wait
→ HOW LONG between attempts

stop
→ WHEN retries end
```

---

## Security Principles

The project follows several security practices:

- secrets are excluded from Git
- secrets are excluded from Docker images
- Gmail credential files are mounted at runtime
- production secrets should come from managed secret stores
- source code is scanned with Bandit
- dependencies are audited with pip-audit
- CI provides independent verification
- credential files should use the minimum required OAuth scopes

---

## Deployment

### Render

The immediate deployment target is Render.

The planned flow is:

```text
GitHub
   ↓
Dockerfile
   ↓
Render Web Service
   ↓
FastAPI container
   ↓
public HTTPS endpoint
```

Environment variables such as `OPENAI_API_KEY` should be configured through Render rather than committed to the repository.

Secret files such as Gmail credentials should also be supplied at runtime.

The application should bind Uvicorn to:

```text
0.0.0.0
```

and respect the platform-provided `PORT`.

---

## Future AWS Deployment

A future deployment target is AWS using:

```text
Docker image
   ↓
Amazon ECR
   ↓
Amazon ECS
   ↓
AWS Fargate
```

Additional AWS services may include:

- AWS Secrets Manager
- IAM
- CloudWatch
- Application Load Balancer
- EventBridge Scheduler
- Amazon S3

The goal is to progress from a managed PaaS deployment to a more enterprise-oriented cloud container architecture.

---

## Planned Improvements

Potential future improvements include:

- canonical URL normalization
- improved semantic story clustering
- persisted briefing history
- configurable article limits
- API authentication
- structured error responses
- cloud-managed secrets
- deployment health checks
- request tracing
- metrics and observability
- model and prompt evaluation
- retry/error monitoring
- persistent storage
- background job processing
- AWS ECS/Fargate deployment
- automated Docker image publishing
- production CI/CD deployment pipeline

---

## Engineering Philosophy

This project intentionally treats the LLM as one component of a larger software system rather than placing all decision-making inside prompts.

The design favors:

- deterministic preprocessing
- explicit schemas
- runtime validation
- controlled concurrency
- deterministic ranking where possible
- testable business logic
- separation of concerns
- dependency and source-code security checks
- reproducible environments
- automated quality gates

The goal is not only to generate a useful daily briefing, but also to demonstrate the engineering practices required to move an AI application from experimentation toward production.

---

## Development Workflow

```text
Develop
   ↓
pytest
   ↓
Ruff
   ↓
Pyright
   ↓
Bandit
   ↓
pre-commit
   ↓
Git commit
   ↓
GitHub Actions CI
   ↓
Docker
   ↓
FastAPI
   ↓
cloud deployment
```

---

## License

Add an appropriate license before distributing or open-sourcing the project.

For example:

- MIT
- Apache 2.0
- proprietary/internal use

---

## Author

Built as a hands-on AI engineering project focused on combining data science, statistics, LLM systems, software engineering, deployment, and production-quality workflows.
