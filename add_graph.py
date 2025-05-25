import json
import os
from typing import Dict, List
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from PyInquirer import prompt, Validator, ValidationError
import re

console = Console()
DATA_FILE = os.path.join(os.path.dirname(__file__), "_data", "graphs.json")


class UrlValidator(Validator):
    def validate(self, document):
        if not document.text.startswith("https://www.desmos.com/calculator/"):
            raise ValidationError(
                message="URL must be a Desmos calculator link",
                cursor_position=len(document.text),
            )


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
    table.add_column("Tags", style="cyan")
    table.add_column("Link", style="blue")

    for graph in graphs:
        table.add_row(
            graph["id"], graph["title"], ", ".join(graph["tags"]), graph["graphLink"]
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
    questions = [
        {
            "type": "input",
            "name": "title",
            "message": "Enter graph title:",
            "validate": lambda val: len(val) > 0 or "Title cannot be empty",
        },
        {
            "type": "input",
            "name": "description",
            "message": "Enter graph description:",
            "validate": lambda val: len(val) > 0 or "Description cannot be empty",
        },
        {
            "type": "input",
            "name": "graphLink",
            "message": "Enter Desmos graph link:",
            "validate": lambda val: val.startswith("https://www.desmos.com/calculator/")
            or "Must be a Desmos calculator link",
        },
        {
            "type": "input",
            "name": "tags",
            "message": "Enter tags (comma-separated):",
            "validate": lambda val: len(val) > 0 or "At least one tag is required",
        },
    ]

    answers = prompt(questions)
    if not answers:  # User cancelled
        return

    data = load_graphs()

    # Generate ID from title
    graph_id = re.sub(r"[^a-z0-9-]", "", answers["title"].lower().replace(" ", "-"))

    new_graph = {
        "id": graph_id,
        "title": answers["title"],
        "description": answers["description"],
        "graphLink": answers["graphLink"],
        "thumbnail": answers["graphLink"] + "/thumbnail",
        "tags": [tag.strip() for tag in answers["tags"].split(",")],
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
    choices = [
        {"name": f"{g['title']} ({g['id']})", "value": i}
        for i, g in enumerate(data["graphs"])
    ]
    selection = prompt(
        [
            {
                "type": "list",
                "name": "graph_index",
                "message": "Select a graph to edit:",
                "choices": choices,
            }
        ]
    )

    if not selection:  # User cancelled
        return

    graph_index = selection["graph_index"]
    graph = data["graphs"][graph_index]

    # Now prompt for edits
    questions = [
        {
            "type": "input",
            "name": "title",
            "message": "Enter new title (or press enter to keep current):",
            "default": graph["title"],
        },
        {
            "type": "input",
            "name": "description",
            "message": "Enter new description (or press enter to keep current):",
            "default": graph["description"],
        },
        {
            "type": "input",
            "name": "graphLink",
            "message": "Enter new Desmos graph link (or press enter to keep current):",
            "default": graph["graphLink"],
        },
        {
            "type": "input",
            "name": "tags",
            "message": "Enter new tags (comma-separated, or press enter to keep current):",
            "default": ",".join(graph["tags"]),
        },
    ]

    answers = prompt(questions)
    if not answers:  # User cancelled
        return

    # Update the graph
    graph["title"] = answers["title"]
    graph["description"] = answers["description"]
    graph["graphLink"] = answers["graphLink"]
    graph["thumbnail"] = answers["graphLink"] + "/thumbnail"
    graph["tags"] = [tag.strip() for tag in answers["tags"].split(",")]

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
    choices = [
        {"name": f"{g['title']} ({g['id']})", "value": i}
        for i, g in enumerate(data["graphs"])
    ]
    selection = prompt(
        [
            {
                "type": "list",
                "name": "graph_index",
                "message": "Select a graph to delete:",
                "choices": choices,
            },
            {
                "type": "confirm",
                "name": "confirm",
                "message": "Are you sure you want to delete this graph?",
                "default": False,
            },
        ]
    )

    if not selection or not selection["confirm"]:  # User cancelled or didn't confirm
        return

    graph_index = selection["graph_index"]
    deleted_graph = data["graphs"].pop(graph_index)
    save_graphs(data)
    console.print("[green]Graph deleted successfully![/green]")
    console.print("[dim]Deleted graph:[/dim]")
    display_graphs([deleted_graph])


if __name__ == "__main__":
    cli()
