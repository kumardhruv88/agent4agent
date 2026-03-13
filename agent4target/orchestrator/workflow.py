import operator
from typing import Annotated, TypedDict, Sequence
from langgraph.graph import StateGraph, START, END

from agent4target.schema.evidence import TargetRequest, RawEvidence, UnifiedEvidence, ScoredTarget
from agent4target.agents import (
    PharosAgent,
    DepMapAgent,
    OpenTargetsAgent,
    NormalizationScoringAgent,
    ExplanationAgent
)

# 1. Define the State
class AgentState(TypedDict):
    target: TargetRequest
    raw_evidence: Annotated[Sequence[RawEvidence], operator.add]
    unified_evidence: UnifiedEvidence | None
    scored_target: ScoredTarget | None
    errors: Annotated[Sequence[str], operator.add]

# 2. Node Functions
def fetch_pharos(state: AgentState):
    try:
        agent = PharosAgent()
        evidence = agent.fetch_evidence(state["target"])
        return {"raw_evidence": [evidence]}
    except Exception as e:
        return {"errors": [f"PHAROS Error: {str(e)}"]}

def fetch_depmap(state: AgentState):
    try:
        agent = DepMapAgent()
        evidence = agent.fetch_evidence(state["target"])
        return {"raw_evidence": [evidence]}
    except Exception as e:
        return {"errors": [f"DepMap Error: {str(e)}"]}

def fetch_open_targets(state: AgentState):
    try:
        agent = OpenTargetsAgent()
        evidence = agent.fetch_evidence(state["target"])
        return {"raw_evidence": [evidence]}
    except Exception as e:
        return {"errors": [f"Open Targets Error: {str(e)}"]}

def normalize_and_score(state: AgentState):
    agent = NormalizationScoringAgent()
    try:
        if not state.get("raw_evidence"):
            return {"errors": ["No raw evidence collected to normalize."]}
        
        unified = agent.process(state["target"], state["raw_evidence"])
        score = agent.compute_aggregate_score(unified)
        
        # We need to temporarily pass the score. We can store it on the unified evidence or state.
        # Let's attach it to unified temporarily, but it's cleaner to pass it to Explainer.
        return {"unified_evidence": unified}
    except Exception as e:
        return {"errors": [f"Scoring Error: {str(e)}"]}

def explain_results(state: AgentState):
    agent = ExplanationAgent()
    scorer = NormalizationScoringAgent()
    try:
        unified = state["unified_evidence"]
        if not unified:
            return {"errors": ["No unified evidence available to explain."]}
        
        score = scorer.compute_aggregate_score(unified)
        scored_target = agent.generate_explanation(score, unified)
        return {"scored_target": scored_target}
    except Exception as e:
        return {"errors": [f"Explanation Error: {str(e)}"]}

# 3. Build the Graph
def build_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("pharos", fetch_pharos)
    workflow.add_node("depmap", fetch_depmap)
    workflow.add_node("open_targets", fetch_open_targets)
    workflow.add_node("normalize", normalize_and_score)
    workflow.add_node("explain", explain_results)
    
    # Define edges
    # Collectors run in parallel after START
    workflow.add_edge(START, "pharos")
    workflow.add_edge(START, "depmap")
    workflow.add_edge(START, "open_targets")
    
    # Normalize waits for all collectors
    workflow.add_edge("pharos", "normalize")
    workflow.add_edge("depmap", "normalize")
    workflow.add_edge("open_targets", "normalize")
    
    # Explain runs after Normalize
    workflow.add_edge("normalize", "explain")
    workflow.add_edge("explain", END)
    
    return workflow.compile()

# Example runner function
def run_pipeline(symbol: str) -> dict:
    app = build_workflow()
    
    initial_state = {
        "target": TargetRequest(symbol=symbol),
        "raw_evidence": [],
        "unified_evidence": None,
        "scored_target": None,
        "errors": []
    }
    
    # Run the graph
    result = app.invoke(initial_state)
    return result
