# errorblob 🐛

**Never block on the same bug twice** - a lightning-fast error database for fast moving teams.

Commit your errors and their fixes from the terminal and check the database when you're stuck, or have Claude do it all for you.

## Installation

```bash
pip install -e .
```

## Quick Start

### 1. Configure errorblob

```bash
errorblob config
```

Choose between:
- **Local mode** (free) - Store errors in a JSON file on your machine
- **Turbopuffer mode** - Cloud-based semantic search with team sharing

### 2. Commit an error when you solve it

```bash
errorblob commit -e "ModuleNotFoundError: No module named 'pandas'" -m "Run: pip install pandas"
```

### 3. Look up errors when you're stuck

```bash
errorblob look "ModuleNotFoundError pandas"
```

## Commands

| Command | Description |
|---------|-------------|
| `errorblob config` | Interactive configuration setup |
| `errorblob commit -e "error" -m "fix"` | Save an error and its fix |
| `errorblob look "query"` | Search for matching errors |
| `errorblob list` | List all stored errors |
| `errorblob status` | Show current configuration |
| `errorblob delete <id>` | Delete an error by ID |

## Options

### commit
- `-e, --error` - The error message text (required)
- `-m, --message` - The fix or additional context (required)
- `-t, --tag` - Optional tags (can be used multiple times)

### look
- `-n, --limit` - Maximum number of results (default: 5)

## Storage Modes

### Local Mode (Free)
Stores errors in a JSON file at `~/.errorblob/errors.json` (configurable).

**Team sharing:** Put the file in a shared git repository!

```bash
# In your team's shared repo
errorblob config
# Set path to: /path/to/team-repo/.errorblob/errors.json
```

### Turbopuffer Mode (Cloud)
Uses [Turbopuffer](https://turbopuffer.com) for cloud-based storage with BM25 full-text search.

1. Get an API key from https://turbopuffer.com/dashboard
2. Run `errorblob config` and select Turbopuffer mode
3. Enter your API key and namespace

**Team sharing:** Use the same namespace across your team!

## Environment Variables

- `TURBOPUFFER_API_KEY` - Turbopuffer API key (alternative to config file)

## Example Workflow

```bash
# You encounter an error
$ python myapp.py
Traceback (most recent call last):
  ...
TypeError: 'NoneType' object is not subscriptable

# Check if someone on your team has seen it
$ errorblob look "NoneType object is not subscriptable"

# Found it! The fix shows you need to add a null check.

# Later, you solve a new error - commit it for the team
$ errorblob commit \
  -e "ConnectionRefusedError: [Errno 111] Connection refused" \
  -m "The database wasn't running. Start it with: docker-compose up -d db" \
  -t docker -t database
```

## Claude Integration

errorblob is designed to work seamlessly with AI assistants. Claude can:

1. **Check errorblob** when you encounter an error
2. **Commit solutions** after helping you fix something

Example prompt:
> "I got this error: [paste error]. Can you check errorblob for a fix?"

## License

MIT

