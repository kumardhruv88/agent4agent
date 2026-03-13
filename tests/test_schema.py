"""Unit tests for Agent4Target schema definitions."""
import pytest
from agent4target.schema.evidence import (
    TargetRequest, RawEvidence, NormalizedEvidence,
    UnifiedEvidence, ScoredTarget, EvidenceSource
)


def test_target_request_valid():
    t = TargetRequest(symbol="BRAF")
    assert t.symbol == "BRAF"
    assert t.ensembl_id is None


def test_target_request_with_ensembl():
    t = TargetRequest(symbol="EGFR", ensembl_id="ENSG00000146648")
    assert t.ensembl_id == "ENSG00000146648"


def test_evidence_source_enum():
    assert EvidenceSource.PHAROS == "PHAROS"
    assert EvidenceSource.DEPMAP == "DEPMAP"
    assert EvidenceSource.OPEN_TARGETS == "OPEN_TARGETS"
    assert EvidenceSource.LITERATURE == "LITERATURE"


def test_raw_evidence_schema():
    raw = RawEvidence(
        source=EvidenceSource.PHAROS,
        raw_data={"development_level": "Tclin"}
    )
    assert raw.source == EvidenceSource.PHAROS
    assert raw.raw_data["development_level"] == "Tclin"


def test_normalized_evidence_schema():
    norm = NormalizedEvidence(
        source=EvidenceSource.DEPMAP,
        confidence_score=0.8,
        evidence_type="Genetic Dependency",
        summary="Test summary"
    )
    assert 0.0 <= norm.confidence_score <= 1.0


def test_scored_target_has_weights():
    target = TargetRequest(symbol="BRAF")
    unified = UnifiedEvidence(target=target, evidence_items=[])
    scored = ScoredTarget(
        target=target,
        aggregate_score=0.75,
        unified_evidence=unified,
        explanation="Test explanation",
        source_weights={"PHAROS": 0.4, "DEPMAP": 0.2}
    )
    assert scored.source_weights["PHAROS"] == 0.4
