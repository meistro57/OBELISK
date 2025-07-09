# Proposed Improvements for OBELISK

## 1. General Code‑base Improvements

### a) Enforce consistency with linting/formatting
- Add a pre‑commit toolchain (Black, isort, Ruff/mypy, Flake8) so that code style, imports, and basic type‑safety checks run automatically on every commit.
- Commit a `.pre-commit-config.yaml`, configure Black for formatting, isort for imports, and Ruff (or Flake8) for lint rules.

### b) Strengthen typing and static analysis
- Add type hints throughout (especially public APIs in `agent_system/*` and `service/api.py`) and enable `mypy` in strict(er) mode.
- Catch mismatches early, improve IDE autocompletion, and document expected parameter/return types.

### c) Improve error handling & observability
- Wrap all external calls (LLM API, database, subprocesses) with clear exception handlers that:
  1. log a structured error message (e.g. via `logging.exception()`),
  2. include enough context (agent name, model, parameters),
  3. propagate or return a user‑friendly error to the API/CLI.
- Consider integrating Sentry (or another error‑tracking service) for production deployments.

### d) Introduce CI/CD
- Add a GitHub Actions (or GitLab CI) pipeline that runs:
  - `pre-commit run --all-files`
  - `pytest -q`
  - `mypy --strict`
  - (optionally) `black --check`, `ruff check .`
- Enforce that pull requests cannot merge unless CI passes.

### e) Modularize & remove dead code
- Audit for any unused modules or vestigial scripts; remove or archive them.
- Group related agents/plugins under a clear package structure; lean on `__init__.py` exports.

### f) Documentation & onboarding
- Split the giant README into smaller docs (e.g. Sphinx/Markdown under a `docs/` folder).
- Provide a “Quickstart” that shows a minimal end‑to‑end run.
- Document how to add new agents, prompts, or plugins in a CONTRIBUTING.md.

## 2. API & Backend UX Suggestions

### a) Health‑check & version endpoint
- Expose `GET /healthz` or `GET /version` that returns service readiness, git commit hash, schema versions, etc.

### b) Pagination & filtering on memory/tasks
- Support query parameters for pagination (e.g. `?page=2&per_page=20`) and filtering by date range or agent.

### c) Async improvements
- For long‑running agent tasks, return a WebSocket or Server‑Sent‑Events (SSE) URL so clients can stream logs/results in real time (instead of polling).

### d) Configurable timeouts & retries
- Allow per‑agent, per‑model timeout overrides; implement retry/backoff for transient LLM/API errors.

## 3. Frontend (“GUI”) Beautification

### a) Adopt a component/UI library
- Chakra UI or MUI (Material‑UI) or Ant Design: provides polished, accessible components (buttons, tables, modals) out of the box.
- Reduces custom CSS burden and enforces a consistent design system.

### b) Responsive layout & theming
- Use CSS Grid or Flexbox to ensure the dashboard adapts to different screen sizes.
- Add light/dark theme toggles, persisted in local storage, for better usability in low‑light environments.

### c) Improve data tables & interactivity
- Replace plain HTML tables with a data‑table component that offers sorting, searching, pagination, and column resizing.
- Examples: MUI DataGrid, React Table + Tailwind, or Ant Design Table.

### d) Richer task & log views
- Task history: display human‑readable timestamps, agent icons/badges, and color‑coded statuses (e.g. green for “SUCCESS”, red for “FAIL”).
- Log streaming: turn the raw WebSocket log feed into a scroll‑locking, auto‑scrolling console panel with syntax highlighting (e.g. using Prism.js).

### e) User feedback & toasts
- Show toast notifications (snackbars) on task enqueue/failure/success using a UI library’s notification component.
- Improves perceived responsiveness; the user knows their action was received.

### f) Polished styling via utility CSS
- If you prefer staying lightweight, adopt Tailwind CSS—rapidly compose responsive, consistent UIs with utility classes.
- Configure a Tailwind theme (colors, spacing) that matches your brand.

### g) Loading & empty states
- For sections that are waiting on network data, show skeleton loaders or spinners rather than blank areas.
- For empty memory/task lists, display an illustration or friendly hint (“No tasks run yet. Submit one from the form above.”).

## 4. Roadmap Ideas

| Area                 | Next Steps                                                            |
|----------------------|-----------------------------------------------------------------------|
| **Testing & CI**     | Add GitHub Actions, enforce pre‑commit & type checks                  |
| **Error Handling**   | Centralize API error middleware, integrate Sentry                     |
| **UX Flows**         | Task submission wizard, parameter validation, confirm dialogs         |
| **UI Polishing**     | MUI/Chakra framework, dark mode, responsive/mobile support            |
| **Plugin Extensibility** | CLI tools to scaffold new agents/plugins (generate YAML stubs)     |
| **Documentation**    | Sphinx site or mkdocs, contribution guide, API reference             |

---

This document outlines proposed improvements for code quality, stability, and user experience. Feel
free to comment or prioritize any items, and I can start implementing them.
