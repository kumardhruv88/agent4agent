import streamlit as st
import sys
import os
import json

# Ensure agent4target is in Python path for local testing
sys.path.append(os.path.abspath('.'))

from agent4target.orchestrator.workflow import build_workflow
from agent4target.schema.evidence import TargetRequest

# Initialize Workflow once
@st.cache_resource
def get_workflow():
    return build_workflow()

st.set_page_config(
    page_title="Agent4Target",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Agent4Target")
st.subheader("Agent-based Evidence Aggregation Toolkit for Therapeutic Target Identification")
st.markdown("Enter a Gene Symbol below to orchestrate the AI agents to collect, normalize, and score multimodal evidence.")

st.divider()

# Input Section
col1, col2 = st.columns([1, 2])

with col1:
    target_symbol = st.text_input("Gene Symbol (e.g., BRAF, EGFR, TP53):", value="BRAF")
    analyze_btn = st.button("Run Knowledge Agents", type="primary")

# Execution and Results
if analyze_btn and target_symbol:
    app = get_workflow()
    
    initial_state = {
        "target": TargetRequest(symbol=target_symbol),
        "raw_evidence": [],
        "unified_evidence": None,
        "scored_target": None,
        "errors": []
    }
    
    with st.spinner(f"🚀 Orchestrating Pipeline for {target_symbol}..."):
        
        # Displaying Agent Progress using status (Mock visual feedback, as LangGraph runs instantly here)
        with st.status("Executing Multi-Agent Workflow...", expanded=True) as status:
            st.write("🧪 Querying PHAROS for Development Status...")
            st.write("🧬 Querying DepMap for Essentiality Scores...")
            st.write("🔗 Querying Open Targets for Disease Associations...")
            st.write("⚖️ Normalizing & Scoring unified multimodal evidence...")
            st.write("📝 Synthesizing Structured Explanations...")
            status.update(label="Workflow Execution Complete!", state="complete", expanded=False)
        
        # Run workflow
        result = app.invoke(initial_state)
        
        errors = result.get("errors")
        scored_target = result.get("scored_target")
        
        if errors:
            st.error("Pipeline encountered errors:")
            for err in errors:
                st.write(f"- {err}")
        
        if scored_target:
            st.success(f"Analysis Complete for **{scored_target.target.symbol}**")
            
            # Display metrics
            st.metric(label="Unified Target Quality Score", value=f"{scored_target.aggregate_score:.2f}")
            
            st.subheader("Transparent Explanation")
            st.info(scored_target.explanation)
            
            with st.expander("View Full Structured JSON Output"):
                st.json(json.loads(scored_target.model_dump_json()))
                
        elif not errors:
            st.error("Failed to generate a final scored target. Check agent execution.")
