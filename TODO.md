# OBELISK TODO (Derived from goals.json)
Based on **goals.json**, implement the following features and components for OBELISK:

## Core Features
- [ ] Modular agent architecture with role-based specializations
- [ ] Dynamic task router based on task type and model strengths
- [ ] YAML task definitions and structured prompt templates
- [ ] Long-term memory with SQL and vector store integration
- [ ] Multi-agent orchestration with fallback and voting logic
- [ ] Prompt chaining, inter-agent messaging, and reasoning logs

## Agent Roles
- **Claude** (System Architect / Planner)
  - [ ] Decomposition and pseudocode generation
  - [ ] Safety-aware logic and conceptual clarity
- **Codex (GPT-4o)** (Code Engineer / Implementer)
  - [ ] Precise code generation and API scaffolding
  - [ ] Structured logic and DevOps automation
- **Eli (ChatGPT)** (Synthesizer / Explainer / Coordinator)
  - [ ] Final output polish, testing harness integration
  - [ ] Documentation, humor, and meta-reasoning

## Modules

### memory
- [ ] Relational store support (MySQL/PostgreSQL)
- [ ] Vector store integration (FAISS, Chroma, etc.)
- [ ] Context recall, RAG support, agent preference memory

### prompt_system
- [ ] Model-specific and role-tuned prompt templates
- [ ] Self-refining prompt optimizer
- [ ] Retry + self-prompting fallback mechanisms

### execution
- [ ] Sandbox support (subprocess & Docker)
- [ ] Pytest auto-generator, code coverage, auto-repair on failure
- [ ] Validation: Pylint, Black, token/cost scoring

### interface
- [x] CLI (natural-language driven)
- [x] Web dashboard (FastAPI + React/Vite)
- [x] Task queue and Task History table
- [x] Log viewer via WebSocket stream

### intelligence
- [x] Meta-agent orchestration and self-improvement loops
- [ ] Agent scoring and inter-agent feedback
- [ ] Personality profiles support

### extensibility
- [x] Plugin API
- [x] Model-agnostic adapter layer
- [ ] Offline support
- [ ] Voice control

## Advanced Capabilities
- [ ] Autonomous mission planner with milestone breakdowns
- [ ] Code review and diffing between agents
- [ ] Thought chain visualization
- [ ] Auto-documentation and README generation
- [ ] Real-time feedback injection during runs
- [ ] Git + Docker integration for deployable builds
- [ ] Forkable task states via time-travel debugger

## Vision & Codename
- **Vision**: Trans-model, self-adaptive multi-agent OS to build, reason, test,
  and evolve software from idea to completion autonomously.
- **Codename**: THE AGENCY – MAX POWER EDITION
