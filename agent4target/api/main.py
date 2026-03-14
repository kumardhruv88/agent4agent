"""
FastAPI REST layer for Agent4Target.
Exposes the evidence aggregation pipeline as a production-ready HTTP API.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import time

from agent4target.orchestrator.workflow import run_pipeline

# ─── App Setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agent4Target API",
    description="Agent-based evidence aggregation for therapeutic target identification.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request / Response Models ────────────────────────────────────────────────

class TargetRequest(BaseModel):
    symbol: str
    custom_weights: Optional[Dict[str, float]] = None

class EvidenceItem(BaseModel):
    source: str
    confidence_score: float
    evidence_type: str
    summary: str

class TargetResponse(BaseModel):
    symbol: str
    aggregate_score: float
    priority: str
    evidence_items: List[EvidenceItem]
    source_weights: Dict[str, float]
    explanation: str
    elapsed_seconds: float

class BatchRequest(BaseModel):
    symbols: List[str]

class BatchResponse(BaseModel):
    results: List[TargetResponse]
    total_elapsed_seconds: float

# ─── Helper ───────────────────────────────────────────────────────────────────

def priority_label(score: float) -> str:
    if score >= 0.80:
        return "HIGH"
    elif score >= 0.55:
        return "MODERATE"
    else:
        return "LOW"

def format_response(symbol: str, result: dict, elapsed: float) -> TargetResponse:
    scored = result.get("scored_target")
    
    if scored is None:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed for {symbol}. Errors: {result.get('errors')}"
        )
    
    evidence_items = [
        EvidenceItem(
            source=item.source.value,
            confidence_score=item.confidence_score,
            evidence_type=item.evidence_type,
            summary=item.summary
        )
        for item in scored.unified_evidence.evidence_items
    ]
    
    return TargetResponse(
        symbol=scored.target.symbol,
        aggregate_score=scored.aggregate_score,
        priority=priority_label(scored.aggregate_score),
        evidence_items=evidence_items,
        source_weights=scored.source_weights,
        explanation=scored.explanation,
        elapsed_seconds=round(elapsed, 3)
    )

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "Agent4Target API",
        "version": "0.1.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/evaluate", response_model=TargetResponse)
def evaluate_target(request: TargetRequest):
    """
    Evaluate a single therapeutic target.
    Returns aggregate score, per-source evidence, and structured explanation.
    """
    start = time.time()
    
    try:
        result = run_pipeline(request.symbol.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    elapsed = time.time() - start
    return format_response(request.symbol.upper(), result, elapsed)

@app.post("/batch", response_model=BatchResponse)
def evaluate_batch(request: BatchRequest):
    """
    Evaluate multiple therapeutic targets in sequence.
    Returns ranked results sorted by aggregate score.
    """
    if len(request.symbols) > 20:
        raise HTTPException(
            status_code=400,
            detail="Batch size limited to 20 targets per request."
        )
    
    batch_start = time.time()
    results = []
    
    for symbol in request.symbols:
        start = time.time()
        try:
            result = run_pipeline(symbol.upper())
            elapsed = time.time() - start
            results.append(format_response(symbol.upper(), result, elapsed))
        except Exception as e:
            continue
    
    results.sort(key=lambda x: x.aggregate_score, reverse=True)
    
    return BatchResponse(
        results=results,
        total_elapsed_seconds=round(time.time() - batch_start, 3)
    )