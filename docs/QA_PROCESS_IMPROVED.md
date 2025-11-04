# Improved Quality Assurance Process

**Version**: 2.0
**Date**: 2025-11-04
**Status**: Active
**Previous Issues**: v0.15.0 had 3 CI failures that should have been caught locally

---

## 🎯 Goal

**Catch issues locally before they reach GitHub CI**

---

## 📊 Root Cause Analysis (v0.15.0)

### Issues Found

| Issue | Root Cause | Prevention |
|-------|------------|------------|
| test_version_command failure | Manual checklist not followed | Automated version check |
| performance test timeout | Missing @pytest.mark.performance | Automated marker validation |
| Semantic dependencies missing | CI config out of sync | Environment consistency check |

### Common Theme

**All issues were preventable with automation**

---

## 🔧 Improved QA Process

### Phase 0: Pre-Development Setup (One-time)

**Install QA Tools**:

```bash
# Install pre-commit framework
pip install pre-commit

# Install additional QA tools
pip install pytest-testmon pytest-watch tox

# Setup pre-commit hooks
pre-commit install
```

**Configure Pre-commit** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: local
    hooks:
      # 1. Type checking
      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        args: [--strict, clauxton/]
        pass_filenames: false

      # 2. Linting
      - id: ruff
        name: ruff
        entry: ruff check
        language: system
        types: [python]
        args: [--fix]

      # 3. Fast tests only (no slow/performance)
      - id: pytest-fast
        name: pytest (fast)
        entry: pytest
        language: system
        types: [python]
        args: [-m, "not slow and not performance", --tb=short, -q]
        pass_filenames: false
        stages: [commit]

      # 4. Security scan
      - id: bandit
        name: bandit
        entry: bandit
        language: system
        types: [python]
        args: [-r, clauxton/, -ll, -q]
        pass_filenames: false
```

---

### Phase 1: During Development (Continuous)

**Test-Driven Development**:

```bash
# Watch mode: auto-run tests on file changes
pytest-watch -- -m "not slow and not performance"

# Or use testmon for faster incremental testing
pytest --testmon -m "not slow and not performance"
```

**Best Practices**:
1. ✅ Write test first
2. ✅ Run test locally before committing
3. ✅ Use appropriate markers (`@pytest.mark.slow`, `@pytest.mark.performance`)
4. ✅ Keep tests fast (<1s per test for unit tests)

---

### Phase 2: Pre-Commit (Automated)

**Automatic Checks** (via pre-commit hooks):

1. ✅ **Type checking** (mypy --strict)
2. ✅ **Linting** (ruff check --fix)
3. ✅ **Fast tests** (pytest -m "not slow and not performance")
4. ✅ **Security** (bandit -r clauxton/ -ll)

**If any check fails**:
- ❌ Commit is blocked
- 🔧 Fix the issue
- 🔄 Try commit again

**Bypass** (use sparingly):
```bash
# Skip pre-commit hooks (NOT recommended)
git commit --no-verify -m "message"
```

---

### Phase 3: Pre-Release Validation (Manual but Scripted)

#### 3.1 Release Readiness Script

**Create**: `scripts/pre_release_check.sh`

```bash
#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/pre_release_check.sh <version>"
    exit 1
fi

echo "🔍 Pre-Release Validation for v$VERSION"
echo "========================================"

# 1. Version consistency check
echo ""
echo "1️⃣ Checking version consistency..."
VERSION_PY=$(grep '__version__' clauxton/__version__.py | cut -d'"' -f2)
VERSION_TOML=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
VERSION_TEST=$(grep 'assert.*in result.output' tests/cli/test_main.py | grep -oP '\d+\.\d+\.\d+' | head -1)

if [ "$VERSION" != "$VERSION_PY" ]; then
    echo "❌ Version mismatch: __version__.py ($VERSION_PY) != expected ($VERSION)"
    exit 1
fi

if [ "$VERSION" != "$VERSION_TOML" ]; then
    echo "❌ Version mismatch: pyproject.toml ($VERSION_TOML) != expected ($VERSION)"
    exit 1
fi

if [ "$VERSION" != "$VERSION_TEST" ]; then
    echo "❌ Version mismatch: test_main.py ($VERSION_TEST) != expected ($VERSION)"
    exit 1
fi

echo "✅ Version consistent: $VERSION"

# 2. Test marker validation
echo ""
echo "2️⃣ Checking test markers..."
MISSING_MARKERS=$(grep -rn "def test_performance_" tests/ | grep -v "@pytest.mark.performance" || true)
if [ ! -z "$MISSING_MARKERS" ]; then
    echo "❌ Performance tests missing @pytest.mark.performance:"
    echo "$MISSING_MARKERS"
    exit 1
fi

MISSING_SLOW=$(grep -rn "time.sleep.*[5-9]\|time.sleep.*[1-9][0-9]" tests/ | grep -v "@pytest.mark.slow" || true)
if [ ! -z "$MISSING_SLOW" ]; then
    echo "⚠️  Warning: Tests with sleep(5+) should have @pytest.mark.slow"
    echo "$MISSING_SLOW"
