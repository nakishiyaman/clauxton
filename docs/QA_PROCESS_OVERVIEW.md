# Clauxton Quality Assurance Process - Complete Overview

**Version**: 2.0
**Last Updated**: 2025-11-04
**Status**: ✅ Active

---

## 🎯 Overview

Clauxton's QA process is designed to **catch issues locally before they reach GitHub CI**, using a multi-layered approach with automation at every stage.

### Key Principle

> **"Issues should be caught at the earliest possible stage"**

```
Local Development → Pre-Commit → Pre-Release → GitHub CI → Production
     ↓                ↓             ↓              ↓            ↓
   Fast Tests     All Checks    Comprehensive   Full Matrix   Monitoring
   (seconds)      (1-2 min)     Validation      (5-10 min)
                                 (5-10 min)
```

---

## 📊 Quality Assurance Layers

### Layer 1: Development (Continuous) ⚡

**When**: During active coding
**Duration**: Real-time to seconds
**Goal**: Immediate feedback

#### Tools & Practices

1. **Type Hints** (Real-time in IDE)
   ```python
   # ✅ Good - Type hints everywhere
   def add_memory(entry: MemoryEntry) -> str:
       """Add memory entry."""
       return entry.id

   # ❌ Bad - No type hints
   def add_memory(entry):
       return entry.id
   ```

2. **IDE Integration**
   - VSCode: Python extension with mypy
   - PyCharm: Built-in type checking
   - Neovim: LSP with pyright/mypy

3. **Watch Mode** (Optional but recommended)
   ```bash
   # Auto-run tests on file change
   pytest-watch -- -m "not slow and not performance"

   # Or use pytest-testmon for incremental testing
   pytest --testmon -m "not slow and not performance"
   ```

**Coverage**: Type hints, basic syntax, fast tests

---

### Layer 2: Pre-Commit Hooks (Automated) 🔒

**When**: Every git commit
**Duration**: 1-2 minutes
**Goal**: Block bad commits

#### Configuration

**File**: `.pre-commit-config.yaml`

#### Checks Performed

```bash
# Automatic execution on: git commit
┌─────────────────────────────────────────┐
│ Pre-Commit Checks (Blocking)            │
├─────────────────────────────────────────┤
│ 1. Type Checking (mypy --strict)        │  ~30s
│ 2. Linting (ruff check --fix)           │  ~10s
│ 3. Fast Tests (no slow/performance)     │  ~30s
│ 4. Security Scan (bandit)               │  ~10s
│ 5. File Checks (YAML, trailing spaces)  │  ~5s
└─────────────────────────────────────────┘
Total: ~85 seconds
```

#### Setup

```bash
# One-time setup
pip install pre-commit
pre-commit install

# Test hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

#### Bypass (Emergency Only)

```bash
# Skip hooks (NOT recommended)
git commit --no-verify -m "Emergency fix"

# Better: Fix issues and commit normally
```

**Coverage**: Type safety, code style, fast tests, security, file formats

---

### Layer 3: Pre-Release Validation (Scripted) 📋

**When**: Before creating git tag
**Duration**: 5-10 minutes
**Goal**: Comprehensive release readiness

#### Script

**File**: `scripts/pre_release_check.sh`

#### Usage

```bash
# Basic usage
./scripts/pre_release_check.sh 0.16.0

# Output:
🔍 Pre-Release Validation for v0.16.0
========================================

1️⃣  Checking version consistency...
✅ __version__.py: 0.16.0
✅ pyproject.toml: 0.16.0
✅ test_main.py: 0.16.0

2️⃣  Checking test markers...
✅ All performance tests have markers

3️⃣  Checking CI dependency consistency...
✅ CI includes semantic dependencies
✅ CI includes parsers-all dependencies

4️⃣  Type checking (strict mode)...
✅ Type checking passed

5️⃣  Linting...
✅ Linting passed

6️⃣  Security scan...
✅ Security scan passed (0 vulnerabilities)

7️⃣  Running fast tests...
✅ Fast tests passed

8️⃣  Building package...
✅ Package built successfully
✅ Package validation passed

========================================
📊 Pre-Release Check Summary
========================================

✅ All checks passed!

🚀 Ready to release v0.16.0

