# Fraud Detection API

A weekend project exploring LLM applications for fraud detection. Built with FastAPI and Claude API.

## Background

I wanted to understand how LLMs could be applied to fraud detection in payments, so I spent a weekend building this prototype. It's pretty simple - just a single API endpoint that analyzes transactions - but it helped me learn a lot about prompt engineering and working with LLM APIs.

This isn't production-ready (no auth, no real pattern detection, minimal testing), but it demonstrates the core concepts and gave me hands-on experience with:

- Crafting prompts that return structured, consistent outputs
- Basic guardrails like PII filtering and input validation  
- Applying patterns from my iOS work (logging, error handling) to API development
- Working with Claude's API in a fintech context

## Key Learnings

**Prompt Engineering**: Getting consistent structured output took some iteration. I found that being very explicit about the format (risk level, confidence, reasoning, etc.) and using a lower temperature (0.3) made responses way more predictable. Earlier versions with open-ended prompts were all over the place.

**Guardrails Matter**: Even for a prototype, I wanted to think about security from the start. The PII validation (only accepting last 4 card digits), basic prompt injection filtering, and input validation all felt important. Probably overkill for a learning project, but good practice.

**Familiar Patterns Still Apply**: A lot of what I've learned from iOS SDK development translates well - proper error handling, logging for debugging, thinking about failure modes. It's just HTTP instead of Swift.

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /analyze
       ▼
┌─────────────────────────────────┐
│   FastAPI Service (main.py)     │
│   ├─ Input Validation           │
│   ├─ Guardrails (PII, Injection)│
## How It Works

Pretty straightforward:
1. Receive transaction data via POST `/analyze`
2. Validate inputs (Pydantic does the heavy lifting)
3. Build a structured prompt with the transaction details
4. Send to Claude API (using Sonnet 3.5, temp 0.3 for consistency)
5. Parse the response and return risk assessment

I went with a single endpoint and kept it simple. No database, no complex orchestration - just wanted to focus on getting the prompt engineering right and understanding the API patterns.

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Run the Service

```bash
python main.py
```

Server starts at `http://localhost:8000`

### Test It

```bash
# Check health
curl http://localhost:8000/health

# Analyze a transaction
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_001",
    "amount": 5000.00,
    "merchant": "Electronics Store",
    "category": "electronics",
    "location": "Nigeria",
    "timestamp": "2024-12-08T02:30:00Z",
    "card_last_four": "1234"
  }'
```

**Expected Response**:
```json
{
  "transaction_id": "txn_001",
  "risk_level": "high",
  "confidence": "medium",
  "reasoning": "Large round-number amount in high-risk location at unusual hour...",
  "red_flags": ["High-risk location", "Round amount", "Late night transaction"],
  "recommendations": "Flag for manual review and contact cardholder"
}
```

## Example Scenarios

### Low Risk Transaction
```json
{
  "transaction_id": "txn_002",
  "amount": 47.32,
  "merchant": "Starbucks",
  "category": "food",
  "location": "San Francisco, CA",
  "timestamp": "2024-12-08T08:15:00Z",
  "card_last_four": "5678"
}
```

### High Risk Transaction
```json
{
  "transaction_id": "txn_003",
  "amount": 10000.00,
  "merchant": "Wire Transfer Service",
  "category": "financial",
  "location": "Unknown",
  "timestamp": "2024-12-08T03:00:00Z",
  "card_last_four": "9012"
}
```

## Limitations & Future Work

**Current Limitations**:
- ❌ No transaction history (can't detect unusual patterns for a user)
- ❌ No real-time monitoring/alerting
- ❌ Basic prompt injection prevention (not comprehensive)
- ❌ No authentication/rate limiting
- ❌ Single-model approach (no fallback if Claude is down)

**If I Continue This**:
- Add Redis for caching recent transactions per card
- Implement pattern detection (velocity checks, location hopping)
- Add test suite with mock Claude responses
- Deploy to Railway/Render with proper secrets management
- Compare different models (Claude vs GPT-4) for accuracy
- Add structured output (JSON mode) instead of regex parsing

## Technical Choices Explained

| Choice | Why |
|--------|-----|
| FastAPI | Fast, modern, great for APIs. Auto-generates OpenAPI docs |
| Claude Sonnet 3.5 | Good balance of speed/quality. Better at reasoning than Haiku |
| Pydantic | Type safety and validation. Catches bad input early |
| Temperature 0.3 | Low variance for consistent fraud analysis |
| Regex Parsing | Simple for prototype. Would use JSON mode in production |
| No Database | KISS for learning. Would add PostgreSQL for real app |

## What This Demonstrates

For interviews, I can discuss:
- ✅ Prompt engineering strategies and temperature tuning
- ✅ Guardrails and security considerations
- ✅ Production patterns (logging, error handling, validation)
- ✅ Trade-offs (simplicity vs features, speed vs accuracy)
## What's Missing

Lots, honestly. This was a weekend project to learn the basics:
- No transaction history or pattern detection (velocity checks, etc.)
- No authentication or rate limiting
- Regex parsing instead of structured JSON output
- No tests (would mock the Claude responses for testing)
- Single model with no fallback

If I keep working on this, I'd probably add Redis to track recent transactions per card, set up proper testing with mocked responses, and compare Claude vs GPT-4 for accuracy. Also would be interesting to try the structured output features instead of parsing text.c.com/claude/docs/prompt-engineering)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) (for guardrails)

## About

**Author**: Leo (iOS Engineer learning ML/AI)  
## Running It

Need Python 3.9+ and an Anthropic API key (they give $5 free credits when you sign up).

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
## Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_001",
    "amount": 5000.00,
    "merchant": "Electronics Warehouse",
    "category": "electronics",
    "location": "Lagos, Nigeria",
    "timestamp": "2024-12-08T02:30:00Z",
    "card_last_four": "1234"
  }'
```

Response includes risk level (low/medium/high), confidence, reasoning, red flags, and recommendations.

---

Built over a weekend to learn LLM application development. Feedback welcome!