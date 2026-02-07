# Architecture & Schema Reference

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Dashboard | Test Runner | Leaderboard | Drift Monitor   │   │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ POST /api/v1/inference/run                               │   │
│  │ GET  /api/v1/traces/{trace_id}                          │   │
│  │ GET  /api/v1/prompts/{prompt_id}/metrics               │   │
│  │ GET  /api/v1/leaderboard                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ↓                 ↓                 ↓
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Inference    │  │ Evaluation   │  │ Prompt       │
    │ Service      │  │ Service      │  │ Service      │
    └──────────────┘  └──────────────┘  └──────────────┘
           ├                 ├                 ├
           └─────────────────┼─────────────────┘
                             ↓
    ┌────────────────────────────────────────────┐
    │        LLM Providers (Abstract)             │
    │  ┌──────────────────────────────────────┐  │
    │  │ • MockProvider                       │  │
    │  │ • OpenAIProvider                     │  │
    │  │ • AnthropicProvider (coming)        │  │
    │  │ • GeminiProvider (coming)           │  │
    │  │ • OllamaProvider (coming)           │  │
    │  └──────────────────────────────────────┘  │
    └────────────────────────────────────────────┘
           │        │        │         │
           ↓        ↓        ↓         ↓
          API      API      API       Local
        (OpenAI) (Anthropic) (Google) (Ollama)
```

---

## Database Schema

### Core Tables

```sql
-- Prompts (Manages versions)
CREATE TABLE prompts (
    id UUID PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR,
    created_at DATETIME,
    updated_at DATETIME
);

-- Prompt Versions (Semantic versioning)
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY,
    prompt_id UUID NOT NULL REFERENCES prompts(id),
    version VARCHAR NOT NULL,  -- "1.0.0", "1.1.0", etc.
    system_template TEXT,
    user_template TEXT NOT NULL,
    llm_config JSONB NOT NULL,  -- {"provider": "openai", "model": "gpt-4", ...}
    author VARCHAR,
    created_at DATETIME,
    is_active BOOLEAN DEFAULT FALSE,
    UNIQUE(prompt_id, version)
);

-- Inference Traces (TimescaleDB Hypertable)
CREATE TABLE inference_traces (
    trace_id UUID PRIMARY KEY,
    prompt_version_id UUID NOT NULL REFERENCES prompt_versions(id),
    inputs JSONB NOT NULL,          -- {"name": "Alice", "topic": "Python"}
    output TEXT NOT NULL,            -- LLM output
    tokens_in INT NOT NULL,
    tokens_out INT NOT NULL,
    latency_ms INT NOT NULL,
    cost_usd DECIMAL(10,6) NOT NULL,
    model VARCHAR NOT NULL,          -- "gpt-4-turbo"
    timestamp DATETIME(TZ) NOT NULL  -- REQUIRED for TimescaleDB partitioning
);
CREATE INDEX idx_traces_prompt_version_timestamp 
    ON inference_traces (prompt_version_id, timestamp DESC);
CREATE INDEX idx_traces_timestamp 
    ON inference_traces (timestamp DESC);

-- Evaluation Results (TimescaleDB Hypertable)
CREATE TABLE evaluation_results (
    eval_id UUID PRIMARY KEY,
    trace_id UUID NOT NULL REFERENCES inference_traces(trace_id),
    evaluator_id VARCHAR NOT NULL,  -- "judge-gpt4", "hallucination-detector"
    scores JSONB NOT NULL,          -- {"correctness": 8, "completeness": 7, ...}
    overall_score FLOAT NOT NULL,   -- 0-10 aggregate
    reasoning TEXT NOT NULL,        -- Explanation from evaluator
    timestamp DATETIME(TZ) NOT NULL -- REQUIRED for TimescaleDB
);
CREATE INDEX idx_evals_trace_id ON evaluation_results (trace_id);
CREATE INDEX idx_evals_evaluator_id ON evaluation_results (evaluator_id);
CREATE INDEX idx_evals_timestamp ON evaluation_results (timestamp DESC);
```

---

## Data Relationships

```
Prompts (1) ──→ (many) PromptVersions
    ↑
    │
    └─── managed via CRUD.prompt ──→ (many) InferenceTraces
                                              ↓
                                              │
                                              ├─→ stores: inputs, output, 
                                              │           tokens, latency, cost
                                              │
                                              └──→ (many) EvaluationResults
                                                          ↓
                                                          ├─→ stores: scores,
                                                          │           overall_score,
                                                          │           reasoning
                                                          │
                                                          └─→ evaluator_id points to
                                                              evaluation system
