# Test Requirements Checklist

**Purpose**: Automatic test requirement validation for new features
**Usage**: Check this list when adding ANY new feature
**Target**: Ensure comprehensive test coverage from day 1

---

## 📋 How to Use This Checklist

### For New Features

When adding a new feature, copy this checklist and mark completed items:

```markdown
## Feature: [Feature Name]

### Test Requirements
- [ ] Unit Tests
- [ ] Integration Tests
- [ ] Scenario Tests
- [ ] Performance Tests
- [ ] Security Tests
- [ ] Error Handling Tests
- [ ] Documentation Tests
```

### Automatic Validation

This checklist is integrated into:
1. **CLAUDE.md** - Development guidelines
2. **Pre-release script** - Automated validation
3. **Code review** - Manual verification

---

## 🎯 Test Requirements by Category

### 1. Unit Tests (REQUIRED for ALL features)

**Minimum Coverage**: 95%

#### Checklist

- [ ] **Happy Path Tests**
  - [ ] Feature works with valid inputs
  - [ ] Returns expected outputs
  - [ ] State changes correctly

- [ ] **Edge Cases**
  - [ ] Empty inputs
  - [ ] Boundary values (0, 1, max)
  - [ ] Maximum size inputs
  - [ ] Unicode characters (日本語, emoji)

- [ ] **Error Cases**
  - [ ] Invalid inputs raise appropriate exceptions
  - [ ] Error messages are clear and actionable
  - [ ] No silent failures

- [ ] **State Transitions**
  - [ ] Valid state changes work
  - [ ] Invalid state changes are rejected
  - [ ] State is consistent after operations

#### Example

```python
# Feature: Memory.add()
def test_memory_add_valid_entry()          # Happy path
def test_memory_add_empty_content()        # Edge case
def test_memory_add_duplicate_id()         # Error case
def test_memory_add_updates_state()        # State transition
```

---

### 2. Integration Tests (REQUIRED for multi-component features)

**Minimum Coverage**: 1 integration test per feature

#### Checklist

- [ ] **Component Integration**
  - [ ] Feature works with related components
  - [ ] Data flows correctly between components
  - [ ] No integration conflicts

- [ ] **API Integration**
  - [ ] CLI commands work end-to-end
  - [ ] MCP tools work end-to-end
  - [ ] Python API works end-to-end

- [ ] **Storage Integration**
  - [ ] Data persists correctly
  - [ ] Data loads correctly
  - [ ] Data migrates correctly (if applicable)

#### Example

```python
# Feature: Memory Migration
def test_migrate_kb_to_memory_integration()     # KB → Memory
def test_memory_search_after_migration()        # Search works
def test_memory_cli_workflow()                  # CLI integration
```

---

### 3. Scenario Tests (REQUIRED for user-facing features)

**Minimum Coverage**: 1 complete user scenario

#### Checklist

- [ ] **Complete User Journey**
  - [ ] User can discover feature
  - [ ] User can use feature successfully
  - [ ] User gets feedback at each step
  - [ ] User can recover from errors

- [ ] **Common Workflows**
  - [ ] Most common use case tested
  - [ ] Second most common use case tested
  - [ ] Error recovery workflow tested

- [ ] **Cross-Feature Scenarios**
  - [ ] Feature works with related features
  - [ ] Feature doesn't break existing features

#### Example

```python
# Feature: Memory System
def test_complete_memory_migration_workflow():
    """
    Scenario: User migrates from v0.14.0 to v0.15.0
    1. User has 100 KB entries + 50 tasks
    2. User runs: clauxton migrate memory --dry-run
    3. User reviews migration plan
    4. User runs: clauxton migrate memory --confirm
    5. User verifies data preserved
    6. User searches across memory types
    """
```

---

### 4. Performance Tests (REQUIRED for data-intensive features)

**Minimum Coverage**: 1 performance test if feature handles >100 items

#### Checklist

- [ ] **Small Dataset** (10-50 items)
  - [ ] Operation completes quickly (<100ms)
  - [ ] Memory usage acceptable (<50MB)

