from agent4target.schema.evidence import UnifiedEvidence, ScoredTarget

class ExplanationAgent:
    """Agent that generates structured explanations linking scores to evidence."""
    
    def generate_explanation(self, aggregate_score: float, unified_evidence: UnifiedEvidence) -> ScoredTarget:
        """Generates a final ScoredTarget including a structured textual explanation."""
        
        explanation_lines = [
            f"Target {unified_evidence.target.symbol} achieved an aggregate score of {aggregate_score:.2f}.",
            "This score is derived from the following evidence:"
        ]
        
        for item in unified_evidence.evidence_items:
            source_name = item.source.value
            explanation_lines.append(
                f"- [{source_name}] ({item.evidence_type}): {item.summary} (Confidence: {item.confidence_score:.2f})"
            )
            
        final_explanation = "\n".join(explanation_lines)
        
        return ScoredTarget(
            target=unified_evidence.target,
            aggregate_score=aggregate_score,
            unified_evidence=unified_evidence,
            explanation=final_explanation
        )