```

---

## Request/Response Flow

### 1. Inference Request

```json
{
  "prompt_name": "greeting",                    // or prompt_version_id
  "variables": {
    "name": "Alice",
    "topic": "AI"
  },
  "model": "gpt-4-turbo",                       // optional override
  "temperature": 0.7,                           // optional override
  "session_id": "session-123",                  // tracking
  "user_id": "user-456"                         // tracking
}
```

### 2. Inference Processing

```
Input validation
  ↓
Resolve prompt version
  ├─ By ID: SELECT * FROM prompt_versions WHERE id = ?
  └─ By name: SELECT * FROM prompts WHERE name = ? 
             → SELECT * FROM prompt_versions WHERE is_active = TRUE
  ↓
Template interpolation
  ├─ system_template.format(**variables)
  └─ user_template.format(**variables)
  ↓
Select provider & model
  ├─ Get llm_config from prompt_version
  └─ Override with request params
  ↓
Run LLM inference [ASYNC]
  ├─ MockProvider.run_inference()
  └─ OpenAIProvider.run_inference()
     ├─ Count input tokens
     ├─ Call API
     ├─ Calculate output tokens
     ├─ Calculate cost
     └─ Measure latency_ms
  ↓
Log trace to database [ASYNC]
  └─ INSERT INTO inference_traces (
       trace_id, prompt_version_id, inputs, output, 
       tokens_in, tokens_out, latency_ms, cost_usd, 
       model, timestamp
     ) VALUES (...)
  ↓
Trigger background evaluation [FIRE & FORGET]
  ├─ LLM-as-Judge.evaluate(trace_id)
  ├─ Hallucination-Detector.check(trace_id)
  └─ Other evaluators...
  ↓
Return InferenceResponse [200 OK]
```

### 3. Inference Response

```json
{
  "trace_id": "uuid-1234-5678-90ab",
  "output": "Hi Alice! I'd love to discuss AI...",
  "latency_ms": 245,
  "tokens_in": 52,
  "tokens_out": 118,
  "cost_usd": 0.00425,
  "model": "gpt-4-turbo"
}
```

### 4. Background Evaluation

```
After returning 200 OK, trigger async tasks:

LLM-as-Judge Evaluator:
  ├─ SELECT output FROM inference_traces WHERE trace_id = ?
  ├─ Judge Prompt: "You are expert evaluator..."
  ├─ Call LLM with:
  │  ├─ Output to evaluate
  │  ├─ Original prompt
  │  └─ Scoring rubric
  ├─ Parse JSON response:
  │  ├─ correctness: 8
  │  ├─ completeness: 7
  │  ├─ safety: 10
  │  └─ reasoning: "Well-structured response..."
  ├─ Calculate overall_score: (8+7+10)/3 = 8.33
  └─ INSERT INTO evaluation_results (
       eval_id, trace_id, evaluator_id='judge-gpt4',
       scores, overall_score, reasoning, timestamp
     ) VALUES (...)

Hallucination Detector:
  ├─ Extract claims from output
  ├─ Embed each claim (sentence-transformers)
  ├─ Query knowledge_base (pgvector) for similar docs
  ├─ Calculate similarity scores
  ├─ If similarity < threshold: flag as potential hallucination
  └─ INSERT INTO evaluation_results (
       eval_id, trace_id, evaluator_id='hallucination-detector',
       scores={'hallucination_risk': 0.15},
       overall_score=9.85,  # Low hallucination = high score
       reasoning='...'
     ) VALUES (...)
```

---

## Query Examples for Dashboard

### Leaderboard: Top Prompts by Quality

```sql
SELECT 
  pv.prompt_id,
  p.name,
  pv.version,
  COUNT(er.eval_id) as evaluation_count,
  AVG(er.overall_score) as avg_quality_score,
  AVG(it.latency_ms) as avg_latency_ms,
  AVG(it.cost_usd) as avg_cost_usd,
  MAX(it.timestamp) as last_used
FROM prompt_versions pv
JOIN prompts p ON pv.id = p.id
LEFT JOIN inference_traces it ON pv.id = it.prompt_version_id
LEFT JOIN evaluation_results er ON it.trace_id = er.trace_id
WHERE it.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY pv.prompt_id, p.name, pv.version
ORDER BY avg_quality_score DESC
LIMIT 10;
```

### Drift Detection: Quality Over Time

```sql
SELECT 
  DATE_TRUNC('hour', timestamp) as hour,
  COUNT(*) as trace_count,
  AVG(er.overall_score) as avg_score,
  STDDEV(er.overall_score) as score_stddev,
  MIN(er.overall_score) as min_score,
  MAX(er.overall_score) as max_score
