# BFF: Box For File

A robust Command Line Interface (CLI) tool designed for efficient file management, indexing, and deduplication.

## Features

- **Initialize**: Set up a new repository for file tracking.
- **Index**: Catalog files with flexible filtering options (extension, size, date).
- **Stats**: View detailed statistics about your file repository, including duplication rates and potential storage savings.
- **Clean**: Identify and deduplicate files to save space (supports deletion or symlinking).
- **Check**: Verify the integrity of your index against the filesystem, detecting missing or corrupted files.
- **Reset**: Safely clear the database when needed.

## Installation

You can install `bff` directly from the source.

### Standard Installation

```bash
pip install .
```

### Development Installation

For contributors who want to run tests or modify the code:

```bash
pip install -e ".[dev]"
```

## Usage

After installation, the `bff` command will be available in your terminal.

### 1. Initialization

Start by initializing a BFF repository in your project root.

```bash
bff init
```

### 2. Indexing Files

Index your files to start tracking them. You can filter by extension, size, or modification date.

```bash
# Index everything
bff index

# Index only .pdf files larger than 1MB
bff index --ext .pdf --min-size 1048576

# Index files created after a specific date
bff index --after 2023-01-01
```

### 3. Deduplication

Save disk space by identifying duplicate files. You can either delete duplicates or replace them with symlinks.

```bash
# Delete duplicates (keeps one master copy)
bff clean

# Replace duplicates with symlinks (saves space, keeps file accessible)
bff clean --link
```

### 4. Monitoring & Integrity

Keep track of your repository's health.

```bash
# View storage statistics
bff stats

# Verify index integrity (detect corruption or missing files)
bff check

# Remove missing files from the index
bff check --prune
```

## Development

This project uses modern Python tooling:

- **Build**: `setuptools` (via `pyproject.toml`)
- **Testing**: `pytest`
- **Linting**: `ruff`
- **Formatting**: `black`
- **Type Checking**: `mypy`

Run the full suite of checks with:

```bash
ruff check . && black . && mypy src && pytest
```

## Project Structure

```
src/bff/
├── commands/       # CLI command implementations
│   ├── check.py
│   ├── clean.py
│   ├── index.py
│   ├── init.py
│   ├── reset.py
│   └── stats.py
├── core/           # Core business logic
│   ├── constants.py
│   ├── filtering.py
│   ├── hash.py
│   └── index_manager.py
└── main.py         # Entry point
```

## License

MIT