- [ ] **Medium Dataset** (100-500 items)
  - [ ] Operation completes in reasonable time (<1s)
  - [ ] Memory usage acceptable (<200MB)

- [ ] **Large Dataset** (1000+ items) - Optional but recommended
  - [ ] Operation doesn't timeout (<30s)
  - [ ] Memory usage doesn't grow unbounded

#### Example

```python
# Feature: Memory.search()
@pytest.mark.performance
def test_memory_search_performance_100_entries()

@pytest.mark.performance
def test_memory_search_performance_1000_entries()
```

#### Marker Required

```python
@pytest.mark.performance  # MUST use this marker
def test_performance_large_dataset():
    ...
```

---

### 5. Security Tests (REQUIRED for features handling user input)

**Minimum Coverage**: 1 security test if feature accepts external input

#### Checklist

- [ ] **Input Validation**
  - [ ] Malicious inputs rejected
  - [ ] SQL injection impossible (if applicable)
  - [ ] Command injection impossible
  - [ ] Path traversal impossible

- [ ] **Output Sanitization**
  - [ ] Output doesn't leak sensitive data
  - [ ] Output doesn't contain executable code

- [ ] **Access Control** (if applicable)
  - [ ] Unauthorized access prevented
  - [ ] File permissions correct

#### Example

```python
# Feature: Memory.add()
def test_memory_add_sanitizes_input()
def test_memory_add_rejects_path_traversal()
def test_memory_add_validates_id_format()
```

---

### 6. Error Handling Tests (REQUIRED for ALL features)

**Minimum Coverage**: 1 error test per error condition

#### Checklist

- [ ] **Expected Errors**
  - [ ] Clear error messages shown
  - [ ] Suggestions for fixes provided
  - [ ] System remains in consistent state

- [ ] **Unexpected Errors**
  - [ ] Graceful degradation
  - [ ] No data corruption
  - [ ] Recovery instructions provided

- [ ] **Partial Failures**
  - [ ] Rollback works correctly
  - [ ] User notified of partial completion
  - [ ] Resume/retry possible

#### Example

```python
# Feature: Memory Migration
def test_migration_rollback_on_error()
def test_migration_partial_completion_recovery()
def test_migration_disk_full_error()
```

---

### 7. Documentation Tests (REQUIRED for ALL features)

**Minimum Coverage**: Verify documentation exists

#### Checklist

- [ ] **Code Documentation**
  - [ ] Docstrings exist (Google style)
  - [ ] Parameters documented
  - [ ] Return values documented
  - [ ] Exceptions documented
  - [ ] Examples provided

- [ ] **User Documentation**
  - [ ] README.md updated
  - [ ] CLI help text updated
  - [ ] Migration guide (if breaking change)

- [ ] **Test Documentation**
  - [ ] Test docstrings explain what/why
  - [ ] Complex tests have comments

#### Example

```python
def add(entry: MemoryEntry) -> str:
    """
    Add memory entry to store.

    Args:
        entry: MemoryEntry to add

    Returns:
        Memory ID (e.g., "MEM-20260127-001")

    Raises:
        ValidationError: If entry is invalid
        DuplicateError: If entry ID already exists

    Example:
        >>> memory = Memory(Path("."))
        >>> entry = MemoryEntry(id="MEM-...", ...)
        >>> memory_id = memory.add(entry)
    """
```

---

## 🔄 Feature-Specific Requirements

### For CLI Commands

Additional requirements:

- [ ] **CLI Integration**
  - [ ] Help text accurate
  - [ ] Options work correctly
  - [ ] Interactive mode tested (if applicable)
  - [ ] Error messages user-friendly

#### Example

```python
def test_memory_add_cli_help()
def test_memory_add_cli_with_options()
def test_memory_add_cli_interactive()
def test_memory_add_cli_error_message()
```

---

### For MCP Tools

Additional requirements:

- [ ] **MCP Integration**
  - [ ] Tool registered correctly
  - [ ] Tool description accurate
  - [ ] Parameters validated
  - [ ] Error handling works
  - [ ] Tool chaining tested (if applicable)

