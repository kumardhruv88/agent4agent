"""
Normalization & Scoring Agent for Agent4Target.

This module implements the GSoC requirement for:
- Evidence normalization across sources
- Confidence-aware scoring and aggregation
- Optional weighting or calibration strategies
"""
from typing import List, Dict, Optional
from agent4target.schema.evidence import (
    TargetRequest, RawEvidence, NormalizedEvidence,
    EvidenceSource, UnifiedEvidence
)

# Default weights for each evidence source.
# These reflect biological relevance in drug discovery:
# - PHAROS (clinical validation status) is highest priority
# - Open Targets (disease association) is strong evidence
# - DepMap (genetic essentiality) provides functional evidence
# - Literature (research attention) is a softer, supporting signal
DEFAULT_WEIGHTS: Dict[str, float] = {
    EvidenceSource.PHAROS: 0.40,
    EvidenceSource.OPEN_TARGETS: 0.30,
    EvidenceSource.DEPMAP: 0.20,
    EvidenceSource.LITERATURE: 0.10,
}


class NormalizationScoringAgent:
    """
    Agent that normalizes raw evidence and computes a confidence-aware
    weighted aggregate score.
    
    Supports optional custom weight overrides for calibration strategies.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Args:
            weights: Optional dict mapping EvidenceSource to a float weight.
                     Falls back to DEFAULT_WEIGHTS if not provided.
        """
        self.weights = weights or DEFAULT_WEIGHTS

    def process(self, target: TargetRequest, raw_evidence_list: List[RawEvidence]) -> UnifiedEvidence:
        """Normalize all raw evidence items into a unified schema."""
        normalized_items: List[NormalizedEvidence] = []

        for raw in raw_evidence_list:
            normalizer = {
                EvidenceSource.PHAROS: self._normalize_pharos,
                EvidenceSource.DEPMAP: self._normalize_depmap,
                EvidenceSource.OPEN_TARGETS: self._normalize_open_targets,
                EvidenceSource.LITERATURE: self._normalize_literature,
            }.get(raw.source)

            if normalizer:
                normalized_items.append(normalizer(raw))

        return UnifiedEvidence(target=target, evidence_items=normalized_items)

    def _normalize_pharos(self, raw: RawEvidence) -> NormalizedEvidence:
        data = raw.raw_data
        level = data.get("development_level", "Tdark")

        # Biologically grounded scoring: Tclin = approved target, Tdark = uncharacterized
        score_map = {"Tclin": 1.0, "Tchem": 0.75, "Tbio": 0.45, "Tdark": 0.1}
        score = score_map.get(level, 0.1)

        return NormalizedEvidence(
            source=EvidenceSource.PHAROS,
            confidence_score=score,
            evidence_type="Development Level",
            summary=f"PHAROS classifies this target as {level}.",
            metadata={"development_level": level, "target_family": data.get("family")}
        )

    def _normalize_depmap(self, raw: RawEvidence) -> NormalizedEvidence:
        data = raw.raw_data
        dep_score = data.get("crispr_dependency_score", 0.0)
        dependent_lines = data.get("dependent_cell_lines", 0)

        # A more negative score implies higher essentiality/dependency
        score = min(1.0, max(0.0, abs(dep_score) if dep_score < -0.5 else 0.2))

        return NormalizedEvidence(
            source=EvidenceSource.DEPMAP,
            confidence_score=score,
            evidence_type="Genetic Dependency",
            summary=f"CRISPR dependency score is {dep_score} across {dependent_lines} cell lines.",
            metadata={"crispr_dependency_score": dep_score, "dependent_cell_lines": dependent_lines}
        )

    def _normalize_open_targets(self, raw: RawEvidence) -> NormalizedEvidence:
        data = raw.raw_data
        score = float(data.get("overall_association_score", 0.0))

        return NormalizedEvidence(
            source=EvidenceSource.OPEN_TARGETS,
            confidence_score=score,
            evidence_type="Disease Association",
            summary=f"Open Targets overall association score is {score:.2f}.",
            metadata={
                "ensembl_id": data.get("ensembl_id"),
                "association_types": data.get("association_types", {})
            }
        )

    def _normalize_literature(self, raw: RawEvidence) -> NormalizedEvidence:
        data = raw.raw_data
        pub_count = data.get("publication_count", 0)

        # Logarithmic normalization: >1000 papers = max signal, <10 = very low
        import math
        score = min(1.0, math.log10(pub_count + 1) / 4.0) if pub_count > 0 else 0.0

        return NormalizedEvidence(
            source=EvidenceSource.LITERATURE,
            confidence_score=round(score, 3),
            evidence_type="Literature Evidence",
            summary=f"Found {pub_count} peer-reviewed publications in Europe PMC.",
            metadata={"publication_count": pub_count, "source_db": data.get("source_db")}
        )

    def compute_aggregate_score(self, unified_evidence: UnifiedEvidence) -> float:
        """
        Computes a final target quality score using confidence-aware weighted aggregation.
        
        Sources with defined weights are weighted proportionally.
        Sources without weights fall back to equal contribution.
        
        Returns:
            Aggregate score between 0.0 and 1.0.
        """
        if not unified_evidence.evidence_items:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for item in unified_evidence.evidence_items:
            w = self.weights.get(item.source, 1.0 / len(unified_evidence.evidence_items))
            weighted_sum += item.confidence_score * w
            total_weight += w

        if total_weight == 0:
            return 0.0

        return round(weighted_sum / total_weight, 4)

    def get_active_weights(self, unified_evidence: UnifiedEvidence) -> Dict[str, float]:
        """Returns the weights that were actually applied, for transparency in the output."""
        return {
            item.source.value: self.weights.get(item.source, 0.0)
            for item in unified_evidence.evidence_items
        }
