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

## How It Works

Pretty straightforward:
1. Receive transaction data via POST `/analyze`
2. Validate inputs (Pydantic does the heavy lifting)
3. Build a structured prompt with the transaction details
4. Send to Claude API (using Sonnet 3.5, temp 0.3 for consistency)
5. Parse the response and return risk assessment

I went with a single endpoint and kept it simple. No database, no complex orchestration - just wanted to focus on getting the prompt engineering right and understanding the API patterns.

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
- **Claude Sonnet 3.5**: Wanted to try Anthropic's API. Sonnet has good reasoning ability and the pricing is reasonable.
- **Pydantic**: Makes validation so much cleaner than manual checks.
- **Temperature 0.3**: After testing, lower temps gave way more consistent results for this use case.
- **Regex parsing**: Quick and dirty for a prototype. Their structured output feature would be better for real use.

## Running It

Need Python 3.9+ and an Anthropic API key (they give $5 free credits when you sign up).

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Edit .env with your key

# Start the server
python main.py
```

Server runs at `http://localhost:8000`. Check `/docs` for the Swagger UI.

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
