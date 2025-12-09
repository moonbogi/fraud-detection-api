# Fraud Detection API

A weekend project exploring fraud detection patterns and API development. Built with FastAPI and rule-based logic.

## Background

I wanted to understand how LLMs could be applied to fraud detection in payments, so I spent a weekend building this prototype. It's pretty simple - just a single API endpoint that analyzes transactions - but it helped me learn a lot about prompt engineering and working with LLM APIs.

This isn't production-ready (no auth, no real pattern detection, minimal testing), but it demonstrates core fraud detection concepts and gave me hands-on experience with:

- Understanding common fraud indicators (location patterns, amount analysis, time-of-day)
- Basic guardrails like PII filtering and input validation  
- Applying patterns from my iOS work (logging, error handling) to API development
- Building structured APIs for financial applications

## Key Learnings

**Fraud Detection Logic**: Built rule-based analysis checking for common fraud indicators - high-risk locations, round amounts, unusual times, risky merchant categories. Simple but effective for demonstrating the concepts.

**Guardrails Matter**: Even for a prototype, I wanted to think about security from the start. The PII validation (only accepting last 4 card digits), input sanitization, and proper validation all felt important. Good practice for fintech applications.

**Familiar Patterns Still Apply**: A lot of what I've learned from iOS SDK development translates well - proper error handling, logging for debugging, thinking about failure modes. It's just HTTP instead of Swift.

## How It Works

Pretty straightforward:
1. Receive transaction data via POST `/analyze`
2. Validate inputs (Pydantic does the heavy lifting)
3. Apply rule-based fraud detection logic
4. Check for red flags (location, amount patterns, timing, merchant type)
5. Return risk assessment with reasoning

I went with a single endpoint and kept it simple. No database, no complex orchestration - just wanted to focus on understanding fraud patterns and building a clean API.

## What's Missing

Lots, honestly. This was a weekend project to learn the basics:
- No transaction history or pattern detection (velocity checks, etc.)
- No authentication or rate limiting
- Regex parsing instead of structured JSON output
- No tests (would mock the Claude responses for testing)
- Single model with no fallback

If I keep working on this, I'd probably add Redis to track recent transactions per card, set up proper testing with mocked responses, and compare Claude vs GPT-4 for accuracy. Also would be interesting to try the structured output features instead of parsing text.

## Tech Choices

- **FastAPI**: Seemed like the obvious choice for a modern Python API. The auto-generated docs are nice.
- **Rule-based logic**: Simple and deterministic. Good for demos and understanding fraud patterns before adding ML complexity.
- **Pydantic**: Makes validation so much cleaner than manual checks.

## Running It

## Running It

Need Python 3.9+. No API keys required.

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the server
python main.py
```ver runs at `http://localhost:8000`. Check `/docs` for the Swagger UI.

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
