#!/bin/bash
#
# Pre-Release Validation Script for Clauxton
#
# Usage: ./scripts/pre_release_check.sh <version>
# Example: ./scripts/pre_release_check.sh 0.16.0
#
# This script validates that all release requirements are met before tagging.
#

set -e  # Exit on error

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "❌ Usage: $0 <version>"
    echo "   Example: $0 0.16.0"
    exit 1
fi

echo "🔍 Pre-Release Validation for v$VERSION"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0
WARNINGS=0

# ============================================================================
# 1. Version Consistency Check
# ============================================================================
echo "1️⃣  Checking version consistency..."

VERSION_PY=$(grep '__version__' clauxton/__version__.py | cut -d'"' -f2)
VERSION_TOML=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
VERSION_TEST=$(grep 'assert.*in result.output' tests/cli/test_main.py | grep -oP '\d+\.\d+\.\d+' | head -1 || echo "")

if [ "$VERSION" != "$VERSION_PY" ]; then
    echo -e "${RED}❌ Version mismatch: __version__.py ($VERSION_PY) != expected ($VERSION)${NC}"
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}✅ __version__.py: $VERSION_PY${NC}"
fi

if [ "$VERSION" != "$VERSION_TOML" ]; then
    echo -e "${RED}❌ Version mismatch: pyproject.toml ($VERSION_TOML) != expected ($VERSION)${NC}"
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}✅ pyproject.toml: $VERSION_TOML${NC}"
fi

if [ ! -z "$VERSION_TEST" ] && [ "$VERSION" != "$VERSION_TEST" ]; then
    echo -e "${RED}❌ Version mismatch: test_main.py ($VERSION_TEST) != expected ($VERSION)${NC}"
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}✅ test_main.py: $VERSION_TEST${NC}"
fi

echo ""

# ============================================================================
# 2. Test Marker Validation
# ============================================================================
echo "2️⃣  Checking test markers..."

# Check for performance tests without marker
MISSING_PERF=$(grep -rn "def test_performance" tests/ --include="*.py" | while read line; do
    file=$(echo "$line" | cut -d: -f1)
    lineno=$(echo "$line" | cut -d: -f2)
    # Check if @pytest.mark.performance exists in previous 5 lines
    prev_line=$((lineno - 1))
    if [ -f "$file" ] && [ "$lineno" -gt 1 ]; then
        if ! sed -n "${prev_line}p" "$file" 2>/dev/null | grep -q "@pytest.mark.performance"; then
            echo "$line"
        fi
    fi
done)

if [ ! -z "$MISSING_PERF" ]; then
    echo -e "${RED}❌ Performance tests missing @pytest.mark.performance:${NC}"
    echo "$MISSING_PERF"
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}✅ All performance tests have markers${NC}"
fi

# Check for slow tests
MISSING_SLOW=$(grep -rn "time.sleep([5-9]\|[1-9][0-9]" tests/ --include="*.py" 2>/dev/null | while read line; do
    file=$(echo "$line" | cut -d: -f1)
    lineno=$(echo "$line" | cut -d: -f2)
    prev_line=$((lineno - 5))
    if [ -f "$file" ] && [ "$lineno" -gt 5 ]; then
        if ! sed -n "${prev_line},${lineno}p" "$file" 2>/dev/null | grep -q "@pytest.mark.slow"; then
            echo "$line"
        fi
    fi
done)

if [ ! -z "$MISSING_SLOW" ]; then
    echo -e "${YELLOW}⚠️  Tests with sleep(5+) should have @pytest.mark.slow:${NC}"
    echo "$MISSING_SLOW"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ============================================================================
# 3. CI Dependency Consistency
# ============================================================================
echo "3️⃣  Checking CI dependency consistency..."

if ! grep -q 'semantic' .github/workflows/ci.yml; then
    echo -e "${YELLOW}⚠️  CI does not install 'semantic' dependencies${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ CI includes semantic dependencies${NC}"
fi

if ! grep -q 'parsers-all' .github/workflows/ci.yml; then
    echo -e "${YELLOW}⚠️  CI does not install 'parsers-all' dependencies${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ CI includes parsers-all dependencies${NC}"
fi

echo ""

# ============================================================================
# 4. Type Checking
# ============================================================================
echo "4️⃣  Type checking (strict mode)..."

if ! mypy --strict clauxton/ 2>&1 | grep -q "Success: no issues found"; then
    echo -e "${RED}❌ Type checking failed${NC}"
    mypy --strict clauxton/
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}✅ Type checking passed${NC}"
fi

echo ""

# ============================================================================
# 5. Linting
# ============================================================================
echo "5️⃣  Linting..."

if ! ruff check clauxton/ tests/ > /dev/null 2>&1; then
    echo -e "${RED}❌ Linting failed${NC}"
    ruff check clauxton/ tests/
    FAILURES=$((FAILURES + 1))
else
    echo -e "${GREEN}✅ Linting passed${NC}"
fi

echo ""

# ============================================================================
# 6. Security Scan
# ============================================================================
echo "6️⃣  Security scan..."

BANDIT_OUTPUT=$(bandit -r clauxton/ -ll -f txt 2>&1 || true)
if echo "$BANDIT_OUTPUT" | grep -q "No issues identified"; then
    echo -e "${GREEN}✅ Security scan passed (0 vulnerabilities)${NC}"
else
    echo -e "${RED}❌ Security issues found:${NC}"
    echo "$BANDIT_OUTPUT"
    FAILURES=$((FAILURES + 1))
fi

echo ""

# ============================================================================
# 7. Fast Tests
# ============================================================================
echo "7️⃣  Running fast tests (excluding slow/performance)..."

if pytest -m "not slow and not performance" -q --tb=short; then
    echo -e "${GREEN}✅ Fast tests passed${NC}"
else
    echo -e "${RED}❌ Fast tests failed${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""

# ============================================================================
# 8. Build Check
# ============================================================================
echo "8️⃣  Building package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info

if python -m build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Package built successfully${NC}"

    if twine check dist/* > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Package validation passed${NC}"
    else
        echo -e "${RED}❌ Package validation failed${NC}"
        twine check dist/*
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${RED}❌ Package build failed${NC}"
    python -m build
    FAILURES=$((FAILURES + 1))
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "========================================"
echo "📊 Pre-Release Check Summary"
echo "========================================"
echo ""

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"

    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found (non-blocking)${NC}"
    fi

    echo ""
    echo "🚀 Ready to release v$VERSION"
    echo ""
    echo "Next steps:"
    echo "  1. Review CHANGELOG.md"
    echo "  2. git add -A && git commit -m 'chore: prepare v$VERSION release'"
    echo "  3. git tag -a v$VERSION -m 'Release v$VERSION'"
    echo "  4. git push origin main"
    echo "  5. git push origin v$VERSION"
    echo "  6. gh release create v$VERSION --generate-notes"
    echo "  7. twine upload dist/*"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $FAILURES check(s) failed${NC}"

    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found${NC}"
    fi

    echo ""
    echo "🛑 Please fix the issues above before releasing."
    echo ""
    exit 1
fi