FROM inference_traces it
LEFT JOIN evaluation_results er ON it.trace_id = er.trace_id
WHERE it.prompt_version_id = 'uuid-prompt-version'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC
LIMIT 48;  -- Last 2 days hourly
```

### Cost Analysis by Model

```sql
SELECT 
  model,
  COUNT(*) as inference_count,
  ROUND(SUM(cost_usd), 4) as total_cost_usd,
  ROUND(AVG(cost_usd), 6) as avg_cost_usd,
  ROUND(MIN(latency_ms), 0) as min_latency_ms,
  ROUND(AVG(latency_ms), 0) as avg_latency_ms
FROM inference_traces
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY model
ORDER BY total_cost_usd DESC;
```

### Evaluation Breakdown by Type

```sql
SELECT 
  evaluator_id,
  COUNT(*) as evaluation_count,
  ROUND(AVG(overall_score), 2) as avg_score,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY overall_score) as median_score
FROM evaluation_results
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY evaluator_id;
```

---

## Async/Await Flow

```
request → endpoint (async def)
  ↓
get_db (async generator) → yields AsyncSession
  ↓
inference_service.run_inference(db) → async def
  ├─ await db.execute(select(...))  [async DB query]
  ├─ await provider.run_inference()  [async LLM call]
  ├─ await crud_trace.create(db, obj) [async DB insert]
  └─ background_tasks.add_task(...)  [fire & forget]
  ↓
response → 200 OK (immediate)
```

---

## Key Design Principles

### 1. **Prompt Versioning (Git for LLMs)**
   - Every change creates new semantic version
   - Can rollback to previous versions
   - Track who changed what and when
   - Easy A/B testing between versions

### 2. **Non-Blocking Evaluation**
   - Inference returns immediately (don't wait for evaluation)
   - Evaluation runs in background async
   - Dashboard polls for results
   - No impact on user latency

### 3. **Time-Series Ready**
   - All timestamps with timezone
   - indexed for time queries
   - Easy to bucket into hours/days/weeks
   - Built for TimescaleDB hypertables

### 4. **Provider Abstraction**
   - Easy to add new providers (OpenAI, Claude, Gemini, Ollama)
   - Standardized interface (InferenceResult)
   - Can compare providers easily
   - Mock provider for testing

### 5. **Flexible Evaluation**
   - Multiple evaluators per trace
   - Evaluator-specific score structures
   - Overall score aggregation
   - Reasoning/explanation storage

---

## Testing Data Example

### Setup Test Prompt

```python
# Create a test prompt and version
prompt = Prompt(
    id=uuid4(),
    name="greeting",
    description="Personalized greeting generator"
)
db.add(prompt)

version = PromptVersion(
    id=uuid4(),
    prompt_id=prompt.id,
    version="1.0.0",
    system_template="You are a friendly greeting generator.",
    user_template="Generate a greeting for {name} about {topic}.",
    llm_config={
        "provider": "openai",
        "model": "gpt-4-turbo",
        "temperature": 0.7
    },
    author="alice@example.com",
    is_active=True
)
db.add(version)
db.commit()
```

### Run Test Inference

```python
response = await client.post(
    "/api/v1/inference/run",
    json={
        "prompt_name": "greeting",
        "variables": {"name": "Bob", "topic": "Python"},
        "model": "gpt-4-turbo"
    }
)
# Returns: 200 OK with InferenceResponse
```

### Check Trace

```python
# Verify trace was created
trace = await crud_trace.get(db, response.trace_id)
assert trace is not None
assert trace.inputs == {"name": "Bob", "topic": "Python"}
assert trace.model == "gpt-4-turbo"
assert trace.timestamp is not None
```

### Query Metrics

```python
# Get aggregated metrics for the prompt
metrics = await crud_trace.get_metrics_by_version(
    db, 
    version.id, 
    hours=24
)
print(f"Avg latency: {metrics.avg_latency_ms}ms")
print(f"Avg cost: ${metrics.avg_cost_usd}")
```

---

## Performance Metrics

### Baseline (Mock Provider)
- Inference latency: 50-200ms
- DB insert: <10ms
- Response time: ~60-210ms total
- Cost per call: ~$0.0003

### Production (OpenAI GPT-4)
- API latency: 500-3000ms
- Token counting: <5ms
- DB insert: <10ms
- Response time: ~510-3010ms total
- Cost per call: ~$0.002-$0.01 (varies by tokens)

### Scaling Considerations
- Each trace adds ~100 bytes to DB
- 1M inferences = ~100MB storage
- Evaluation results add another ~200 bytes per eval
- Indexes needed on: (prompt_version_id, timestamp), (evaluator_id)
- Consider TimescaleDB compression for traces older than 30 days

---

**Status: Phase 1 Complete ✅**
**Next: Implement Phase 2 (OpenAI Provider) using PHASE2_GUIDE.md**
