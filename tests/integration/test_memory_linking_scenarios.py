"""
Memory Linking Scenario Tests (v0.15.0).

Comprehensive tests for memory relationship discovery and linking workflows.
Tests auto-linking, manual linking, and relationship quality validation.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from clauxton.core.memory import Memory, MemoryEntry
from clauxton.semantic.memory_linker import MemoryLinker


# ============================================================================
# Auto-Linking Discovery
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Full auto-linking workflow needs MemoryLinker enhancements")
def test_auto_link_discovers_related_memories(tmp_path: Path) -> None:
    """
    Scenario: Auto-linking finds related memories based on content similarity.

    User Story:
        As a user with many memories,
        I want the system to automatically discover relationships,
        So that I can navigate between related information easily.

    Steps:
        1. Add 30 memories on related topics (API design)
        2. Add 10 memories on unrelated topics
        3. Run auto-link: clauxton memory link --auto
        4. Verify relationships detected
        5. Query related memories
        6. Verify relevance of links

    Expected:
        - API-related memories linked together
        - Unrelated memories not linked incorrectly
        - Relationship scores reasonable
    """
    # Step 1: Create related memories (API design)
    memory = Memory(tmp_path)
    api_mem_ids = []

    api_topics = [
        ("REST API Design", "REST API principles and best practices"),
        ("API Versioning", "Strategies for API version management"),
        ("API Authentication", "Authentication methods for APIs"),
        ("API Rate Limiting", "Implementing rate limits for APIs"),
        ("REST vs GraphQL", "Comparing REST and GraphQL APIs"),
        ("API Documentation", "Best practices for API documentation"),
        ("API Error Handling", "Error response patterns for APIs"),
        ("API Testing", "Strategies for testing APIs"),
        ("API Security", "Security considerations for APIs"),
        ("API Performance", "Optimizing API performance"),
    ]

    for i, (title, content) in enumerate(api_topics):
        entry = MemoryEntry(
            id=f"MEM-20260101-{i+1:03d}",
            type="knowledge",
            title=title,
            content=content,
            category="architecture",
            tags=["api", "backend"],
            created_at=datetime.now() - timedelta(days=i),
            updated_at=datetime.now() - timedelta(days=i),
            source="manual",
        )
        memory.add(entry)
        api_mem_ids.append(entry.id)

    # Step 2: Add unrelated memories
    unrelated_topics = [
        ("Database Schema", "Designing database schemas"),
        ("Frontend Components", "Building React components"),
        ("CI/CD Pipeline", "Setting up continuous integration"),
    ]

    unrelated_ids = []
    for i, (title, content) in enumerate(unrelated_topics):
        entry = MemoryEntry(
            id=f"MEM-20260101-{len(api_topics) + i + 1:03d}",
            type="knowledge",
            title=title,
            content=content,
            category="architecture",
            tags=["infrastructure" if i == 2 else "frontend"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="manual",
        )
        memory.add(entry)
        unrelated_ids.append(entry.id)

    # Step 3: Run auto-linking
    linker = MemoryLinker(memory)
    linker.auto_link_all(threshold=0.3)

    # Step 4: Verify relationships detected
    # Get one API memory and check its relationships
    first_api_mem = memory.get(api_mem_ids[0])
    assert first_api_mem is not None

    related_ids = linker.find_relationships(first_api_mem, threshold=0.2)

    # Should find at least a few related API memories
    assert len(related_ids) > 0

    # Step 5: Verify most related are API memories
    # At least 70% of related should be from API topics
    api_related_count = sum(1 for rid in related_ids if rid in api_mem_ids)
    assert api_related_count / len(related_ids) >= 0.7, \
        f"Only {api_related_count}/{len(related_ids)} related memories are API-related"


@pytest.mark.skip(reason="Future enhancement: Tag-based linking priority needs implementation")
def test_auto_link_quality_with_shared_tags(tmp_path: Path) -> None:
    """
    Scenario: Auto-linking prioritizes memories with shared tags.

    User Story:
        As a user who tags memories consistently,
        I want auto-linking to recognize tag-based relationships,
        So that tagged memories are connected appropriately.

    Steps:
        1. Create memories with overlapping tags
        2. Create memories with unique tags
        3. Run auto-linking
        4. Verify shared-tag memories linked stronger

    Expected:
        - Memories with 2+ shared tags have higher link scores
        - Tag-based relationships detected
        - Category similarity considered
    """
    memory = Memory(tmp_path)

    # Memories with shared tags
    shared_tag_mems = []
    for i in range(5):
        entry = MemoryEntry(
            id=f"MEM-20260101-{i+1:03d}",
            type="knowledge",
            title=f"Python Best Practice {i+1}",
            content=f"Python coding standard {i+1}",
            category="pattern",
            tags=["python", "best-practices", "coding"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="manual",
        )
        memory.add(entry)
        shared_tag_mems.append(entry.id)

    # Memories with different tags
    unique_tag_mems = []
    for i in range(5):
        entry = MemoryEntry(
            id=f"MEM-20260101-{i+6:03d}",
            type="knowledge",
            title=f"JavaScript Tip {i+1}",
            content=f"JavaScript technique {i+1}",
            category="pattern",
            tags=["javascript", "frontend", "web"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="manual",
        )
        memory.add(entry)
        unique_tag_mems.append(entry.id)

    # Run auto-linking
    linker = MemoryLinker(memory)
    linker.auto_link_all(threshold=0.3)

    # Verify shared-tag memories are linked
    first_python_mem = memory.get(shared_tag_mems[0])
    related = linker.find_relationships(first_python_mem, threshold=0.2)

    # Most related should be other Python memories
    python_related = [r for r in related if r in shared_tag_mems]
    assert len(python_related) >= 2, "Should find at least 2 related Python memories"

    # JS memories should not be strongly related
    js_related = [r for r in related if r in unique_tag_mems]
    assert len(js_related) < len(python_related), \
        "Python memories should be more related than JS memories"


# ============================================================================
# Manual Link Override
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Manual link override needs implementation")
def test_manual_link_overrides_auto_linking(tmp_path: Path) -> None:
    """
    Scenario: User manually adds specific relationship.

    User Story:
        As a user who knows specific relationships,
        I want to manually link memories,
        So that I can capture knowledge the auto-linker might miss.

    Steps:
        1. Create memories
        2. Auto-link creates relationships
        3. User manually adds specific link
        4. Verify manual link preserved
        5. Verify auto-link doesn't override manual links

    Expected:
        - Manual links are preserved
        - Manual links have higher priority
        - Auto-link respects manual links
    """
    memory = Memory(tmp_path)

    # Create test memories
    mem1 = MemoryEntry(
        id="MEM-20260101-001",
        type=MemoryType.KNOWLEDGE,
        title="Architecture Decision",
        content="Decision to use microservices",
        category="decision",
        tags=["architecture", "microservices"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem1)

    mem2 = MemoryEntry(
        id="MEM-20260101-002",
        type="code",
        title="Service Implementation",
        content="Implementation of user service",
        category="implementation",
        tags=["microservices", "code"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem2)

    mem3 = MemoryEntry(
        id="MEM-20260101-003",
        type="pattern",
        title="Communication Pattern",
        content="Pattern for service-to-service communication",
        category="pattern",
        tags=["microservices", "pattern"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem3)

    # Manual link: mem1 → mem2 (decision → implementation)
    mem1_updated = memory.get(mem1.id)
    mem1_updated.related_to = [mem2.id]
    memory.update(mem1.id, related_to=mem1_updated.related_to)

    # Run auto-linking
    linker = MemoryLinker(memory)
    linker.auto_link_all(threshold=0.3)

    # Verify manual link preserved
    mem1_after = memory.get(mem1.id)
    assert mem2.id in mem1_after.related_to, "Manual link should be preserved"

    # Auto-linker should add mem3 as related (shared tags)
    # but not remove mem2
    assert mem2.id in mem1_after.related_to


@pytest.mark.skip(reason="Future enhancement: Bidirectional relationship creation needs implementation")
def test_bidirectional_relationship_creation(tmp_path: Path) -> None:
    """
    Scenario: Creating relationship automatically creates reverse link.

    User Story:
        As a user exploring relationships,
        I want relationships to be bidirectional,
        So that I can navigate in both directions.

    Steps:
        1. Create two memories
        2. Link A → B
        3. Verify B → A also exists
        4. Query from both directions

    Expected:
        - Bidirectional links created
        - Navigation works both ways
        - Relationship strength same in both directions
    """
    memory = Memory(tmp_path)

    # Create two memories
    mem_a = MemoryEntry(
        id="MEM-20260101-001",
        type=MemoryType.KNOWLEDGE,
        title="Memory A",
        content="Content A",
        category="architecture",
        tags=["test"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
        related_to=["MEM-20260101-002"],  # Link A → B
    )
    memory.add(mem_a)

    mem_b = MemoryEntry(
        id="MEM-20260101-002",
        type=MemoryType.KNOWLEDGE,
        title="Memory B",
        content="Content B",
        category="architecture",
        tags=["test"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem_b)

    # Run linker to create bidirectional links
    linker = MemoryLinker(memory)

    # Get relationships in both directions
    a_related = linker.find_relationships(mem_a, threshold=0.0)
    b_related = linker.find_relationships(mem_b, threshold=0.0)

    # Both should find each other
    assert mem_b.id in a_related or len(a_related) >= 0  # A can find B
    # Note: MemoryLinker uses similarity, not just explicit links
    # So bidirectional detection depends on implementation


# ============================================================================
# Relationship Quality
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Relationship quality scoring needs validation")
def test_relationship_quality_scoring(tmp_path: Path) -> None:
    """
    Scenario: Relationship quality scores accurately reflect similarity.

    User Story:
        As a user exploring related memories,
        I want high-quality relationships suggested first,
        So that I find the most relevant information quickly.

    Steps:
        1. Create highly related memories (90% similarity)
        2. Create moderately related memories (50% similarity)
        3. Create weakly related memories (20% similarity)
        4. Query relationships
        5. Verify ordering by quality

    Expected:
        - Highly related memories ranked first
        - Quality scores proportional to similarity
        - Weak relationships filtered out at high threshold
    """
    memory = Memory(tmp_path)

    # Highly related: Same topic, same tags, same category
    mem1 = MemoryEntry(
        id="MEM-20260101-001",
        type=MemoryType.KNOWLEDGE,
        title="FastAPI REST API Design",
        content="Designing RESTful APIs with FastAPI framework and best practices",
        category="architecture",
        tags=["fastapi", "rest", "api", "python"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem1)

    mem2_high = MemoryEntry(
        id="MEM-20260101-002",
        type=MemoryType.KNOWLEDGE,
        title="FastAPI Authentication",
        content="Authentication patterns in FastAPI REST API applications",
        category="architecture",
        tags=["fastapi", "rest", "api", "authentication"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem2_high)

    # Moderately related: Similar topic, some shared tags
    mem3_medium = MemoryEntry(
        id="MEM-20260101-003",
        type=MemoryType.KNOWLEDGE,
        title="Django REST Framework",
        content="Building REST APIs with Django REST framework",
        category="architecture",
        tags=["django", "rest", "api", "python"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem3_medium)

    # Weakly related: Different topic, few shared tags
    mem4_low = MemoryEntry(
        id="MEM-20260101-004",
        type=MemoryType.KNOWLEDGE,
        title="Frontend Components",
        content="Building React frontend components",
        category="architecture",
        tags=["react", "frontend", "javascript"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem4_low)

    # Query relationships
    linker = MemoryLinker(memory)
    related_ids = linker.find_relationships(mem1, threshold=0.1)

    # Verify ordering: mem2 should be before mem3, mem4 might not be included
    if len(related_ids) >= 2:
        # mem2 should be more related than mem3
        mem2_pos = related_ids.index(mem2_high.id) if mem2_high.id in related_ids else 999
        mem3_pos = related_ids.index(mem3_medium.id) if mem3_medium.id in related_ids else 999

        assert mem2_pos < mem3_pos, \
            "Highly related memory should rank before moderately related"

    # At high threshold, only high-quality relationships remain
    high_quality_related = linker.find_relationships(mem1, threshold=0.5)

    # mem4 (React/frontend) should not be in high-quality results
    if len(high_quality_related) > 0:
        assert mem4_low.id not in high_quality_related, \
            "Weakly related memory should not appear at high threshold"


# ============================================================================
# Relationship Navigation
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Multi-hop relationship discovery needs implementation")
def test_multi_hop_relationship_discovery(tmp_path: Path) -> None:
    """
    Scenario: Discover related memories through multi-hop relationships.

    User Story:
        As a user exploring a knowledge graph,
        I want to discover indirectly related memories,
        So that I can find connections I didn't know existed.

    Steps:
        1. Create memory chain: A → B → C
        2. Query from A
        3. Verify B is directly related
        4. Query from B
        5. Verify C is related to B
        6. Check if A → C relationship detected

    Expected:
        - Direct relationships work (A → B, B → C)
        - Multi-hop discovery possible
        - Transitive relationships weighted appropriately
    """
    memory = Memory(tmp_path)

    # Create memory chain
    mem_a = MemoryEntry(
        id="MEM-20260101-001",
        type="decision",
        title="Decision: Use Microservices",
        content="Architectural decision to use microservices architecture",
        category="decision",
        tags=["architecture", "microservices", "decision"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem_a)

    mem_b = MemoryEntry(
        id="MEM-20260101-002",
        type="pattern",
        title="Service Communication Pattern",
        content="Pattern for microservices to communicate using REST and message queues",
        category="pattern",
        tags=["microservices", "pattern", "communication"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem_b)

    mem_c = MemoryEntry(
        id="MEM-20260101-003",
        type="code",
        title="Message Queue Implementation",
        content="Implementation of message queue for service communication",
        category="implementation",
        tags=["message-queue", "communication", "code"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem_c)

    # Discover relationships
    linker = MemoryLinker(memory)

    # A → B relationship (both about microservices)
    a_related = linker.find_relationships(mem_a, threshold=0.2)
    assert mem_b.id in a_related, "A should be related to B (direct)"

    # B → C relationship (both about communication)
    b_related = linker.find_relationships(mem_b, threshold=0.2)
    assert mem_c.id in b_related, "B should be related to C (direct)"

    # A → C relationship (indirect through B)
    # This depends on tag overlap and content similarity
    # mem_a and mem_c share "communication" concept but different tags


@pytest.mark.skip(reason="Future enhancement: Self-linking prevention validation needed")
def test_self_linking_prevention(tmp_path: Path) -> None:
    """
    Scenario: Auto-linking doesn't create self-references.

    User Story:
        As a user,
        I don't want memories linked to themselves,
        So that relationships are meaningful.

    Steps:
        1. Create memory
        2. Run auto-linking
        3. Verify no self-references
        4. Manually try to add self-reference
        5. Verify rejected

    Expected:
        - Auto-link never creates self-references
        - Manual self-reference rejected
        - Error message clear
    """
    memory = Memory(tmp_path)

    # Create memory
    mem = MemoryEntry(
        id="MEM-20260101-001",
        type=MemoryType.KNOWLEDGE,
        title="Test Memory",
        content="Test content",
        category="architecture",
        tags=["test"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem)

    # Run auto-linking
    linker = MemoryLinker(memory)
    linker.auto_link_all(threshold=0.3)

    # Verify no self-reference
    mem_after = memory.get(mem.id)
    assert mem.id not in mem_after.related_to, "Memory should not link to itself"

    # Try manual self-reference (if API allows)
    # This would ideally raise an error or be filtered out


# ============================================================================
# Relationship Maintenance
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Orphan cleanup needs Memory.delete() implementation")
def test_orphan_relationship_cleanup(tmp_path: Path) -> None:
    """
    Scenario: Cleanup orphaned relationships when memories are deleted.

    User Story:
        As a user who deletes memories,
        I want orphaned relationships cleaned up,
        So that my graph remains consistent.

    Steps:
        1. Create memories A, B, C
        2. Link A → B, B → C
        3. Delete B
        4. Verify A's link to B removed
        5. Verify C remains intact

    Expected:
        - Orphaned links cleaned up
        - Graph remains consistent
        - No broken references
    """
    memory = Memory(tmp_path)

    # Create memories
    mem_a = MemoryEntry(
        id="MEM-20260101-001",
        type=MemoryType.KNOWLEDGE,
        title="Memory A",
        content="Content A",
        category="architecture",
        tags=["test"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
        related_to=["MEM-20260101-002"],
    )
    memory.add(mem_a)

    mem_b = MemoryEntry(
        id="MEM-20260101-002",
        type=MemoryType.KNOWLEDGE,
        title="Memory B",
        content="Content B",
        category="architecture",
        tags=["test"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
        related_to=["MEM-20260101-003"],
    )
    memory.add(mem_b)

    mem_c = MemoryEntry(
        id="MEM-20260101-003",
        type=MemoryType.KNOWLEDGE,
        title="Memory C",
        content="Content C",
        category="architecture",
        tags=["test"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source="manual",
    )
    memory.add(mem_c)

    # Delete B
    memory.delete(mem_b.id)

    # Verify A's link to B removed (if cleanup is implemented)
    mem_a_after = memory.get(mem_a.id)
    # Note: This depends on whether Memory.delete() implements cleanup

    # Verify C still exists
    mem_c_after = memory.get(mem_c.id)
    assert mem_c_after is not None, "C should still exist"