#### Example

```python
@pytest.mark.asyncio
async def test_memory_add_mcp_tool()

@pytest.mark.asyncio
async def test_memory_add_mcp_error_handling()

@pytest.mark.asyncio
async def test_memory_tool_chaining()
```

---

### For Data Migration Features

Additional requirements:

- [ ] **Migration Safety**
  - [ ] Dry-run mode works
  - [ ] Backup created automatically
  - [ ] Rollback tested
  - [ ] Data integrity verified
  - [ ] Large dataset tested

#### Example

```python
def test_migration_dry_run()
def test_migration_creates_backup()
def test_migration_rollback()
def test_migration_data_integrity()
def test_migration_large_dataset()
```

---

### For Search/Query Features

Additional requirements:

- [ ] **Search Quality**
  - [ ] Relevance ranking tested
  - [ ] Edge queries tested (empty, special chars)
  - [ ] Performance tested (large datasets)
  - [ ] Fallback tested (if applicable)

#### Example

```python
def test_search_relevance_ranking()
def test_search_empty_query()
def test_search_unicode_query()
def test_search_performance_1000_entries()
def test_search_fallback_no_sklearn()
```

---

## 📊 Coverage Requirements Summary

| Feature Type | Unit | Integration | Scenario | Performance | Security | Error | Documentation |
|--------------|------|-------------|----------|-------------|----------|-------|---------------|
| **Core Logic** | ✅ 95%+ | ✅ 1+ | ✅ 1+ | ⚠️ Optional | ⚠️ If input | ✅ 1+ | ✅ Required |
| **CLI Command** | ✅ 90%+ | ✅ 1+ | ✅ 1+ | ⚠️ Optional | ✅ Required | ✅ 1+ | ✅ Required |
| **MCP Tool** | ✅ 95%+ | ✅ 1+ | ✅ 1+ | ⚠️ Optional | ✅ Required | ✅ 1+ | ✅ Required |
| **Data Migration** | ✅ 95%+ | ✅ 2+ | ✅ 2+ | ✅ Required | ⚠️ Optional | ✅ 2+ | ✅ Required |
| **Search/Query** | ✅ 90%+ | ✅ 1+ | ✅ 1+ | ✅ Required | ⚠️ If external | ✅ 1+ | ✅ Required |

---

## 🚨 Blocking Requirements

These tests are **REQUIRED** before merging:

### Minimum Viable Tests (Must Have)

1. ✅ **At least 1 unit test** (happy path)
2. ✅ **At least 1 error test**
3. ✅ **Type checking passes** (mypy --strict)
4. ✅ **Linting passes** (ruff check)
5. ✅ **Docstring exists** (function/class level)

### Quality Tests (Should Have)

6. ⚠️ **At least 1 integration test**
7. ⚠️ **At least 1 scenario test** (for user-facing features)
8. ⚠️ **Edge cases tested** (empty, boundary, unicode)
9. ⚠️ **Performance test** (if data-intensive)
10. ⚠️ **Security test** (if user input)

### Documentation (Should Have)

11. ⚠️ **README.md updated** (if user-facing)
12. ⚠️ **CHANGELOG.md updated**
13. ⚠️ **Migration guide** (if breaking change)

---

## 🔍 Review Checklist for Code Reviewers

Use this when reviewing PRs:

```markdown
## Test Review Checklist

### Coverage
- [ ] Unit tests exist and cover main functionality
- [ ] Edge cases tested (empty, boundary, unicode)
- [ ] Error cases tested
- [ ] Integration test exists (if multi-component)
- [ ] Scenario test exists (if user-facing)

### Quality
- [ ] Tests are clear and well-named
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] No flaky tests (deterministic)
- [ ] Fast tests (<1s per test for unit tests)
- [ ] Performance tests use @pytest.mark.performance

### Documentation
- [ ] Docstrings exist and are complete
- [ ] README.md updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] Migration guide exists (if breaking)

### Security
- [ ] Input validation tested (if user input)
- [ ] No hardcoded secrets
- [ ] Safe file operations (no path traversal)

### Special Requirements
- [ ] CLI help text tested (if CLI command)
- [ ] MCP tool integration tested (if MCP tool)
- [ ] Migration safety tested (if migration)
- [ ] Rollback tested (if data modification)
```

