# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned

#### Phase 0: Foundation (Week 1-2)
- Knowledge Base CRUD operations
- CLI commands (`init`, `kb add`, `kb search`, `kb list`)
- Basic MCP Server infrastructure
- YAML-based persistence
- Pydantic data models

#### Phase 1: Core Engine (Week 3-8)
- Task Management with DAG validation
- Dependency Analyzer (auto-inference)
- MCP Server tools (`kb_search`, `kb_add`, `task_*`)
- Slash commands integration
- Dependency Analyzer Subagent

#### Phase 2: Conflict Prevention (Week 9-12)
- Conflict Detector (pre-merge risk analysis)
- Drift Detection
- Lifecycle Hooks
- Event Logging
- Conflict Detector Subagent

---

## [0.1.0] - TBD (Phase 0 Target)

### Added
- Initial project structure
- Pydantic data models:
  - `KnowledgeBaseEntry` with validation
  - `KnowledgeBaseConfig`
- Knowledge Base manager (`clauxton/core/knowledge_base.py`):
  - `add()` - Add KB entry
  - `search()` - Search with keyword/category/tag filtering
  - `get()` - Retrieve entry by ID
  - `update()` - Update entry with versioning
  - `delete()` - Soft delete
  - `list_all()` - List all entries
- YAML utilities with atomic write and backup
- File utilities with secure permissions (700/600)
- CLI commands:
  - `clauxton init` - Initialize `.clauxton/` directory
  - `clauxton kb add` - Add Knowledge Base entry (interactive)
  - `clauxton kb search <query>` - Search Knowledge Base
  - `clauxton kb list` - List all KB entries
- Basic MCP Server (`clauxton/mcp/kb_server.py`):
  - Health check endpoint
  - Tool registration infrastructure
- Unit tests:
  - `tests/core/test_models.py`
  - `tests/core/test_knowledge_base.py`
  - `tests/utils/test_yaml_utils.py`
  - `tests/cli/test_main.py`
- Integration tests:
  - End-to-end workflow (init → add → search)
- Documentation:
  - `README.md` - Project overview
  - `docs/quick-start.md` - Quick start guide
  - `docs/installation.md` - Installation instructions
  - `docs/project-plan.md` - Market analysis & strategy
  - `docs/requirements.md` - Functional & non-functional requirements
  - `docs/technical-design.md` - Architecture & implementation details
  - `docs/roadmap.md` - 16-week development roadmap
  - `docs/phase-0-plan.md` - Detailed Phase 0 plan
  - `CONTRIBUTING.md` - Contribution guidelines
  - `CODE_OF_CONDUCT.md` - Code of Conduct
- GitHub templates:
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
- Development setup:
  - `pyproject.toml` with dependencies
  - `.gitignore` for Python projects
  - MIT License

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- File permissions set to 700 (directories) and 600 (files)
- YAML schema validation on read/write
- Input sanitization via Pydantic validators

---

## [0.0.1] - 2025-10-19 (Project Inception)

### Added
- Project structure initialization
- Basic package files
- Planning documentation (Japanese versions)
- Repository setup at `/home/kishiyama-n/workspace/projects/clauxton/`

---

## Format Guide

### Types of Changes
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

### Version Format
- **MAJOR** - Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR** - New features (e.g., 0.1.0 → 0.2.0)
- **PATCH** - Bug fixes (e.g., 0.1.0 → 0.1.1)

---

**Note**: This changelog is maintained manually. Contributors should update this file when making significant changes as part of their pull requests.

[Unreleased]: https://github.com/nakishiyaman/clauxton/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nakishiyaman/clauxton/releases/tag/v0.1.0
[0.0.1]: https://github.com/nakishiyaman/clauxton/releases/tag/v0.0.1
