import json
import os
from typing import Dict, List
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import questionary
import re

console = Console()
DATA_FILE = os.path.join(os.path.dirname(__file__), "_data", "graphs.json")


def validate_url(text: str) -> bool:
    if not text.startswith("https://www.desmos.com/calculator/"):
        raise ValueError("URL must be a Desmos calculator link")
    return True


def load_graphs() -> Dict:
    """Load graphs from the JSON file."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"graphs": []}


def save_graphs(data: Dict) -> None:
    """Save graphs to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def display_graphs(graphs: List[Dict]) -> None:
    """Display graphs in a rich table."""
    if not graphs:
        console.print("[yellow]No graphs found![/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Author", style="yellow")
    table.add_column("Description", style="green")
    table.add_column("Tags", style="cyan")
    table.add_column("Link", style="blue")

    for graph in graphs:
        table.add_row(
            graph["id"],
            graph["title"],
            graph.get("author", "Anonymous"),
            (
                graph["description"][:50] + "..."
                if len(graph["description"]) > 50
                else graph["description"]
            ),
            ", ".join(graph["tags"]),
            graph["graphLink"],
        )

    console.print(table)


@click.group()
def cli():
    """Desmos Graphs Manager - A tool to manage your Desmos graphs collection."""
    pass


@cli.command()
def list():
    """List all graphs"""
    data = load_graphs()
    console.print(Panel.fit("[bold blue]Your Desmos Graphs[/bold blue]"))
    display_graphs(data["graphs"])


@cli.command()
def add():
    """Add a new graph"""
    # Get graph details using questionary
    title = questionary.text(
        "Enter graph title:", validate=lambda text: len(text) > 0
    ).ask()
    if not title:  # User cancelled
        return

    author = questionary.text(
        "Enter author name:", validate=lambda text: len(text) > 0
    ).ask()
    if not author:
        return

    description = questionary.text(
        "Enter graph description:", validate=lambda text: len(text) > 0
    ).ask()
    if not description:
        return

    graph_link = questionary.text(
        "Enter Desmos graph link:", validate=validate_url
    ).ask()
    if not graph_link:
        return

    tags = questionary.text(
        "Enter tags (comma-separated):", validate=lambda text: len(text) > 0
    ).ask()
    if not tags:
        return

    data = load_graphs()

    # Generate ID from title
    graph_id = re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))

    new_graph = {
        "id": graph_id,
        "title": title,
        "author": author,
        "description": description,
        "graphLink": graph_link,
        "thumbnail": graph_link + "/thumbnail",
        "tags": [tag.strip() for tag in tags.split(",")],
    }

    data["graphs"].append(new_graph)
    save_graphs(data)
    console.print("[green]Graph added successfully![/green]")
    display_graphs([new_graph])


@cli.command()
def edit():
    """Edit an existing graph"""
    data = load_graphs()
    if not data["graphs"]:
        console.print("[yellow]No graphs to edit![/yellow]")
        return

    # First, select a graph to edit
    choices = [f"{g['title']} ({g['id']})" for g in data["graphs"]]
    graph_choice = questionary.select("Select a graph to edit:", choices=choices).ask()
    if not graph_choice:  # User cancelled
        return

    # Find the selected graph
    graph_index = choices.index(graph_choice)
    graph = data["graphs"][graph_index]

    # Now prompt for edits
    title = questionary.text("Enter new title:", default=graph["title"]).ask()
    if title is None:  # User cancelled
        return

    author = questionary.text(
        "Enter new author:", default=graph.get("author", "Anonymous")
    ).ask()
    if author is None:
        return

    description = questionary.text(
        "Enter new description:", default=graph["description"]
    ).ask()
    if description is None:
        return

    graph_link = questionary.text(
        "Enter new Desmos graph link:",
        default=graph["graphLink"],
        validate=validate_url,
    ).ask()
    if graph_link is None:
        return

    tags = questionary.text(
        "Enter new tags (comma-separated):", default=",".join(graph["tags"])
    ).ask()
    if tags is None:
        return

    # Update the graph
    graph["title"] = title
    graph["author"] = author
    graph["description"] = description
    graph["graphLink"] = graph_link
    graph["thumbnail"] = graph_link + "/thumbnail"
    graph["tags"] = [tag.strip() for tag in tags.split(",")]

    save_graphs(data)
    console.print("[green]Graph updated successfully![/green]")
    display_graphs([graph])


@cli.command()
def delete():
    """Delete a graph"""
    data = load_graphs()
    if not data["graphs"]:
        console.print("[yellow]No graphs to delete![/yellow]")
        return

    # Select a graph to delete
    choices = [f"{g['title']} ({g['id']})" for g in data["graphs"]]
    graph_choice = questionary.select(
        "Select a graph to delete:", choices=choices
    ).ask()
    if not graph_choice:  # User cancelled
        return

    # Confirm deletion
    confirm = questionary.confirm(
        "Are you sure you want to delete this graph?", default=False
    ).ask()
    if not confirm:
        return

    # Find and delete the graph
    graph_index = choices.index(graph_choice)
    deleted_graph = data["graphs"].pop(graph_index)
    save_graphs(data)
    console.print("[green]Graph deleted successfully![/green]")
    console.print("[dim]Deleted graph:[/dim]")
    display_graphs([deleted_graph])


if __name__ == "__main__":
    cli()
