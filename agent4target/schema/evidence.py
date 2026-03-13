from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class TargetRequest(BaseModel):
    """Input target to evaluate"""
    symbol: str = Field(..., description="Gene symbol, e.g., BRAF")
    ensembl_id: Optional[str] = Field(None, description="Ensembl Gene ID")

class EvidenceSource(str, Enum):
    PHAROS = "PHAROS"
    DEPMAP = "DEPMAP"
    OPEN_TARGETS = "OPEN_TARGETS"

class RawEvidence(BaseModel):
    """Base schema for raw evidence collected from APIs"""
    source: EvidenceSource
    raw_data: Dict[str, Any] = Field(..., description="Raw JSON data from the source")

class NormalizedEvidence(BaseModel):
    """Normalized evidence snippet derived from raw data"""
    source: EvidenceSource
    confidence_score: float = Field(0.0, description="Normalized score between 0 and 1 representing confidence/strength")
    evidence_type: str = Field(..., description="Type of evidence e.g., 'Genetic Perturbation', 'Development Level'")
    summary: str = Field(..., description="A brief text summary of what this evidence states")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Any additional structured metadata")

class UnifiedEvidence(BaseModel):
    """Unified schema combining multiple normalized evidence items"""
    target: TargetRequest
    evidence_items: List[NormalizedEvidence] = Field(default_factory=list)

class ScoredTarget(BaseModel):
    """Final output schema including aggregate score and generated explanations"""
    target: TargetRequest
    aggregate_score: float = Field(..., description="Final target quality score (0-1)")
    unified_evidence: UnifiedEvidence
    explanation: str = Field(..., description="Structured string explaining the score based on evidence")

