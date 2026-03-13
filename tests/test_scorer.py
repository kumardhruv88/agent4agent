"""Unit tests for the NormalizationScoringAgent."""
import pytest
from agent4target.schema.evidence import (
    TargetRequest, RawEvidence, EvidenceSource
)
from agent4target.agents.scorer import NormalizationScoringAgent, DEFAULT_WEIGHTS


@pytest.fixture
def target():
    return TargetRequest(symbol="BRAF")


@pytest.fixture
def pharos_raw():
    return RawEvidence(source=EvidenceSource.PHAROS, raw_data={"development_level": "Tclin"})


@pytest.fixture
def depmap_raw():
    return RawEvidence(source=EvidenceSource.DEPMAP, raw_data={
        "crispr_dependency_score": -0.8, "dependent_cell_lines": 100
    })


@pytest.fixture
def open_targets_raw():
    return RawEvidence(source=EvidenceSource.OPEN_TARGETS, raw_data={
        "overall_association_score": 0.85
    })


@pytest.fixture
def literature_raw():
    return RawEvidence(source=EvidenceSource.LITERATURE, raw_data={
        "publication_count": 1000,
        "source_db": "Europe PMC"
    })


def test_pharos_normalization(target, pharos_raw):
    agent = NormalizationScoringAgent()
    unified = agent.process(target, [pharos_raw])
    item = unified.evidence_items[0]
    assert item.source == EvidenceSource.PHAROS
    assert item.confidence_score == 1.0  # Tclin = top score


def test_depmap_normalization(target, depmap_raw):
    agent = NormalizationScoringAgent()
    unified = agent.process(target, [depmap_raw])
    item = unified.evidence_items[0]
    assert item.source == EvidenceSource.DEPMAP
    assert item.confidence_score == 0.8  # abs(-0.8) for score > 0.5


def test_open_targets_normalization(target, open_targets_raw):
    agent = NormalizationScoringAgent()
    unified = agent.process(target, [open_targets_raw])
    item = unified.evidence_items[0]
    assert item.confidence_score == 0.85


def test_literature_normalization(target, literature_raw):
    agent = NormalizationScoringAgent()
    unified = agent.process(target, [literature_raw])
    item = unified.evidence_items[0]
    # 1000 publications → log10(1001)/4 ≈ 0.75
    assert item.confidence_score > 0.5


def test_weighted_aggregate_score(target, pharos_raw, depmap_raw, open_targets_raw, literature_raw):
    agent = NormalizationScoringAgent()
    unified = agent.process(target, [pharos_raw, depmap_raw, open_targets_raw, literature_raw])
    score = agent.compute_aggregate_score(unified)
    # Score should be between 0 and 1
    assert 0.0 <= score <= 1.0


def test_custom_weights(target, pharos_raw, depmap_raw):
    """Test that custom weight overrides work correctly."""
    custom_weights = {EvidenceSource.PHAROS: 0.9, EvidenceSource.DEPMAP: 0.1}
    agent = NormalizationScoringAgent(weights=custom_weights)
    unified = agent.process(target, [pharos_raw, depmap_raw])
    score = agent.compute_aggregate_score(unified)
    # With 90% weight on Tclin (score=1.0), result should be high
    assert score > 0.85


def test_empty_evidence_returns_zero(target):
    agent = NormalizationScoringAgent()
    unified = agent.process(target, [])
    score = agent.compute_aggregate_score(unified)
    assert score == 0.0
