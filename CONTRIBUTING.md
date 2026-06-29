# Contributing to wzgram

Thanks for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/rjriajul/wzgram
cd wzgram
make venv
make api
```

## Running Tests

```bash
tox
```

## Building Docs

```bash
pip install -e .[docs]
python compiler/docs/compiler.py
sphinx-build -b dirhtml docs/source docs/build
```

## Submitting Changes

1. Fork the repo
2. Create a branch from `dev`
3. Make your changes
4. Run tests
5. Submit a pull request to `dev`

## Code Style

- Follow the existing Sphinx/reST docstring style for any new methods or types
- Add type hints to all function signatures
- Keep methods focused and well-documented
