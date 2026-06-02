# Desmos Graphs Collection

A Jekyll-based website to showcase and manage your Desmos graph collection. Features a modern, responsive interface with dynamic graph loading and a powerful CLI management tool.

## 🌐 Website Features

- Dynamic graph browser with search and tag filtering
- Responsive design using Bootstrap 5
- Non-interactive Desmos graph previews
- Multi-select tag filtering system with descriptions
- Fast and efficient loading

## 🛠️ CLI Tool Usage

The project includes a powerful CLI tool (`cli.py`) for managing your graph collection.

### Prerequisites

```bash
pip install -r requirements.txt
```

### Commands

1. **List all graphs**
   ```bash
   python cli.py list
   ```
   Displays all graphs in a nicely formatted table.

2. **Add a new graph**
   ```bash
   python cli.py add
   ```   Interactive prompt to add a new graph with:
   - Title
   - Author
   - Description
   - Desmos graph link
   - Tags (comma-separated)
   
   Note: Graphs must include at least one of these tags: graphs, geometry, or 3d

3. **Edit a graph**
   ```bash
   python cli.py edit
   ```
   Select and edit any existing graph's properties.

4. **Delete a graph**
   ```bash
   python cli.py delete
   ```
   Select and delete a graph with confirmation.

### CLI Features

- 🎨 Colorful interface
- ✔️ Input validation
- 🏷️ Easy tag management
- 🔒 Safe deletion with confirmation
- 📝 Automatic ID generation
- 🖼️ Automatic thumbnail URLs

## 🚀 Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your graphs using the CLI:
   ```bash
   python cli.py add
   ```
4. Start the Jekyll server:
   ```bash
   bundle exec jekyll serve
   ```

## 📁 Project Structure

```
.
├── _config.yml        # Jekyll configuration
├── _data/
│   └── graphs.json    # Graph collection data
├── _layouts/
│   ├── default.html   # Main layout template
│   └── graph.html     # Individual graph layout
├── cli.py            # CLI management tool
├── graphs.html       # Graph browser page
└── index.html        # Homepage
```

## 💻 Development

The site uses:
- Jekyll for static site generation
- Bootstrap 5 for styling
- Desmos Calculator API for graph embedding
- Python with Click and Rich for CLI

## 🔄 Updating Content

1. Use the CLI tool to manage graphs
2. Jekyll will automatically use the updated data
3. Commit and push changes to deploy

## 📝 Graph Data Format

Each graph in `_data/graphs.json` follows this structure:

```json
{
  "id": "unique-id",
  "title": "Graph Title",
  "description": "Graph description",
  "graphLink": "https://www.desmos.com/calculator/...",
  "thumbnail": "https://www.desmos.com/calculator/.../thumbnail",
  "tags": ["tag1", "tag2"]
}
```