fi

echo "✅ Test markers correct"

# 3. Dependency consistency check
echo ""
echo "3️⃣ Checking CI dependency consistency..."
CI_DEPS=$(grep 'pip install -e' .github/workflows/ci.yml | head -1 | grep -oP '\[.*?\]' | tr -d '[]')
OPTIONAL_DEPS=$(grep '^\[project.optional-dependencies\]' -A 50 pyproject.toml | grep -E '^[a-z-]+ = \[' | cut -d' ' -f1)

echo "CI installs: $CI_DEPS"
echo "Available: $OPTIONAL_DEPS"

if ! echo "$CI_DEPS" | grep -q "semantic"; then
    echo "⚠️  Warning: CI does not install 'semantic' dependencies"
fi

echo "✅ Dependency check complete"

# 4. Run comprehensive tests
echo ""
echo "4️⃣ Running comprehensive test suite..."
pytest --cov=clauxton --cov-report=term --cov-report=html -v

# 5. Coverage check
echo ""
echo "5️⃣ Checking coverage..."
COVERAGE=$(pytest --cov=clauxton --cov-report=term-missing | grep "TOTAL" | awk '{print $4}' | tr -d '%')
if [ "$COVERAGE" -lt 90 ]; then
    echo "⚠️  Warning: Coverage is ${COVERAGE}% (target: 90%+)"
else
    echo "✅ Coverage: ${COVERAGE}% (target met)"
fi

# 6. Type checking
echo ""
echo "6️⃣ Type checking (strict mode)..."
mypy --strict clauxton/

# 7. Linting
echo ""
echo "7️⃣ Linting..."
ruff check clauxton/ tests/

# 8. Security scan
echo ""
echo "8️⃣ Security scan..."
bandit -r clauxton/ -ll

