# Quick Start Guide

## Installation

```bash
# Install in development mode (recommended for development)
pip install -e .

# Or install normally
pip install .
```

## Running the Application

### Using the installed command

After installation, simply run:

```bash
personal-assistant
```

### Test vs Release Mode

**Test Mode** (default) - Uses `demo_data/` and `demo_index/`:
```bash
personal-assistant --test
```

**Release Mode** - Uses production data directories:
```bash
personal-assistant --release
```

### Alternative: Run without installation

You can also run directly from the source:

```bash
python -m personal_assistant.main
```

## Building Distribution Packages

To create distribution packages (wheel and source):

```bash
# Install build tool
pip install build

# Build the package
python -m build
```

This creates:
- `dist/personal_assistant-1.0.0-py3-none-any.whl` (wheel)
- `dist/personal-assistant-1.0.0.tar.gz` (source distribution)

## Installing from Built Package

```bash
pip install dist/personal_assistant-1.0.0-py3-none-any.whl
```

## Uninstallation

```bash
pip uninstall personal-assistant
```

## Troubleshooting

### Command not found after installation

Make sure your Python scripts directory is in your PATH. You can find it with:
```bash
python -m site --user-base
```

Add `{user-base}/bin` (Linux/Mac) or `{user-base}\Scripts` (Windows) to your PATH.

### Import errors

If you get import errors, ensure you're in the correct directory or the package is properly installed:
```bash
pip show personal-assistant
```

