"""
Fraud Detection API

Weekend project to learn LLM application development. Uses Claude API to analyze
credit card transactions for fraud indicators.
"""

import os
import re
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="Simple fraud analysis using Claude API",
    version="0.1.0"
)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class TransactionRequest(BaseModel):
    """Transaction data to analyze."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    merchant: str = Field(..., min_length=1, max_length=200, description="Merchant name")
    category: str = Field(..., description="Transaction category (e.g., retail, travel)")
    location: str = Field(..., description="Transaction location")
    timestamp: str = Field(..., description="Transaction timestamp (ISO 8601)")
    card_last_four: Optional[str] = Field(None, description="Last 4 digits of card")
    
    @field_validator("card_last_four")
    @classmethod
    def validate_card_last_four(cls, v):
        """Only accept last 4 digits (no full card numbers)."""
        if v and len(v) != 4:
            raise ValueError("Only last 4 digits of card allowed")
        if v and not v.isdigit():
            raise ValueError("Card digits must be numeric")
        return v
    
    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Invalid timestamp format. Use ISO 8601")
        return v


class FraudAnalysisResponse(BaseModel):
    """Fraud analysis result."""
    transaction_id: str
    risk_level: str  # "low", "medium", "high"
    confidence: str  # "low", "medium", "high"
    reasoning: str
    red_flags: list[str]
    recommendations: str


def sanitize_input(text: str) -> str:
    """
    Basic prompt injection prevention - removes common attack patterns.
    Not comprehensive, but catches the obvious stuff.
    """
    # Filter out common injection attempts
    injection_patterns = [
        r"ignore\s+previous\s+instructions",
        r"ignore\s+above",
        r"disregard\s+previous",
        r"system\s*:",
        r"assistant\s*:",
        r"user\s*:",
    ]
    
    sanitized = text
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()


def build_fraud_prompt(transaction: TransactionRequest) -> str:
    """
    Construct the analysis prompt. Took a few iterations to get the format right -
    being explicit about the output structure made responses way more consistent.
    """
    # Clean inputs first
    merchant = sanitize_input(transaction.merchant)
    category = sanitize_input(transaction.category)
    location = sanitize_input(transaction.location)
    
    prompt = f"""You are a fraud detection expert analyzing a credit card transaction.

Transaction Details:
- Amount: ${transaction.amount:.2f}
- Merchant: {merchant}
- Category: {category}
- Location: {location}
- Time: {transaction.timestamp}
- Card: ****{transaction.card_last_four or 'XXXX'}

Analyze this transaction for fraud indicators. Consider:
1. Amount appropriateness for category
2. Unusual location patterns (e.g., high-risk regions)
3. Merchant reputation concerns
4. Time-of-day patterns
5. Round number amounts (common in fraud)

Provide your analysis in this exact format:

RISK_LEVEL: [low/medium/high]
CONFIDENCE: [low/medium/high]
REASONING: [2-3 sentences explaining your assessment]
RED_FLAGS: [comma-separated list of concerns, or "none"]
RECOMMENDATIONS: [1-2 sentence action recommendation]

Be specific and practical. Focus on concrete indicators."""

    return prompt


def parse_claude_response(response_text: str) -> dict:
    """
    Extract the structured fields from Claude's response.
    Quick and dirty regex parsing - would use JSON mode for anything real.
    """
    result = {
        "risk_level": "unknown",
        "confidence": "unknown",
        "reasoning": "",
        "red_flags": [],
        "recommendations": ""
    }
    
    # Extract risk level
    risk_match = re.search(r"RISK_LEVEL:\s*(\w+)", response_text, re.IGNORECASE)
    if risk_match:
        result["risk_level"] = risk_match.group(1).lower()
    
    # Extract confidence
    conf_match = re.search(r"CONFIDENCE:\s*(\w+)", response_text, re.IGNORECASE)
    if conf_match:
        result["confidence"] = conf_match.group(1).lower()
    
    # Extract reasoning
    reason_match = re.search(r"REASONING:\s*(.+?)(?=RED_FLAGS:|$)", response_text, re.IGNORECASE | re.DOTALL)
    if reason_match:
        result["reasoning"] = reason_match.group(1).strip()
    
    # Extract red flags
    flags_match = re.search(r"RED_FLAGS:\s*(.+?)(?=RECOMMENDATIONS:|$)", response_text, re.IGNORECASE | re.DOTALL)
    if flags_match:
        flags_text = flags_match.group(1).strip()
        if flags_text.lower() != "none":
            result["red_flags"] = [f.strip() for f in flags_text.split(",") if f.strip()]
    
    # Extract recommendations
    rec_match = re.search(r"RECOMMENDATIONS:\s*(.+)", response_text, re.IGNORECASE | re.DOTALL)
    if rec_match:
        result["recommendations"] = rec_match.group(1).strip()
    
    return result


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Fraud Detection API",
        "version": "0.1.0"
    }


@app.post("/analyze", response_model=FraudAnalysisResponse)
async def analyze_transaction(transaction: TransactionRequest, request: Request):
    """
    Analyze a transaction for fraud indicators.
    
    Sends transaction details to Claude with a structured prompt and parses
    the response into risk level, confidence, reasoning, etc.
    """
    try:
        # Log request (without sensitive data)
        logger.info(
            f"Analyzing transaction {transaction.transaction_id} - "
            f"Amount: ${transaction.amount:.2f}, Category: {transaction.category}"
        )
        
        # Build prompt
        prompt = build_fraud_prompt(transaction)
        
        # Call Claude API
        logger.debug(f"Calling Claude API with prompt length: {len(prompt)} chars")
        # Call Claude
        logger.debug(f"Calling Claude API with prompt length: {len(prompt)} chars")
        
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            temperature=0.3,  # Lower temp = more consistent results
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract response text
        response_text = message.content[0].text
        logger.debug(f"Claude response: {response_text[:200]}...")
        
        # Parse response
        analysis = parse_claude_response(response_text)
        
        # Build response
        result = FraudAnalysisResponse(
            transaction_id=transaction.transaction_id,
            risk_level=analysis["risk_level"],
            confidence=analysis["confidence"],
            reasoning=analysis["reasoning"],
            red_flags=analysis["red_flags"],
            recommendations=analysis["recommendations"]
        )
        
        logger.info(
            f"Transaction {transaction.transaction_id} analyzed - "
            f"Risk: {result.risk_level}, Confidence: {result.confidence}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing transaction {transaction.transaction_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze transaction: {str(e)}"
        )


@app.get("/health")
async def health_check():
@app.get("/health")
async def health_check():
    """Health check - verifies API key is configured."""
        "timestamp": datetime.utcnow().isoformat(),
        "anthropic_api_configured": bool(os.getenv("ANTHROPIC_API_KEY"))
    }
    
    if not health["anthropic_api_configured"]:
        health["status"] = "unhealthy"
        health["error"] = "ANTHROPIC_API_KEY not configured"
    
    return health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
