# Session 13 Plan: v0.10.1 Documentation & Polish

**Date**: TBD (Post Session 12)
**Status**: 📋 Ready to Start
**Estimated Duration**: 4-5 hours
**Target**: Documentation improvements and minor polish for v0.10.1 release

---

## 📍 Current Status (After Session 12)

### ✅ Completed in Session 12

**v0.10.0 Release**:
- ✅ Released to PyPI: https://pypi.org/project/clauxton/0.10.0/
- ✅ Released to TestPyPI: https://test.pypi.org/project/clauxton/0.10.0/
- ✅ GitHub Release updated: v0.10.0 - Production Ready
- ✅ Installation verified from PyPI

**Documentation Updates**:
- ✅ README.md fully updated for v0.10.0
  - Removed all Phase 0-3 references
  - Removed old version references (v0.8.0, v0.9.0-beta)
  - Updated Architecture section with complete v0.10.0 structure
  - Updated Installation section with v0.10.0 features
  - Added Usage examples for Undo/Config commands
- ✅ 59 documents archived (sessions, planning, old releases)
- ✅ search-algorithm.md Japanese text fixed

**Quality Metrics**:
- ✅ **758 tests** passing (100% success rate)
- ✅ **91% overall coverage** (Session 11 completion)
- ✅ **99% MCP server coverage**
- ✅ **17 MCP tools** fully tested

### 🔄 Known Issues to Address

**Documentation**:
1. ❌ **docs/technical-design.md** contains 2143 Japanese characters
   - Currently linked from README.md, quick-start.md, roadmap.md
   - Needs English version

2. ❌ **PyPI project page** shows outdated README.md
   - Contains "Phase 1: Complete (v0.9.0-beta)"
   - Contains "Phase 2: Conflict Detection (Complete in v0.9.0-beta)"
   - Contains "Beta Testing 🔄 In Progress"
   - Will be fixed by v0.10.1 release (automatic update)

**Test Coverage**:
- ⚠️ Utils modules: 15-29% coverage (logger, backup_manager, yaml_utils)
- ⚠️ htmlcov/index.html shows 19% coverage (needs verification)

**Missing Documentation**:
- ❌ TEST_WRITING_GUIDE.md (for contributors)
- ❌ English version of technical-design.md

---

## 🎯 Session 13 Goals

### Phase 1: Critical Documentation (MUST DO)

#### 1.1 Create English technical-design.md
**Estimated Time**: 1.5 hours
**Priority**: CRITICAL

**Reason**: Currently Japanese, linked from 3 docs, blocks professional appearance

**Tasks**:
1. Backup Japanese version to `docs/archive/planning/technical-design-ja.md`
2. Create new English `docs/technical-design.md` with:
   - System architecture overview
   - Component design (core, utils, cli, mcp)
   - Data models (Pydantic schemas)
   - Storage design (YAML structure)
   - MCP protocol integration
   - Security considerations
   - Testing approach
3. Update content to reflect v0.10.0 (17 tools, undo, config, etc.)
4. Verify links from README.md, quick-start.md, roadmap.md

**Acceptance Criteria**:
- ✅ No Japanese text in docs/technical-design.md
- ✅ Reflects v0.10.0 architecture (operation_history, confirmation_manager, etc.)
- ✅ All links working
- ✅ Japanese version preserved in archive

---

#### 1.2 Create TEST_WRITING_GUIDE.md
**Estimated Time**: 1.5 hours
**Priority**: HIGH

**Purpose**: Help contributors write high-quality tests

**Content**:
- Testing philosophy (why we test, tests as documentation)
- Test structure (arrange-act-assert / given-when-then)
- Coverage requirements (90% minimum, 95% for core)
- Writing unit tests (fixtures, mocking, parametrize)
- Writing integration tests (tmp_path, end-to-end)
- Testing edge cases (empty inputs, Unicode, errors)
- Testing CLI commands (Click CliRunner)
- Testing MCP tools (call_tool examples)
- Testing async code (if applicable)
- Coverage analysis (pytest-cov, HTML reports)
- Common patterns and examples

