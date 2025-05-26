#!/usr/bin/env python3
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

def load_tags() -> Dict:
    """Load tags from the JSON file."""
    tags_file = os.path.join(os.path.dirname(__file__), '_data', 'tags.json')
    try:
        with open(tags_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"tags": []}

def save_tags(data: Dict) -> None:
    """Save tags to the JSON file."""
    tags_file = os.path.join(os.path.dirname(__file__), '_data', 'tags.json')
    with open(tags_file, 'w') as f:
        json.dump(data, f, indent=2)

def update_tag_counts() -> None:
    """Update the count of each tag based on graph usage."""
    graphs_data = load_graphs()
    tags_data = load_tags()
    
    # Reset all counts to 0
    for tag in tags_data['tags']:
        tag['count'] = 0
    
    # Count tag usage
    tag_counts = {}
    for graph in graphs_data['graphs']:
        for tag in graph['tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Update existing tags and add new ones
    existing_tags = {tag['name'] for tag in tags_data['tags']}
    for tag_name, count in tag_counts.items():
        if tag_name in existing_tags:
            for tag in tags_data['tags']:
                if tag['name'] == tag_name:
                    tag['count'] = count
                    break
        else:
            tags_data['tags'].append({
                'name': tag_name,
                'description': '',  # Empty description for new tags
                'count': count
            })
    
    save_tags(tags_data)

def validate_tags(tags_list: List[str]) -> bool:
    """Validate that required tags are included and update tag counts."""
    required_tags = {'graphs', 'geometry', '3d'}
    tag_types = set(tag.strip() for tag in tags_list)
    
    # Check if the graph uses any of the required tag types
    has_required = any(tag in required_tags for tag in tag_types)
    
    if not has_required:
        raise ValueError('Must include at least one of these tags: graphs, geometry, or 3d')
    
    return True

def validate_url(text: str) -> bool:
    """Validate that the URL is a Desmos calculator link."""
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
    """Save graphs to the JSON file and update tag counts."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    update_tag_counts()

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
    console.print(Panel.fit("[bold blue]Desmos Graphs[/bold blue]"))
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
        "Enter author name (Anonymous):",
        validate=lambda text: len(text) > 0,
        default="Anonymous",
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

    # Validate and process tags
    tag_list = [tag.strip() for tag in tags.split(",")]
    try:
        validate_tags(tag_list)
    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
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
        "tags": tag_list,
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

    # Validate and process tags
    tag_list = [tag.strip() for tag in tags.split(",")]
    try:
        validate_tags(tag_list)
    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return

    # Update the graph
    graph["title"] = title
    graph["author"] = author
    graph["description"] = description
    graph["graphLink"] = graph_link
    graph["thumbnail"] = graph_link + "/thumbnail"
    graph["tags"] = tag_list

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
