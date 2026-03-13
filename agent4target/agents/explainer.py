"""
ExplanationAgent for Agent4Target.

Produces structured, non-conversational explanations that explicitly link
aggregate scores to supporting evidence — satisfying the GSoC requirement
for transparency and interpretability.
"""
from typing import Dict, Optional
from agent4target.schema.evidence import UnifiedEvidence, ScoredTarget


class ExplanationAgent:
    """
    Agent that generates structured explanations linking scores to evidence.

    Per the GSoC specification, this agent does NOT generate free-form
    conversational text. Instead, it produces structured, deterministic
    explanations that explicitly connect each evidence source to the final
    aggregate score, enabling reproducible and auditable outputs.
    """

    def generate_explanation(
        self,
        aggregate_score: float,
        unified_evidence: UnifiedEvidence,
        source_weights: Optional[Dict[str, float]] = None,
    ) -> ScoredTarget:
        """
        Generates a final ScoredTarget with a structured explanation.

        Args:
            aggregate_score: The weighted aggregate score (0-1).
            unified_evidence: The normalized evidence from all sources.
            source_weights: Optional dict of weights used per source.

        Returns:
            ScoredTarget with explanation and optional weight transparency.
        """
        symbol = unified_evidence.target.symbol

        # Determine rating based on score
        if aggregate_score >= 0.80:
            rating = "HIGH PRIORITY — Strong multi-source evidence."
        elif aggregate_score >= 0.55:
            rating = "MODERATE PRIORITY — Supporting evidence across some sources."
        else:
            rating = "LOW PRIORITY — Evidence is limited or conflicting."

        explanation_lines = [
            f"=== Target Evaluation Report: {symbol} ===",
            f"Aggregate Score: {aggregate_score:.3f}/1.000  |  Priority: {rating}",
            "",
            "Evidence Breakdown:",
            "-" * 50,
        ]

        for item in unified_evidence.evidence_items:
            weight_str = ""
            if source_weights:
                w = source_weights.get(item.source.value, 0.0)
                weight_str = f" [weight={w:.2f}]"

            explanation_lines.append(
                f"  [{item.source.value}]{weight_str} — {item.evidence_type}"
            )
            explanation_lines.append(f"    Score : {item.confidence_score:.3f}")
            explanation_lines.append(f"    Detail: {item.summary}")
            explanation_lines.append("")

        explanation_lines.append("-" * 50)
        explanation_lines.append(
            "Note: This explanation is deterministic and machine-readable. "
            "All scores are derived from source data, not generated text."
        )

        final_explanation = "\n".join(explanation_lines)

        return ScoredTarget(
            target=unified_evidence.target,
            aggregate_score=aggregate_score,
            unified_evidence=unified_evidence,
            explanation=final_explanation,
            source_weights=source_weights or {},
        )