**Example Code**:
- Unit test example (test_knowledge_base.py)
- Integration test example (test_cli_kb.py)
- MCP tool test example (test_mcp_kb_tools.py)
- Error handling test example

**Target Audience**: New contributors, developers adding features

---

### Phase 2: Release Preparation (MUST DO)

#### 2.1 Update Version Numbers
**Estimated Time**: 10 minutes

**Files to update**:
- `clauxton/__version__.py`: `__version__ = "0.10.1"`
- `pyproject.toml`: `version = "0.10.1"`

---

#### 2.2 Update CHANGELOG.md
**Estimated Time**: 15 minutes

**Add v0.10.1 entry**:
```markdown
## [0.10.1] - 2025-10-22

### Documentation
- Add TEST_WRITING_GUIDE.md for contributors
- Replace Japanese technical-design.md with English version
- Update README.md to remove Technical Design link (restored after rewrite)

### Fixed
- Japanese text in search-algorithm.md example
- PyPI project page now shows updated README.md

### Internal
- Archive Japanese technical-design.md for reference
```

---

#### 2.3 Build and Test Package
**Estimated Time**: 20 minutes

**Commands**:
```bash
# Quality checks
mypy clauxton
ruff check clauxton tests

# Build
python -m build

# Validate
twine check dist/clauxton-0.10.1*

# Test local install
pip install dist/clauxton-0.10.1-py3-none-any.whl --force-reinstall
clauxton --version  # Should show 0.10.1
```

---

### Phase 3: Release Workflow (MUST DO)

#### 3.1 GitHub Verification
**Estimated Time**: 10 minutes

**Tasks**:
1. Push all changes to GitHub
2. **CRITICAL**: Verify README.md on GitHub web interface
   - Check all links work
   - Check formatting is correct
   - Check no Japanese text visible (except in archive)
   - Check Technical Design link points to English version
3. Only proceed if GitHub README looks perfect

---

#### 3.2 TestPyPI Upload
**Estimated Time**: 10 minutes

**Commands**:
```bash
twine upload --repository-url https://test.pypi.org/legacy/ \
  dist/clauxton-0.10.1* \
  --username __token__ \
  --password <TestPyPI-token>
```

**Verification**:
1. Visit https://test.pypi.org/project/clauxton/0.10.1/
2. **CRITICAL**: Check project description page
   - Verify no "Phase 1 (v0.9.0-beta)" references
   - Verify no "Beta Testing" text
   - Verify updated content matches GitHub README
3. Only proceed if TestPyPI page looks correct

---

#### 3.3 Production PyPI Upload
**Estimated Time**: 10 minutes

**Commands**:
```bash
twine upload dist/clauxton-0.10.1* \
  --username __token__ \
  --password <PyPI-token>
```

**Verification**:
1. Visit https://pypi.org/project/clauxton/0.10.1/
2. **CRITICAL**: Check project description page
3. Test installation:
   ```bash
   pip install clauxton==0.10.1
   clauxton --version
   ```

---

#### 3.4 GitHub Release
**Estimated Time**: 10 minutes

**Create release**:
```bash
# Create and push tag
git tag -a v0.10.1 -m "Release v0.10.1 - Documentation & Polish

- Add TEST_WRITING_GUIDE.md for contributors
- Replace Japanese technical-design.md with English version
- Fix PyPI project page showing outdated information
- Minor documentation improvements"

git push origin v0.10.1

# Create GitHub release
gh release create v0.10.1 \
  --title "v0.10.1 - Documentation & Polish" \
  --notes "See CHANGELOG.md for details" \
  dist/clauxton-0.10.1-py3-none-any.whl \
  dist/clauxton-0.10.1.tar.gz
```

---

## 🔄 Phase 4: Optional Improvements (IF TIME PERMITS)

### 4.1 PERFORMANCE_GUIDE.md (Optional)
**Estimated Time**: 1 hour
**Priority**: LOW (can defer to v0.10.2)

