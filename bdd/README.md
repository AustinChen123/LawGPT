# BDD Test Specifications for LawGPT

This directory contains Behavior-Driven Development (BDD) specifications written in Gherkin syntax for the LawGPT project.

## Structure

```
bdd/
├── features/
│   ├── 01_retrieval/          # Retrieval system behaviors
│   ├── 02_agent/              # Agent system behaviors
│   ├── 03_ui/                 # User interface behaviors
│   ├── 04_integration/        # End-to-end integration scenarios
│   └── 05_performance/        # Performance and quality scenarios
└── README.md
```

## Coverage Areas

### 1. Retrieval System (Phase 1)
- Vector database retrieval
- Web search retrieval
- Hybrid retrieval strategies
- Document chunking and processing
- Metadata extraction

### 2. Agent System (Phase 2)
- ReAct agent reasoning
- Tool orchestration
- Memory management
- Error handling and recovery
- Multi-turn conversations

### 3. User Interface (Phase 3)
- Streamlit visualization
- Reasoning trace display
- Metrics dashboard
- User interactions

### 4. Integration Flows (All Phases)
- End-to-end query workflows
- Multi-retrieval mode scenarios
- Cross-language support
- Citation extraction and validation

### 5. Performance & Quality
- Response time requirements
- Retrieval accuracy
- Cost optimization
- System resilience

## Running BDD Tests

```bash
# Install behave (Python BDD framework)
pip install behave

# Run all scenarios
behave bdd/features/

# Run specific feature
behave bdd/features/01_retrieval/vector_retrieval.feature

# Run with tags
behave --tags=@critical
behave --tags=@phase1
```

## Writing Guidelines

1. **Feature**: Describe the high-level capability
2. **Scenario**: Specific behavior example
3. **Given**: Setup/preconditions
4. **When**: Action/trigger
5. **Then**: Expected outcome
6. **And**: Additional steps

## Tags

- `@phase1`, `@phase2`, `@phase3`, `@phase4`: Implementation phases
- `@critical`: Critical path scenarios
- `@integration`: Cross-component tests
- `@performance`: Performance-related tests
- `@smoke`: Quick smoke tests
- `@wip`: Work in progress