# 9. Build check
echo ""
echo "9️⃣ Building package..."
python -m build
twine check dist/*

echo ""
echo "✅ All pre-release checks passed!"
echo ""
echo "Next steps:"
echo "  1. git tag -a v$VERSION -m 'Release v$VERSION'"
echo "  2. git push origin v$VERSION"
echo "  3. gh release create v$VERSION --generate-notes"
echo "  4. twine upload dist/*"
```

**Usage**:

```bash
# Before releasing v0.16.0
chmod +x scripts/pre_release_check.sh
./scripts/pre_release_check.sh 0.16.0

# If all checks pass:
git tag -a v0.16.0 -m "Release v0.16.0"
git push origin v0.16.0
```

---

#### 3.2 CI Environment Simulation

**Test Locally with CI-like Environment**:

```bash
# Simulate CI environment
python -m venv .venv-ci
source .venv-ci/bin/activate
pip install -e ".[dev,parsers-all,semantic]"

# Run exactly what CI runs
pytest --cov=clauxton --cov-report=xml -v

# Check coverage
coverage report
```

**Use Tox for Multi-Python Testing**:

```bash
# Install tox
pip install tox

# Run tests on Python 3.11 and 3.12
tox
```

**`tox.ini`**:

```ini
[tox]
envlist = py311,py312

[testenv]
deps =
    pytest>=7.4
    pytest-cov>=4.1
    pytest-asyncio>=0.21
extras =
    dev
    parsers-all
    semantic
commands =
    pytest --cov=clauxton --cov-report=term -v
```

---

### Phase 4: Post-Commit (Automated)

**GitHub CI Checks** (already configured):

1. ✅ Test matrix (Python 3.11, 3.12)
2. ✅ Lint job (ruff, mypy, bandit)
3. ✅ Build job (python -m build, twine check)
4. ✅ Performance job (weekly/manual)

**If CI fails**:
1. 🔴 **STOP**: Do not proceed
2. 🔍 **Investigate**: Why wasn't this caught locally?
3. 🔧 **Fix**: Address the issue
4. 📝 **Document**: Add to QA process to prevent recurrence
5. 🔄 **Improve**: Update pre-commit hooks if needed

---

## 📋 Release Checklist (v2.0)

### Pre-Release (Mandatory)

- [ ] **1. Version Consistency**
  - [ ] Update `clauxton/__version__.py`
  - [ ] Update `pyproject.toml`
  - [ ] Update `tests/cli/test_main.py::test_version_command`
  - [ ] Update `CHANGELOG.md`
  - [ ] Update `README.md` version references

- [ ] **2. Run Pre-Release Script**
  ```bash
  ./scripts/pre_release_check.sh <version>
  ```

- [ ] **3. Test Marker Validation**
  - [ ] All `test_performance_*` have `@pytest.mark.performance`
  - [ ] All tests with `time.sleep(5+)` have `@pytest.mark.slow`
  - [ ] All integration tests have `@pytest.mark.integration`

- [ ] **4. CI Dependency Check**
  - [ ] `.github/workflows/ci.yml` includes all required dependencies
  - [ ] CI installs: `dev`, `parsers-all`, `semantic`

- [ ] **5. Documentation**
  - [ ] README.md updated with new features
  - [ ] CHANGELOG.md has complete release notes
  - [ ] Migration guide created (if breaking changes)
  - [ ] Quality report created

- [ ] **6. Comprehensive Tests**
  ```bash
  # Run ALL tests (including slow/performance)
  pytest -m "" --cov=clauxton --cov-report=html -v

  # Verify coverage ≥90%
  open htmlcov/index.html
  ```

- [ ] **7. Build Validation**
  ```bash
  python -m build
  twine check dist/*
  ```

### Release (Execute)

- [ ] **8. Create Git Tag**
  ```bash
  git tag -a v<version> -m "Release v<version>"
  git push origin v<version>
  ```

- [ ] **9. Create GitHub Release**
  ```bash
  gh release create v<version> --generate-notes
  ```

- [ ] **10. Publish to PyPI**
  ```bash
  twine upload dist/*
  ```

### Post-Release (Verify)

- [ ] **11. Verify GitHub CI**
  - [ ] All jobs pass (test, lint, build)
  - [ ] Coverage ≥90%

- [ ] **12. Verify PyPI**
  - [ ] Package available: https://pypi.org/project/clauxton/
  - [ ] Installation works: `pip install clauxton==<version>`

- [ ] **13. Create Quality Report**
  - [ ] Document test results
  - [ ] Document coverage metrics
  - [ ] Document any issues found

---

## 🔄 Continuous Improvement

### After Each Release

1. **Post-Mortem** (if issues found):
   - What went wrong?
   - Why wasn't it caught locally?
   - How can we prevent this?

2. **Update Process**:
   - Add new checks to pre-commit hooks
   - Update pre-release script
   - Update documentation

3. **Share Learnings**:
   - Update `QA_PROCESS_IMPROVED.md`
   - Add to `CLAUDE.md` if relevant

---

## 📊 Quality Metrics Tracking

### Before Release

| Metric | Target | Command |
|--------|--------|---------|
| Test Coverage | ≥90% | `pytest --cov=clauxton --cov-report=term` |
| Type Safety | 100% | `mypy --strict clauxton/` |
| Linting | 0 errors | `ruff check clauxton/ tests/` |
| Security | 0 issues | `bandit -r clauxton/ -ll` |
| Build | Pass | `python -m build && twine check dist/*` |

### After Release

| Metric | Target | How to Check |
|--------|--------|--------------|
| CI Pass Rate | 100% | GitHub Actions dashboard |
| PyPI Download | Track | https://pypistats.org/packages/clauxton |
| Issue Reports | <5 per release | GitHub Issues |

---

## 🎓 Best Practices

### Do's ✅

1. **Always run pre-release script before tagging**
2. **Use pre-commit hooks for every commit**
3. **Mark slow/performance tests appropriately**
4. **Test locally with CI-like environment**
5. **Document all QA issues and learnings**
6. **Update version in ALL places simultaneously**
7. **Run full test suite (including slow tests) before release**

### Don'ts ❌

1. **Don't skip pre-commit hooks** (--no-verify)
2. **Don't release without running pre-release script**
3. **Don't push directly to main without tests**
4. **Don't assume CI will catch everything**
5. **Don't forget to update test assertions for new versions**
6. **Don't add long-running tests without markers**
7. **Don't update dependencies without updating CI**

---

## 🚨 Emergency Procedures

### If CI Fails After Release

1. **Assess Severity**:
   - Critical: Rollback immediately
   - High: Fix within 24 hours
   - Medium: Fix in next patch
   - Low: Document and fix in next minor

2. **Quick Fix Process**:
   ```bash
   # Create hotfix branch
   git checkout -b hotfix/v0.15.1

   # Fix issue
   # ...

   # Run pre-release script
   ./scripts/pre_release_check.sh 0.15.1

   # Release
   git tag -a v0.15.1 -m "Hotfix: <description>"
   git push origin v0.15.1
   ```

3. **Post-Mortem**:
   - Document what happened
   - Update QA process to prevent recurrence
   - Add automated check if possible

---

## 📝 Summary

### Old Process (v1.0)

- Manual checklist (error-prone)
- No automated version checking
- No pre-commit hooks
- Issues found in CI

**Result**: 3 issues in v0.15.0

### New Process (v2.0)

- ✅ Automated pre-commit hooks
- ✅ Pre-release validation script
- ✅ Version consistency checking
- ✅ CI environment simulation
- ✅ Test marker validation

**Expected Result**: 0 preventable issues

---

## 🎯 Success Criteria

**QA Process is successful if**:

1. ✅ **95%+ of releases have 0 CI failures**
2. ✅ **Issues are caught locally before push**
3. ✅ **Release process takes <30 minutes** (automation)
4. ✅ **Coverage stays ≥90%**
5. ✅ **No manual checklist errors** (automated)

---

**Last Updated**: 2025-11-04
**Next Review**: After v0.16.0 release
**Owner**: Development Team Lead
