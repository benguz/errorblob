"""Command line interface for errorblob."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .config import (
    ErrorBlobConfig,
    StorageMode,
    TeamMode,
    load_config,
    save_config,
    get_config_path,
    get_turbopuffer_api_key,
)
from .models import ErrorEntry
from .storage import LocalStorage, TurbopufferStorage
from .storage.base import StorageBackend

console = Console()


def get_storage(config: ErrorBlobConfig) -> StorageBackend:
    """Get the appropriate storage backend based on configuration."""
    if config.storage_mode == StorageMode.TURBOPUFFER:
        api_key = get_turbopuffer_api_key(config)
        if not api_key:
            console.print(
                "[red]Error:[/red] Turbopuffer API key not configured. "
                "Run [bold]errorblob config[/bold] or set TURBOPUFFER_API_KEY environment variable."
            )
            raise SystemExit(1)
        
        return TurbopufferStorage(
            api_key=api_key,
            namespace=config.turbopuffer_namespace,
            region=config.turbopuffer_region,
        )
    else:
        return LocalStorage(file_path=config.local_file_path)


@click.group()
@click.version_option()
def cli():
    """errorblob - Never block on the same bug twice.
    
    A lightning-fast error database for fast moving teams.
    Commit your errors and their fixes from the terminal.
    """
    pass


@cli.command()
@click.option("-e", "--error", required=True, help="The error message text")
@click.option("-m", "--message", required=True, help="Additional context or fix description")
@click.option("-t", "--tag", multiple=True, help="Optional tags (can be used multiple times)")
def commit(error: str, message: str, tag: tuple[str, ...]):
    """Save an error and its fix to the database.
    
    Example:
        errorblob commit -e "ModuleNotFoundError: No module named 'foo'" -m "Run pip install foo"
    """
    config = load_config()
    storage = get_storage(config)
    
    entry = ErrorEntry(
        error_text=error,
        message=message,
        author=config.author_name,
        tags=list(tag),
    )
    
    storage.commit(entry)
    
    console.print(Panel(
        f"[green]✓ Error committed![/green]\n\n"
        f"[bold]Error:[/bold] {error[:80]}{'...' if len(error) > 80 else ''}\n"
        f"[bold]Fix:[/bold] {message[:80]}{'...' if len(message) > 80 else ''}",
        title="errorblob",
        border_style="green",
    ))


@cli.command()
@click.argument("query")
@click.option("-n", "--limit", default=5, help="Maximum number of results to return")
def look(query: str, limit: int):
    """Search for an error in the database.
    
    Example:
        errorblob look "ModuleNotFoundError"
    """
    config = load_config()
    storage = get_storage(config)
    
    results = storage.search(query, limit=limit)
    
    if not results:
        console.print(Panel(
            f"[yellow]No matches found for:[/yellow] {query}\n\n"
            "Try a different search term or commit this error when you find the fix!",
            title="errorblob",
            border_style="yellow",
        ))
        return
    
    console.print(f"\n[bold]Found {len(results)} result(s) for:[/bold] {query}\n")
    
    for i, result in enumerate(results, 1):
        entry = result.entry
        score_display = f" [dim](score: {result.score:.2f})[/dim]" if result.score > 0 else ""
        
        panel_content = (
            f"[red bold]Error:[/red bold] {entry.error_text}\n\n"
            f"[green bold]Fix:[/green bold] {entry.message}\n\n"
            f"[dim]Added: {entry.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        
        if entry.author:
            panel_content += f" by {entry.author}"
        
        if entry.tags:
            panel_content += f"\nTags: {', '.join(entry.tags)}"
        
        panel_content += "[/dim]"
        
        console.print(Panel(
            panel_content,
            title=f"Result #{i}{score_display}",
            border_style="blue",
        ))


@cli.command()
def config():
    """Configure errorblob settings interactively."""
    console.print(Panel(
        "[bold]Welcome to errorblob configuration![/bold]\n\n"
        "Let's set up your error database.",
        title="errorblob config",
        border_style="cyan",
    ))
    
    current_config = load_config()
    
    # Choose storage mode
    console.print("\n[bold]Storage Options:[/bold]")
    console.print("  1. [green]local[/green] - Store errors in a local JSON file (free, no account needed)")
    console.print("  2. [blue]turbopuffer[/blue] - Store in Turbopuffer cloud (semantic search, team sharing)")
    
    mode_choice = Prompt.ask(
        "\nChoose storage mode",
        choices=["1", "2", "local", "turbopuffer"],
        default="1" if current_config.storage_mode == StorageMode.LOCAL else "2",
    )
    
    if mode_choice in ["1", "local"]:
        storage_mode = StorageMode.LOCAL
    else:
        storage_mode = StorageMode.TURBOPUFFER
    
    new_config = ErrorBlobConfig(storage_mode=storage_mode)
    
    if storage_mode == StorageMode.LOCAL:
        # Configure local storage
        default_path = str(current_config.local_file_path)
        file_path = Prompt.ask(
            "Local file path",
            default=default_path,
        )
        new_config.local_file_path = Path(file_path)
        
        # Team mode for local
        console.print("\n[bold]Team Sharing (Local Mode):[/bold]")
        console.print("  Store your errors file in a git repo to share with your team!")
        
        use_git = Confirm.ask("Is this file in a shared git repository?", default=False)
        if use_git:
            new_config.team_mode = TeamMode.GIT
    else:
        # Configure Turbopuffer
        api_key = Prompt.ask(
            "Turbopuffer API key (from https://turbopuffer.com/dashboard)",
            default=current_config.turbopuffer_api_key or "",
            password=True,
        )
        new_config.turbopuffer_api_key = api_key if api_key else None
        
        namespace = Prompt.ask(
            "Namespace name",
            default=current_config.turbopuffer_namespace,
        )
        new_config.turbopuffer_namespace = namespace
        
        region = Prompt.ask(
            "Region",
            default=current_config.turbopuffer_region,
        )
        new_config.turbopuffer_region = region
        
        # Team mode for Turbopuffer
        console.print("\n[bold]Team Sharing (Turbopuffer Mode):[/bold]")
        console.print("  Share the same namespace with your team for shared error knowledge!")
        
        use_shared = Confirm.ask("Is this a shared team namespace?", default=False)
        if use_shared:
            new_config.team_mode = TeamMode.SHARED_NAMESPACE
            team_name = Prompt.ask("Team name (optional)", default="")
            if team_name:
                new_config.team_name = team_name
    
    # Author name
    author = Prompt.ask(
        "\nYour name (for attributing commits)",
        default=current_config.author_name or "",
    )
    new_config.author_name = author if author else None
    
    # Save configuration
    save_config(new_config)
    
    console.print(Panel(
        f"[green]✓ Configuration saved![/green]\n\n"
        f"[bold]Mode:[/bold] {new_config.storage_mode.value}\n"
        f"[bold]Config file:[/bold] {get_config_path()}",
        title="errorblob",
        border_style="green",
    ))


@cli.command(name="list")
@click.option("-n", "--limit", default=20, help="Maximum number of entries to show")
def list_errors(limit: int):
    """List all stored errors."""
    config = load_config()
    storage = get_storage(config)
    
    entries = storage.get_all()
    
    if not entries:
        console.print(Panel(
            "[yellow]No errors stored yet.[/yellow]\n\n"
            "Use [bold]errorblob commit[/bold] to add your first error!",
            title="errorblob",
            border_style="yellow",
        ))
        return
    
    table = Table(title=f"Stored Errors ({len(entries)} total)")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Error", style="red", max_width=40)
    table.add_column("Fix", style="green", max_width=40)
    table.add_column("Date", style="dim")
    
    for entry in entries[:limit]:
        table.add_row(
            entry.id[:8],
            entry.error_text[:40] + ("..." if len(entry.error_text) > 40 else ""),
            entry.message[:40] + ("..." if len(entry.message) > 40 else ""),
            entry.created_at.strftime("%Y-%m-%d"),
        )
    
    console.print(table)
    
    if len(entries) > limit:
        console.print(f"\n[dim]Showing {limit} of {len(entries)} entries. Use -n to show more.[/dim]")


@cli.command()
def status():
    """Show current configuration and database status."""
    config = load_config()
    
    console.print(Panel(
        f"[bold]Storage Mode:[/bold] {config.storage_mode.value}\n"
        f"[bold]Team Mode:[/bold] {config.team_mode.value}\n"
        f"[bold]Author:[/bold] {config.author_name or '(not set)'}\n"
        f"[bold]Config File:[/bold] {get_config_path()}",
        title="errorblob status",
        border_style="cyan",
    ))
    
    if config.storage_mode == StorageMode.LOCAL:
        console.print(f"\n[bold]Local File:[/bold] {config.local_file_path}")
        if config.local_file_path.exists():
            storage = LocalStorage(file_path=config.local_file_path)
            count = storage.count()
            console.print(f"[bold]Errors Stored:[/bold] {count}")
        else:
            console.print("[yellow]Database file not yet created.[/yellow]")
    else:
        console.print(f"\n[bold]Turbopuffer Namespace:[/bold] {config.turbopuffer_namespace}")
        console.print(f"[bold]Turbopuffer Region:[/bold] {config.turbopuffer_region}")
        
        api_key = get_turbopuffer_api_key(config)
        if api_key:
            console.print("[green]API Key:[/green] ✓ configured")
            try:
                storage = get_storage(config)
                count = storage.count()
                console.print(f"[bold]Errors Stored:[/bold] {count}")
            except Exception as e:
                console.print(f"[red]Error connecting:[/red] {e}")
        else:
            console.print("[yellow]API Key:[/yellow] not configured")


@cli.command()
@click.argument("error_id")
def delete(error_id: str):
    """Delete an error by ID."""
    config = load_config()
    storage = get_storage(config)
    
    if storage.delete(error_id):
        console.print(f"[green]✓ Deleted error {error_id}[/green]")
    else:
        console.print(f"[red]Error not found: {error_id}[/red]")


if __name__ == "__main__":
    cli()