---

## 📚 Examples by Feature Type

### Example 1: New Core Function

```python
# Feature: Memory.find_related()

# ✅ Unit Tests (5 tests minimum)
def test_find_related_explicit_links()      # Happy path
def test_find_related_shared_tags()         # Happy path
def test_find_related_empty_list()          # Edge case
def test_find_related_nonexistent_id()      # Error case
def test_find_related_threshold()           # Parameter validation

# ✅ Integration Test
def test_find_related_with_memory_store()   # With storage

# ✅ Error Handling
def test_find_related_corrupted_data()      # Corruption handling

# ✅ Documentation
# Docstring with Args, Returns, Raises, Example
```

### Example 2: New CLI Command

```python
# Feature: clauxton memory related <id>

# ✅ Unit Tests (core logic)
def test_memory_related_logic()

# ✅ Integration Tests
def test_memory_related_cli_command()
def test_memory_related_cli_help()
def test_memory_related_cli_options()

# ✅ Scenario Test
def test_memory_related_user_workflow():
    """
    User adds memories, links them, queries related
    """

# ✅ Error Handling
def test_memory_related_cli_invalid_id()
def test_memory_related_cli_no_related()

# ✅ Documentation
# Help text, README update
```

### Example 3: New MCP Tool

```python
# Feature: memory_find_related()

# ✅ Unit Tests (core logic)
# (Same as core function)

# ✅ MCP Integration Tests
@pytest.mark.asyncio
async def test_memory_find_related_mcp()
async def test_memory_find_related_mcp_error()

# ✅ Scenario Test
@pytest.mark.asyncio
async def test_mcp_memory_workflow():
    """
    Use MCP tools to search → find related → view details
    """

# ✅ Security
async def test_memory_find_related_mcp_validates_input()

# ✅ Documentation
# MCP documentation updated
```

---

## 🎯 Quick Reference

### Minimum Tests Required

| Feature Type | Minimum Tests | Estimated Time |
|--------------|---------------|----------------|
| **Simple function** | 3-5 unit tests | 30 minutes |
| **Complex function** | 5-10 unit tests + 1 integration | 1-2 hours |
| **CLI command** | 5-8 unit + 2-3 integration + 1 scenario | 2-3 hours |
| **MCP tool** | 5-8 unit + 2-3 integration + 1 scenario | 2-3 hours |
| **Data migration** | 8-10 unit + 3-4 integration + 2 scenarios | 4-6 hours |
| **Major feature** | 15-20 unit + 5+ integration + 3+ scenarios | 1-2 days |

### Test Markers

```python
# Performance tests (excluded by default)
@pytest.mark.performance

# Slow tests (>5 seconds)
@pytest.mark.slow

# Integration tests
@pytest.mark.integration

# Async tests
@pytest.mark.asyncio
```

---

## ✅ Automated Validation

This checklist is validated by:

### Pre-commit Hooks

```bash
# Runs on every commit
- Type checking (mypy)
- Linting (ruff)
- Fast tests (unit tests only)
- Security scan (bandit)
```

### Pre-release Script

```bash
# Runs before release
./scripts/pre_release_check.sh <version>

# Validates:
- All tests pass
- Coverage ≥90%
- Documentation complete
- Test markers correct
```

### CI/CD

```bash
# Runs on push to main
- All tests (including integration)
- Coverage report to Codecov
- Build validation
```

---

## 📖 See Also

- **Test Writing Guide**: `docs/TEST_WRITING_GUIDE.md`
- **Test Coverage Analysis**: `docs/TEST_COVERAGE_ANALYSIS.md`
- **QA Process**: `docs/QA_PROCESS_IMPROVED.md`
- **CLAUDE.md**: Development guidelines with test requirements

---

**Last Updated**: 2025-11-04
**Next Review**: After each major release
**Owner**: QA Team
