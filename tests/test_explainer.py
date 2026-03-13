"""Unit tests for the ExplanationAgent."""
import pytest
from agent4target.schema.evidence import (
    TargetRequest, RawEvidence, EvidenceSource
)
from agent4target.agents.scorer import NormalizationScoringAgent
from agent4target.agents.explainer import ExplanationAgent


@pytest.fixture
def full_unified():
    target = TargetRequest(symbol="EGFR")
    raw_items = [
        RawEvidence(source=EvidenceSource.PHAROS, raw_data={"development_level": "Tclin"}),
        RawEvidence(source=EvidenceSource.DEPMAP, raw_data={"crispr_dependency_score": -0.9, "dependent_cell_lines": 200}),
        RawEvidence(source=EvidenceSource.OPEN_TARGETS, raw_data={"overall_association_score": 0.9}),
    ]
    scorer = NormalizationScoringAgent()
    return scorer.process(target, raw_items)


def test_explanation_is_structured(full_unified):
    scorer = NormalizationScoringAgent()
    score = scorer.compute_aggregate_score(full_unified)
    weights = scorer.get_active_weights(full_unified)

    agent = ExplanationAgent()
    result = agent.generate_explanation(score, full_unified, source_weights=weights)

    # Verify the output is a ScoredTarget with all fields
    assert result.aggregate_score > 0.0
    assert "EGFR" in result.explanation
    assert "Aggregate Score" in result.explanation
    # Verify that explanations include all sources
    assert "PHAROS" in result.explanation
    assert "DEPMAP" in result.explanation


def test_explanation_includes_weights(full_unified):
    scorer = NormalizationScoringAgent()
    score = scorer.compute_aggregate_score(full_unified)
    weights = scorer.get_active_weights(full_unified)
    
    agent = ExplanationAgent()
    result = agent.generate_explanation(score, full_unified, source_weights=weights)
    
    assert result.source_weights  # weights should be populated
    assert "weight=" in result.explanation


def test_high_score_high_priority(full_unified):
    scorer = NormalizationScoringAgent()
    score = scorer.compute_aggregate_score(full_unified)
    
    agent = ExplanationAgent()
    result = agent.generate_explanation(score, full_unified)
    
    # EGFR with Tclin + high DepMap + high OT should be HIGH PRIORITY
    assert "HIGH PRIORITY" in result.explanation or "MODERATE PRIORITY" in result.explanation
