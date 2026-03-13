from typing import List
from agent4target.schema.evidence import TargetRequest, RawEvidence, NormalizedEvidence, EvidenceSource, UnifiedEvidence

class NormalizationScoringAgent:
    """Agent that normalizes raw evidence and computes an aggregate score"""
    
    def process(self, target: TargetRequest, raw_evidence_list: List[RawEvidence]) -> UnifiedEvidence:
        normalized_items: List[NormalizedEvidence] = []
        
        for raw in raw_evidence_list:
            if raw.source == EvidenceSource.PHAROS:
                item = self._normalize_pharos(raw)
                normalized_items.append(item)
            elif raw.source == EvidenceSource.DEPMAP:
                item = self._normalize_depmap(raw)
                normalized_items.append(item)
            elif raw.source == EvidenceSource.OPEN_TARGETS:
                item = self._normalize_open_targets(raw)
                normalized_items.append(item)
        
        return UnifiedEvidence(target=target, evidence_items=normalized_items)

    def _normalize_pharos(self, raw: RawEvidence) -> NormalizedEvidence:
        data = raw.raw_data
        level = data.get("development_level", "Tdark")
        
        # Simple heuristic scoring based on development level
        score_map = {"Tclin": 1.0, "Tchem": 0.8, "Tbio": 0.5, "Tdark": 0.1}
        score = score_map.get(level, 0.1)
        
        return NormalizedEvidence(
            source=EvidenceSource.PHAROS,
            confidence_score=score,
            evidence_type="Development Level",
            summary=f"PHAROS classifies this target as {level}.",
            metadata={"development_level": level}
        )

    def _normalize_depmap(self, raw: RawEvidence) -> NormalizedEvidence:
        data = raw.raw_data
        dep_score = data.get("crispr_dependency_score", 0.0)
        
        # A more negative score implies higher dependency
        score = min(1.0, max(0.0, abs(dep_score) if dep_score < -0.5 else 0.2))
        
        return NormalizedEvidence(
            source=EvidenceSource.DEPMAP,
            confidence_score=score,
            evidence_type="Genetic Dependency",
            summary=f"CRISPR dependency score is {dep_score}.",
            metadata={"crispr_dependency_score": dep_score}
        )

    def _normalize_open_targets(self, raw: RawEvidence) -> NormalizedEvidence:
        data = raw.raw_data
        score = data.get("overall_association_score", 0.0)
        
        return NormalizedEvidence(
            source=EvidenceSource.OPEN_TARGETS,
            confidence_score=float(score),
            evidence_type="Disease Association",
            summary=f"Open Targets overall association score is {score}.",
            metadata={"association_types": data.get("association_types", {})}
        )

    def compute_aggregate_score(self, unified_evidence: UnifiedEvidence) -> float:
        """Computes a final target quality score by aggregating normalized evidence."""
        if not unified_evidence.evidence_items:
            return 0.0
        
        # Simple average for demonstration purposes. Can be weighted or more complex.
        total_score = sum(item.confidence_score for item in unified_evidence.evidence_items)
        return total_score / len(unified_evidence.evidence_items)
