"""
Workflow Orchestrator for Agent4Target.

Uses LangGraph to implement a deterministic, inspectable state machine
that coordinates all evidence collector agents, the normalization/scoring
agent, and the explanation agent with full error handling.
"""
import operator
from typing import Annotated, TypedDict, Sequence
from langgraph.graph import StateGraph, START, END

from agent4target.schema.evidence import TargetRequest, RawEvidence, UnifiedEvidence, ScoredTarget
from agent4target.agents import (
    PharosAgent,
    DepMapAgent,
    OpenTargetsAgent,
    LiteratureAgent,
    NormalizationScoringAgent,
    ExplanationAgent
)

# ─── State Definition ────────────────────────────────────────────────────────

class AgentState(TypedDict):
    target: TargetRequest
    raw_evidence: Annotated[Sequence[RawEvidence], operator.add]
    unified_evidence: UnifiedEvidence | None
    scored_target: ScoredTarget | None
    errors: Annotated[Sequence[str], operator.add]


# ─── Node Functions (each is an isolated, inspectable unit) ──────────────────

def fetch_pharos(state: AgentState):
    """Node: Retrieve target development level from PHAROS GraphQL API."""
    try:
        evidence = PharosAgent().fetch_evidence(state["target"])
        return {"raw_evidence": [evidence]}
    except Exception as e:
        return {"errors": [f"PHAROS Error: {str(e)}"]}


def fetch_depmap(state: AgentState):
    """Node: Retrieve genetic dependency data from DepMap."""
    try:
        evidence = DepMapAgent().fetch_evidence(state["target"])
        return {"raw_evidence": [evidence]}
    except Exception as e:
        return {"errors": [f"DepMap Error: {str(e)}"]}


def fetch_open_targets(state: AgentState):
    """Node: Retrieve disease association scores from Open Targets GraphQL API."""
    try:
        evidence = OpenTargetsAgent().fetch_evidence(state["target"])
        return {"raw_evidence": [evidence]}
    except Exception as e:
        return {"errors": [f"Open Targets Error: {str(e)}"]}


def fetch_literature(state: AgentState):
    """Node: Retrieve literature evidence (publication count) from Europe PMC."""
    try:
        evidence = LiteratureAgent().fetch_evidence(state["target"])
        return {"raw_evidence": [evidence]}
    except Exception as e:
        return {"errors": [f"Literature Error: {str(e)}"]}


def normalize_and_score(state: AgentState):
    """Node: Normalize all collected evidence and compute a weighted aggregate score."""
    try:
        if not state.get("raw_evidence"):
            return {"errors": ["No raw evidence collected to normalize."]}

        agent = NormalizationScoringAgent()
        unified = agent.process(state["target"], list(state["raw_evidence"]))
        return {"unified_evidence": unified}
    except Exception as e:
        return {"errors": [f"Scoring Error: {str(e)}"]}


def explain_results(state: AgentState):
    """Node: Generate a structured, deterministic explanation of the final score."""
    try:
        unified = state.get("unified_evidence")
        if not unified:
            return {"errors": ["No unified evidence available to explain."]}

        scorer = NormalizationScoringAgent()
        score = scorer.compute_aggregate_score(unified)
        weights = scorer.get_active_weights(unified)

        scored_target = ExplanationAgent().generate_explanation(score, unified, source_weights=weights)
        return {"scored_target": scored_target}
    except Exception as e:
        return {"errors": [f"Explanation Error: {str(e)}"]}


# ─── Graph Assembly ───────────────────────────────────────────────────────────

def build_workflow() -> StateGraph:
    """
    Builds and compiles the deterministic Agent4Target LangGraph state machine.
    
    Topology:
      START → [pharos, depmap, open_targets, literature] → normalize → explain → END
    
    All four collector agents run in parallel before normalization begins.
    """
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("pharos", fetch_pharos)
    workflow.add_node("depmap", fetch_depmap)
    workflow.add_node("open_targets", fetch_open_targets)
    workflow.add_node("literature", fetch_literature)
    workflow.add_node("normalize", normalize_and_score)
    workflow.add_node("explain", explain_results)

    # 4 collectors run in parallel from START
    workflow.add_edge(START, "pharos")
    workflow.add_edge(START, "depmap")
    workflow.add_edge(START, "open_targets")
    workflow.add_edge(START, "literature")

    # All collectors feed into normalize
    workflow.add_edge("pharos", "normalize")
    workflow.add_edge("depmap", "normalize")
    workflow.add_edge("open_targets", "normalize")
    workflow.add_edge("literature", "normalize")

    # Then explain → END
    workflow.add_edge("normalize", "explain")
    workflow.add_edge("explain", END)

    return workflow.compile()


def run_pipeline(symbol: str) -> dict:
    """Convenience runner for a single target symbol."""
    app = build_workflow()

    initial_state = {
        "target": TargetRequest(symbol=symbol),
        "raw_evidence": [],
        "unified_evidence": None,
        "scored_target": None,
        "errors": []
    }

    return app.invoke(initial_state)


