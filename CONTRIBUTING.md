# Contributing to Agent4Target

Thank you for your interest in contributing to **Agent4Target**! We welcome researchers, developers, and biologists to help us build a more robust toolkit for therapeutic target identification.

## 🚀 Getting Started

1. **Fork the Repository**: Create a fork of the project on GitHub.
2. **Clone Locally**: 
   ```bash
   git clone https://github.com/yourusername/agent4target.git
   cd agent4target
   ```
3. **Install Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## 🛠️ Development Workflow

### Adding a New Collector Agent
To add a new data source:
1. Create a new class in `agent4target/agents/collectors.py` inheriting from `EvidenceCollector`.
2. Implement the `fetch_evidence` method.
3. Update the `UnifiedEvidence` schema in `agent4target/schema/evidence.py` if new fields are required.

### Modifying the Workflow
The project uses **LangGraph** to orchestrate agents. If you wish to change the execution logic:
- Modify the state machine in `agent4target/orchestrator/workflow.py`.

## ✅ Coding Standards
- Use **Black** for code formatting.
- Ensure all new methods have type hints.
- Write docstrings for new classes and functions.

## 🧪 Testing
Before submitting a PR, ensure all tests pass:
```bash
pytest tests/
```

## 💡 GSoC Project Ideas
If you are a GSoC applicant, consider these areas for expansion:
- **Advanced Graph Embeddings**: Integrating knowledge graphs for target-disease linking.
- **LLM-based Reasoning**: Enhancing the `ExplainerAgent` with RAG-based literature verification.
- **Multi-modal Visualizer**: Expanding the Streamlit dashboard with interactive heatmaps.
