# Contributing to wzgram

Thanks for your interest in contributing!

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for package management and [poethepoet](https://github.com/nat-n/poethepoet) for task running.

```bash
git clone https://github.com/rjriajul/wzgram
cd wzgram
uv sync --frozen --extra dev
uv run poe api
```

## Running Tests

```bash
uv run poe test
```

## Building Docs

```bash
uv run poe docs
```

## Available Tasks

| Command | Description |
|---------|-------------|
| `uv run poe venv` | Sync frozen environment |
| `uv run poe venv-dev` | Sync dev environment |
| `uv run poe api` | Generate TL API types |
| `uv run poe test` | Run tests |
| `uv run poe docs` | Build documentation |
| `uv run poe build` | Build sdist and wheel |
| `uv run poe publish` | Publish to PyPI |
| `uv run poe tag` | Create and push git tag |
| `uv run poe clean` | Clean all generated files |

## Submitting Changes

1. Fork the repo
2. Create a branch from `dev`
3. Make your changes
4. Run `uv run poe test` to verify
5. Submit a pull request to `dev`

## Code Style

- Follow the existing Sphinx/reST docstring style for any new methods or types
- Add type hints to all function signatures
- Keep methods focused and well-documented
