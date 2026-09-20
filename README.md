# tabstitch

Private CLI-first tooling for reconstructing printable guitar tablature from overlapping screenshots.

The repository is at **V1 Task 1**. The CLI, configuration loader, and run workspace exist; image ingestion, measure detection, reconstruction, and rendering do not.

## Setup and commands

Requires Python 3.11+.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
tabstitch --help
tabstitch config --config config.example.toml
tabstitch inspect examples/input-images
tabstitch build examples/input-images --run-id demo
tabstitch layout runs/demo/manifest.json
python -m pytest
```

Configuration combines built-in defaults with an optional TOML file. Explicit CLI values take precedence. `config` works now. `inspect` reports resolved inputs and `build` creates an inspectable workspace without processing or modifying images. `layout` is an explicit placeholder for V1 Task 9.

```text
runs/<id>/
  inputs/  crops/  normalized/  matches/  outputs/
  manifest.json
  summary.md
```

Run IDs are path-safe and existing runs are never overwritten. The bootstrap manifest records provenance, resolved configuration, lifecycle state, and creation time.

## Product references

- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Execution plan](docs/EXECUTION_PLAN.md)
- [Product skill](.agents/skills/guitar-tab-product/SKILL.md)

V1 excludes video, score recognition, AI runtime integration, Guitar Pro export, web UI, billing, authentication, and MCP integration.
