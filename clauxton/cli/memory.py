"""CLI commands for unified Memory management (v0.15.0)."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from clauxton.core.memory import Memory


@click.group()
def memory() -> None:
    """Memory management commands."""
    pass


@memory.command("add")
@click.option(
    "--type",
    "entry_type",
    type=click.Choice(["knowledge", "decision", "code", "task", "pattern"]),
    help="Memory type",
)
@click.option("--title", help="Memory title")
@click.option("--content", help="Memory content")
@click.option("--category", help="Category")
@click.option("--tags", help="Comma-separated tags")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
def add(
    entry_type: Optional[str],
    title: Optional[str],
    content: Optional[str],
    category: Optional[str],
    tags: Optional[str],
    interactive: bool,
) -> None:
    """
    Add memory entry.

    Examples:
        clauxton memory add -i                    # Interactive
        clauxton memory add --type knowledge --title "API Design" \\
            --content "Use RESTful API" --category architecture
    """
    from clauxton.core.memory import MemoryEntry

    project_root = Path.cwd()

    # Check if .clauxton exists
    if not (project_root / ".clauxton").exists():
        click.echo(click.style("⚠ .clauxton/ not found. Run 'clauxton init' first", fg="red"))
        raise click.Abort()

    mem = Memory(project_root)

    if interactive:
        # Interactive mode with guided prompts
        click.echo(click.style("\nAdd Memory Entry (Interactive Mode)\n", fg="cyan", bold=True))

        entry_type = click.prompt(
            "Memory type",
            type=click.Choice(["knowledge", "decision", "code", "task", "pattern"]),
        )
        title = click.prompt("Title")

        click.echo("\nContent (multi-line, press Ctrl+D when done):")
        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass
        content = "\n".join(content_lines).strip()

        if not content:
            click.echo(click.style("Error: Content cannot be empty", fg="red"))
            raise click.Abort()

        category = click.prompt("Category")
        tags_str = click.prompt("Tags (comma-separated)", default="")
        tags_list = [t.strip() for t in tags_str.split(",") if t.strip()]
    else:
        if not all([entry_type, title, content, category]):
            click.echo(
                click.style(
                    "Missing required fields. Use --interactive or provide all options.",
                    fg="red",
                )
            )
            click.echo("\nRequired: --type, --title, --content, --category")
            click.echo("Optional: --tags")
            raise click.Abort()
        tags_list = [t.strip() for t in (tags or "").split(",") if t.strip()]

    # Generate memory ID
    memory_id = mem._generate_memory_id()

    now = datetime.now()
    entry = MemoryEntry(
        id=memory_id,
        type=entry_type,  # type: ignore[arg-type]
        title=title,  # type: ignore[arg-type]
        content=content,  # type: ignore[arg-type]
        category=category,  # type: ignore[arg-type]
        tags=tags_list,
        created_at=now,
        updated_at=now,
        source="manual",
        confidence=1.0,
    )

    try:
        result_id = mem.add(entry)
        click.echo(click.style(f"\n✓ Memory added: {result_id}", fg="green"))
        click.echo(f"  Type: {entry_type}")
        click.echo(f"  Title: {title}")
        click.echo(f"  Category: {category}")
        if tags_list:
            click.echo(f"  Tags: {', '.join(tags_list)}")
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@memory.command("search")
@click.argument("query")
@click.option(
    "--type",
    "type_filter",
    multiple=True,
    type=click.Choice(["knowledge", "decision", "code", "task", "pattern"]),
    help="Filter by type (can be used multiple times)",
)
@click.option("--limit", default=10, help="Maximum results")
def search(query: str, type_filter: tuple[str, ...], limit: int) -> None:
    """
    Search memories.

    Examples:
        clauxton memory search "authentication"
        clauxton memory search "API" --type knowledge --type decision
    """
    project_root = Path.cwd()

    # Check if .clauxton exists
    if not (project_root / ".clauxton").exists():
        click.echo(click.style("⚠ .clauxton/ not found. Run 'clauxton init' first", fg="red"))
        raise click.Abort()

    mem = Memory(project_root)

    results = mem.search(query, type_filter=list(type_filter) or None, limit=limit)

    if not results:
        click.echo(click.style("\nNo memories found", fg="yellow"))
        return

    click.echo(click.style(f"\nSearch Results: '{query}'", fg="cyan", bold=True))
    click.echo(click.style(f"Found {len(results)} matches\n", fg="white"))

    for entry in results:
        click.echo(click.style(f"  {entry.id}", fg="cyan"))
        click.echo(f"    Type: {entry.type}")
        click.echo(f"    Title: {entry.title}")
        click.echo(f"    Category: {entry.category}")
        if entry.tags:
            click.echo(f"    Tags: {', '.join(entry.tags)}")
        click.echo()


@memory.command("list")
@click.option(
    "--type",
    "type_filter",
    multiple=True,
    type=click.Choice(["knowledge", "decision", "code", "task", "pattern"]),
    help="Filter by type",
)
@click.option("--category", help="Filter by category")
@click.option("--tag", "tag_filter", multiple=True, help="Filter by tags")
def list_memories(
    type_filter: tuple[str, ...], category: Optional[str], tag_filter: tuple[str, ...]
) -> None:
    """
    List all memories.

    Examples:
        clauxton memory list
        clauxton memory list --type knowledge
        clauxton memory list --category architecture
        clauxton memory list --tag api --tag rest
    """
    project_root = Path.cwd()

    # Check if .clauxton exists
    if not (project_root / ".clauxton").exists():
        click.echo(click.style("⚠ .clauxton/ not found. Run 'clauxton init' first", fg="red"))
        raise click.Abort()

    mem = Memory(project_root)

    memories = mem.list_all(
        type_filter=list(type_filter) or None,
        category_filter=category,
        tag_filter=list(tag_filter) or None,
    )

    if not memories:
        click.echo(click.style("\nNo memories found", fg="yellow"))
        return

    click.echo(click.style(f"\nMemories ({len(memories)}):\n", bold=True))

    for entry in memories:
        click.echo(click.style(f"  {entry.id}", fg="cyan"))
        click.echo(f"    Type: {entry.type}")
        title_display = entry.title[:50] + "..." if len(entry.title) > 50 else entry.title
        click.echo(f"    Title: {title_display}")
        click.echo(f"    Category: {entry.category}")
        if entry.tags:
            tags_display = ", ".join(entry.tags[:3])
            if len(entry.tags) > 3:
                tags_display += f" (+{len(entry.tags) - 3} more)"
            click.echo(f"    Tags: {tags_display}")
        click.echo()


@memory.command("get")
@click.argument("memory_id")
def get(memory_id: str) -> None:
    """
    Get memory details.

    Example:
        clauxton memory get MEM-20260127-001
    """
    project_root = Path.cwd()

    # Check if .clauxton exists
    if not (project_root / ".clauxton").exists():
        click.echo(click.style("⚠ .clauxton/ not found. Run 'clauxton init' first", fg="red"))
        raise click.Abort()

    mem = Memory(project_root)

    entry = mem.get(memory_id)

    if not entry:
        click.echo(click.style(f"\nMemory not found: {memory_id}", fg="red"))
        raise click.Abort()

    click.echo(click.style(f"\n{entry.id}", fg="cyan", bold=True))
    click.echo(f"Type: {entry.type}")
    click.echo(f"Title: {entry.title}")
    click.echo(f"Category: {entry.category}")

    if entry.tags:
        click.echo(f"Tags: {', '.join(entry.tags)}")

    click.echo(f"Created: {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Source: {entry.source}")

    if entry.confidence < 1.0:
        click.echo(f"Confidence: {entry.confidence:.2f}")

    click.echo(click.style("\nContent:", bold=True))
    click.echo(entry.content)

    if entry.related_to:
        click.echo(click.style("\nRelated:", bold=True))
        click.echo(", ".join(entry.related_to))

    if entry.supersedes:
        click.echo(click.style(f"\nSupersedes: {entry.supersedes}", fg="yellow"))

    if entry.source_ref:
        click.echo(f"Source ref: {entry.source_ref}")

    if entry.legacy_id:
        click.echo(f"Legacy ID: {entry.legacy_id}")

    click.echo()


@memory.command("update")
@click.argument("memory_id")
@click.option("--title", help="New title")
@click.option("--content", help="New content")
@click.option("--category", help="New category")
@click.option("--tags", help="New tags (comma-separated)")
def update(
    memory_id: str,
    title: Optional[str],
    content: Optional[str],
    category: Optional[str],
    tags: Optional[str],
) -> None:
    """
    Update memory.

    Example:
        clauxton memory update MEM-20260127-001 --title "New Title"
        clauxton memory update MEM-20260127-001 --tags "api,rest,v2"
    """
    project_root = Path.cwd()

    # Check if .clauxton exists
    if not (project_root / ".clauxton").exists():
        click.echo(click.style("⚠ .clauxton/ not found. Run 'clauxton init' first", fg="red"))
        raise click.Abort()

    mem = Memory(project_root)

    # Build kwargs
    kwargs: dict[str, str | list[str]] = {}
    if title:
        kwargs["title"] = title
    if content:
        kwargs["content"] = content
    if category:
        kwargs["category"] = category
    if tags:
        kwargs["tags"] = [t.strip() for t in tags.split(",")]

    if not kwargs:
        click.echo(click.style("No fields to update", fg="yellow"))
        return

    try:
        success = mem.update(memory_id, **kwargs)

        if success:
            click.echo(click.style(f"\n✓ Memory updated: {memory_id}", fg="green"))
            for key, value in kwargs.items():
                if key == "tags":
                    click.echo(f"  {key}: {', '.join(value)}")  # type: ignore[arg-type]
                else:
                    display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    click.echo(f"  {key}: {display_value}")
        else:
            click.echo(click.style(f"\nMemory not found: {memory_id}", fg="red"))
            raise click.Abort()

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@memory.command("delete")
@click.argument("memory_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete(memory_id: str, yes: bool) -> None:
    """
    Delete memory.

    Example:
        clauxton memory delete MEM-20260127-001
        clauxton memory delete MEM-20260127-001 --yes
    """
    project_root = Path.cwd()

    # Check if .clauxton exists
    if not (project_root / ".clauxton").exists():
        click.echo(click.style("⚠ .clauxton/ not found. Run 'clauxton init' first", fg="red"))
        raise click.Abort()

    mem = Memory(project_root)

    # Get entry to show details before deletion
    entry = mem.get(memory_id)
    if not entry:
        click.echo(click.style(f"\nMemory not found: {memory_id}", fg="red"))
        raise click.Abort()

    if not yes:
        click.echo(f"\nDelete memory: {entry.title} ({memory_id})?")
        click.echo(f"Type: {entry.type}")
        click.echo(f"Category: {entry.category}")
        if not click.confirm("\nAre you sure?"):
            click.echo("Cancelled")
            return

    success = mem.delete(memory_id)

    if success:
        click.echo(click.style(f"\n✓ Memory deleted: {memory_id}", fg="green"))
    else:
        click.echo(click.style(f"\nMemory not found: {memory_id}", fg="red"))
        raise click.Abort()


@memory.command("related")
@click.argument("memory_id")
@click.option("--limit", default=5, help="Maximum results")
def related(memory_id: str, limit: int) -> None:
    """
    Find related memories.

    Example:
        clauxton memory related MEM-20260127-001
        clauxton memory related MEM-20260127-001 --limit 10
    """
    project_root = Path.cwd()

    # Check if .clauxton exists
    if not (project_root / ".clauxton").exists():
        click.echo(click.style("⚠ .clauxton/ not found. Run 'clauxton init' first", fg="red"))
        raise click.Abort()

    mem = Memory(project_root)

    # Check if memory exists
    entry = mem.get(memory_id)
    if not entry:
        click.echo(click.style(f"\nMemory not found: {memory_id}", fg="red"))
        raise click.Abort()

    related_entries = mem.find_related(memory_id, limit=limit)

    if not related_entries:
        click.echo(click.style(f"\nNo related memories found for {memory_id}", fg="yellow"))
        return

    click.echo(click.style(f"\nRelated to {memory_id}:", fg="cyan", bold=True))
    click.echo(f"'{entry.title}'")
    click.echo(click.style(f"\nFound {len(related_entries)} related memories:\n", fg="white"))

    for related_entry in related_entries:
        click.echo(click.style(f"  {related_entry.id}", fg="cyan"))
        click.echo(f"    Type: {related_entry.type}")
        title_display = (
            related_entry.title[:50] + "..."
            if len(related_entry.title) > 50
            else related_entry.title
        )
        click.echo(f"    Title: {title_display}")
        click.echo(f"    Category: {related_entry.category}")

        # Show reason for relation
        reasons = []
        if memory_id in related_entry.related_to or related_entry.id in entry.related_to:
            reasons.append("explicit link")
        shared_tags = set(entry.tags) & set(related_entry.tags)
        if shared_tags:
            reasons.append(f"shared tags: {', '.join(list(shared_tags)[:2])}")
        if entry.category == related_entry.category:
            reasons.append("same category")

        if reasons:
            click.echo(click.style(f"    Relation: {', '.join(reasons)}", fg="yellow"))

        click.echo()
