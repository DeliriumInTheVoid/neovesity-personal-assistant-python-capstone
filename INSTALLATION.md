# Personal Assistant - Installation Guide

## Installation

### Install in development mode (editable)

For development, install the package in editable mode:

```bash
pip install -e .
```

This allows you to make changes to the code and see them reflected immediately.

### Install in production mode

For regular use, install the package:

```bash
pip install .
```

### Install with development dependencies

To install with testing dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

After installation, you can run the personal assistant from anywhere using:

```bash
personal-assistant
```

### Command-line options

- **Test mode** (uses demo_data and demo_index):
  ```bash
  personal-assistant --test
  ```
  or
  ```bash
  ASSISTANT_MODE=test personal-assistant
  ```

- **Release mode** (uses production data):
  ```bash
  personal-assistant --release
  ```
  or
  ```bash
  ASSISTANT_MODE=release personal-assistant
  ```

Default mode is `test` if not specified.

## Uninstallation

To uninstall the package:

```bash
pip uninstall personal-assistant
```

## Building Distribution

To build a distribution package:

```bash
pip install build
python -m build
```

This will create `.whl` and `.tar.gz` files in the `dist/` directory that can be distributed to others.

## Publishing to PyPI (Optional)

To publish to PyPI:

```bash
pip install twine
python -m build
twine upload dist/*
```