Next steps:
  1. Review CHANGELOG.md
  2. git add -A && git commit -m 'chore: prepare v0.16.0 release'
  3. git tag -a v0.16.0 -m 'Release v0.16.0'
  4. git push origin main
  5. git push origin v0.16.0
  6. gh release create v0.16.0 --generate-notes
  7. twine upload dist/*
```

#### Checks Performed

```bash
┌──────────────────────────────────────────┐
│ Pre-Release Validation (8 Checks)        │
├──────────────────────────────────────────┤
│ ✅ 1. Version Consistency (3 files)      │
│    - __version__.py                      │
│    - pyproject.toml                      │
│    - tests/cli/test_main.py              │
│                                          │
│ ✅ 2. Test Marker Validation             │
│    - @pytest.mark.performance required   │
│    - @pytest.mark.slow recommended       │
│                                          │
│ ✅ 3. CI Dependency Check                │
│    - semantic dependencies               │
│    - parsers-all dependencies            │
│                                          │
│ ✅ 4. Type Checking (mypy --strict)      │
│                                          │
│ ✅ 5. Linting (ruff check)               │
│                                          │
│ ✅ 6. Security Scan (bandit)             │
│                                          │
│ ✅ 7. Fast Tests                         │
│    - Excludes slow/performance tests     │
│                                          │
│ ✅ 8. Package Build                      │
│    - python -m build                     │
│    - twine check                         │
└──────────────────────────────────────────┘
```

**Coverage**: Version consistency, test markers, CI config, all code quality checks, build

---

### Layer 4: GitHub CI (Automated) 🤖

**When**: On push to main / PR creation
**Duration**: 5-10 minutes (with performance test exclusion)
**Goal**: Multi-environment validation

#### Workflow

**File**: `.github/workflows/ci.yml`

#### Jobs

```bash
┌─────────────────────────────────────────────┐
│ GitHub Actions CI (3 Jobs in Parallel)      │
├─────────────────────────────────────────────┤
│ Job 1: Test (Matrix: Python 3.11, 3.12)     │
│   - Install dependencies                    │
│   - Run pytest with coverage                │
│   - Upload to Codecov                       │
│   Duration: ~5-7 minutes                    │
│                                             │
│ Job 2: Lint                                 │
│   - Run ruff check                          │
│   - Run mypy --strict                       │
│   - Run bandit security scan                │
│   Duration: ~2-3 minutes                    │
│                                             │
│ Job 3: Build                                │
│   - Build package (wheel + sdist)           │
│   - Validate with twine                     │
│   - Upload artifacts                        │
│   Duration: ~2-3 minutes                    │
│                                             │
│ Job 4: Performance (Weekly/Manual Only)     │
│   - Run performance tests                   │
│   - Benchmark tracking                      │
│   Duration: ~30+ minutes                    │
│   Trigger: Schedule (Sunday 02:00 UTC)      │
│            or workflow_dispatch             │
└─────────────────────────────────────────────┘
```

#### Configuration Highlights

```yaml
# Test job - Install ALL dependencies
pip install -e ".[dev,parsers-all,semantic]"

# Run tests - Exclude slow/performance by default
pytest --cov-report=xml -v
# (pyproject.toml: -m 'not slow and not performance')

# Performance job - Run weekly
on:
  schedule:
    - cron: '0 2 * * 0'  # Every Sunday at 02:00 UTC
  workflow_dispatch:      # Allow manual trigger
```

**Coverage**: Multi-Python versions, all dependencies, full test suite, build artifacts

---

### Layer 5: Post-Release Monitoring (Continuous) 📈

**When**: After PyPI release
**Duration**: Ongoing
**Goal**: Production quality monitoring

#### Metrics Tracked

1. **PyPI Downloads**
   - Source: https://pypistats.org/packages/clauxton
   - Alert: Sudden drop (>50%)

2. **GitHub Issues**
   - Target: <5 new issues per release
   - Response time: <24 hours

3. **CI Success Rate**
   - Target: >95% pass rate
   - Alert: 2 consecutive failures

4. **Test Coverage**
   - Target: ≥90%
   - Alert: Drop below 85%

5. **Security Vulnerabilities**
   - Source: Dependabot, bandit
   - Response: Immediate fix (<24h for critical)

---

## 🔄 Complete Development Flow

### Typical Development Session

```
┌──────────────────────────────────────────────────────────┐
│ Developer Workflow with QA Process                        │
└──────────────────────────────────────────────────────────┘

1. Write Code
   │
   ├─ IDE provides real-time type hints
   └─ Watch mode runs fast tests (optional)

2. Git Commit
   │
   ├─ Pre-commit hooks run automatically (1-2 min)
   │  ├─ Type check (mypy)
   │  ├─ Lint (ruff)
   │  ├─ Fast tests
   │  └─ Security scan
   │
   └─ If pass → Commit succeeds
      If fail → Fix issues, retry

3. Push to GitHub
   │
   └─ GitHub CI runs (5-10 min)
      ├─ Test job (Python 3.11, 3.12)
      ├─ Lint job
      └─ Build job

4. Before Release (v0.X.0)
   │
   ├─ Update version in 3 files
   ├─ Update CHANGELOG.md
   │
   ├─ Run pre-release script (5-10 min)
   │  ./scripts/pre_release_check.sh 0.X.0
   │
   └─ If all checks pass:
      ├─ git tag -a v0.X.0 -m "Release v0.X.0"
      ├─ git push origin v0.X.0
      └─ GitHub CI validates tag

5. Release to PyPI
   │
   ├─ gh release create v0.X.0
   └─ twine upload dist/*

6. Post-Release Monitoring
   │
   ├─ Monitor GitHub CI
   ├─ Check PyPI downloads
   ├─ Watch for issues
   └─ Create quality report
```

---

## 📋 Quality Checklists

### Daily Development Checklist

- [ ] IDE shows no type errors
- [ ] Fast tests pass locally
- [ ] Pre-commit hooks pass on commit
- [ ] Code pushed to GitHub
- [ ] GitHub CI passes

### Pre-Release Checklist (Automated by Script)

- [ ] Version updated in 3 files
- [ ] Test markers validated
- [ ] CI dependencies verified
- [ ] Type checking passes (strict)
- [ ] Linting passes
- [ ] Security scan clean
- [ ] Fast tests pass
- [ ] Package builds successfully

### Release Day Checklist

- [ ] Run pre-release script: `./scripts/pre_release_check.sh <version>`
- [ ] All checks pass ✅
- [ ] Review CHANGELOG.md
- [ ] Create git tag
- [ ] Push to GitHub
- [ ] GitHub CI passes
- [ ] Create GitHub release
- [ ] Upload to PyPI
- [ ] Verify installation: `pip install clauxton==<version>`
- [ ] Create quality report

### Weekly Monitoring Checklist

- [ ] Review GitHub CI success rate (>95%)
- [ ] Check test coverage (≥90%)
- [ ] Review Dependabot alerts
- [ ] Check PyPI download trends
- [ ] Review GitHub issues (<5 open)

---

## 🎓 Best Practices

### Test Writing

```python
# ✅ Good - Fast unit test
def test_memory_add(memory: Memory) -> None:
    """Test adding memory entry."""
    entry = MemoryEntry(...)
    memory_id = memory.add(entry)
    assert memory_id.startswith("MEM-")

# ⚠️ Needs marker - Slow test (>5s)
@pytest.mark.slow
def test_integration_workflow() -> None:
    """Test complete workflow."""
    time.sleep(5)  # Simulating long operation
    ...

# ⚠️ Needs marker - Performance test (>30s)
@pytest.mark.performance
def test_large_dataset_performance() -> None:
    """Test with 1000+ entries."""
    for i in range(1000):
        ...
```

### Version Updates

```bash
# ✅ Good - Update all 3 files together
vim clauxton/__version__.py     # __version__ = "0.16.0"
vim pyproject.toml               # version = "0.16.0"
vim tests/cli/test_main.py       # assert "0.16.0" in result.output

# Then run validation
./scripts/pre_release_check.sh 0.16.0

# ❌ Bad - Update only one file
vim clauxton/__version__.py     # __version__ = "0.16.0"
# Forgot pyproject.toml and test_main.py
# → Pre-release script will catch this!
```

### Dependency Management

```bash
# ✅ Good - Keep CI in sync with pyproject.toml
# Update pyproject.toml
[project.optional-dependencies]
semantic = ["sentence-transformers>=2.3.0"]

# Update .github/workflows/ci.yml
pip install -e ".[dev,parsers-all,semantic]"

# ❌ Bad - CI missing dependencies
# Only update pyproject.toml
# → Pre-release script will warn!
```

---

## 📊 Quality Metrics Dashboard

### Current Quality Snapshot (v0.15.0)

```
┌──────────────────────────────────────────┐
│ Clauxton Quality Metrics                 │
├──────────────────────────────────────────┤
│ Test Coverage:        82% → 90% (goal)   │
│ Test Count:           2,391 passing      │
│ Type Safety:          100% (strict)      │
│ Linting:              0 errors           │
│ Security:             0 vulnerabilities  │
│ CI Pass Rate:         ~70% → 95% (goal)  │
│ Release Frequency:    ~1 per week        │
│ Average Fix Time:     <24 hours          │
└──────────────────────────────────────────┘
```

### Quality Targets

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Test Coverage** | 82% | 90%+ | ⚠️ In Progress |
| **CI Pass Rate** | ~70% | 95%+ | ⚠️ New Process |
| **Type Safety** | 100% | 100% | ✅ |
| **Security Scan** | 0 issues | 0 issues | ✅ |
| **Lint Errors** | 0 | 0 | ✅ |
| **Build Success** | 100% | 100% | ✅ |
| **Test Speed** | 5-10 min | <10 min | ✅ |

---

## 🚨 Troubleshooting

### Pre-Commit Hook Fails

**Problem**: Commit blocked by pre-commit hooks

```bash
# See what failed
git commit -m "feat: new feature"
# → Shows which hook failed

# Fix the issue
ruff check --fix .     # Auto-fix linting
mypy --strict clauxton/  # Check types
pytest -m "not slow and not performance" -x  # Run tests

# Retry commit
git commit -m "feat: new feature"
```

**Emergency bypass** (use sparingly):
```bash
git commit --no-verify -m "Emergency hotfix"
```

### Pre-Release Script Fails

**Problem**: Pre-release validation fails

```bash
# See detailed output
./scripts/pre_release_check.sh 0.16.0

# Common issues:
# 1. Version mismatch
#    → Update all 3 files: __version__.py, pyproject.toml, test_main.py

# 2. Missing test marker
#    → Add @pytest.mark.performance to slow tests

# 3. CI dependency mismatch
#    → Update .github/workflows/ci.yml

# 4. Test failures
#    → Run pytest -v to see failures
#    → Fix tests and retry
```

### GitHub CI Fails After Local Success

**Problem**: CI fails but all local checks passed

**Possible causes**:
1. **Environment differences**
   ```bash
   # Test with CI-like environment
   python -m venv .venv-ci
   source .venv-ci/bin/activate
   pip install -e ".[dev,parsers-all,semantic]"
   pytest --cov=clauxton --cov-report=xml -v
   ```

2. **Python version differences**
   ```bash
   # Test multiple Python versions locally
   tox  # Requires tox.ini configuration
   ```

3. **Missing files in git**
   ```bash
   # Check git status
   git status
   git add <missing-files>
   ```

---

## 📚 Related Documentation

- **Setup Guide**: `docs/QA_PROCESS_IMPROVED.md` - Detailed QA process
- **Test Coverage**: `docs/TEST_COVERAGE_ANALYSIS.md` - Comprehensive test analysis 🆕
- **Release Checklist**: `CLAUDE.md` - Release procedures
- **Test Writing**: `docs/TEST_WRITING_GUIDE.md` - Test best practices
- **CI Configuration**: `.github/workflows/ci.yml` - GitHub Actions
- **Pre-Commit**: `.pre-commit-config.yaml` - Hook configuration

---

## 🎯 Success Criteria

### QA Process is successful when:

1. ✅ **95%+ of releases have 0 CI failures**
2. ✅ **Issues are caught locally before push**
3. ✅ **Release process takes <30 minutes**
4. ✅ **Coverage stays ≥90%**
5. ✅ **No manual checklist errors**

### Expected Impact (v0.16.0+)

- 🎯 CI failures: 30% → **<5%** (6x improvement)
- 🎯 Local detection: 50% → **95%+** (2x improvement)
- 🎯 Release time: 1-2h → **<30min** (3x faster)
- 🎯 Manual errors: Frequent → **Nearly zero**

---

**Last Updated**: 2025-11-04
**Next Review**: After v0.16.0 release
**Owner**: Development Team