**Content**:
- Performance targets (KB operations <100ms, task operations <200ms)
- Bulk import optimization (YAML parsing, validation)
- TF-IDF search optimization (caching, indexing)
- File I/O optimization (atomic writes, buffering)
- Profiling guide (cProfile, line_profiler)
- Benchmarking patterns
- Common bottlenecks

---

### 4.2 Utils Module Tests (Optional)
**Estimated Time**: 1-2 hours
**Priority**: LOW (91% coverage is acceptable)

**Current coverage**:
- `backup_manager.py`: 23% (13/56 statements)
- `logger.py`: 15% (12/79 statements)
- `yaml_utils.py`: 16% (10/61 statements)
- `file_utils.py`: 29% (6/21 statements)

**Target**: Add tests to reach 50%+ coverage (not critical)

---

### 4.3 Bandit CI/CD Integration (Optional)
**Estimated Time**: 30 minutes
**Priority**: LOW (manual scan already done in Session 8)

**Implementation**:
```yaml
# .github/workflows/ci.yml
bandit:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    - run: pip install bandit
    - run: bandit -r clauxton -ll -f json -o bandit-report.json
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: bandit-report
        path: bandit-report.json
```

---

## 📊 Success Criteria

### MUST Have (v0.10.1 Release)
- ✅ docs/technical-design.md is English
- ✅ TEST_WRITING_GUIDE.md exists and is comprehensive
- ✅ PyPI project page shows updated README.md (no Phase/beta references)
- ✅ v0.10.1 released to PyPI
- ✅ GitHub release created with v0.10.1 tag
- ✅ All links verified on GitHub
- ✅ All quality checks pass (mypy, ruff)
- ✅ Package installs correctly from PyPI

### NICE to Have (Can defer)
- 🔄 PERFORMANCE_GUIDE.md
- 🔄 Utils module tests (50%+ coverage)
- 🔄 Bandit in CI/CD

---

## 🚀 Release Workflow Summary

```
1. Create English technical-design.md (1.5h)
   ↓
2. Create TEST_WRITING_GUIDE.md (1.5h)
   ↓
3. Update version numbers (10min)
   ↓
4. Update CHANGELOG.md (15min)
   ↓
5. Run quality checks (mypy, ruff) (5min)
   ↓
6. Build package (5min)
   ↓
7. Validate with twine (5min)
   ↓
8. Test local install (5min)
   ↓
9. Commit and push to GitHub (5min)
   ↓
10. ⚠️ VERIFY GitHub README.md (10min) ⚠️
   ↓
11. Upload to TestPyPI (10min)
   ↓
12. ⚠️ VERIFY TestPyPI project page (10min) ⚠️
   ↓
13. Upload to PyPI (10min)
   ↓
14. ⚠️ VERIFY PyPI project page (10min) ⚠️
   ↓
15. Test install from PyPI (5min)
   ↓
16. Create GitHub release (10min)
   ↓
17. Done! 🎉
```

**Total Estimated Time**: 4-5 hours (core tasks only)

---

## 📝 Notes for Next Session

### Important Reminders
1. **Always verify on GitHub first** before uploading to PyPI
2. **Use TestPyPI** to catch README rendering issues
3. **Check PyPI project page** after upload to ensure correct display
4. **Japanese version of technical-design.md** preserved in archive for reference
5. **Coverage at 91%** is production-ready; utils tests are optional polish

### Files to Check
- `docs/technical-design.md` - Must be English, no Japanese
- `docs/TEST_WRITING_GUIDE.md` - Must exist
- `README.md` - All links working
- `CHANGELOG.md` - v0.10.1 entry added

### Post-Release Verification
- [ ] PyPI shows updated README (no "Phase 1 (v0.9.0-beta)")
- [ ] GitHub release v0.10.1 exists
- [ ] `pip install clauxton` gives v0.10.1
- [ ] All documentation links work

---

**Next Session**: Execute this plan to release v0.10.1
