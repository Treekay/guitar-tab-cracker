"""Command-line skeleton for the V1 pipeline."""

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Sequence
from tabstitch.config import ConfigError, load_config
from tabstitch.workspace import RunWorkspace, WorkspaceError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tabstitch")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)
    config = commands.add_parser("config", help="print resolved configuration")
    _config_option(config); config.set_defaults(handler=_show_config)
    inspect = commands.add_parser("inspect", help="resolve input folder (scaffold)")
    inspect.add_argument("input_directory", type=Path); _config_option(inspect); inspect.set_defaults(handler=_inspect)
    build = commands.add_parser("build", help="initialize a V1 run workspace")
    build.add_argument("input_directory", type=Path); build.add_argument("--run-id", required=True)
    build.add_argument("--output", type=Path); _config_option(build); build.set_defaults(handler=_build)
    layout = commands.add_parser("layout", help="layout command scaffold")
    layout.add_argument("manifest", type=Path); _config_option(layout); layout.set_defaults(handler=_layout)
    return parser


def _config_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, help="optional TOML configuration file")


def _directory(path: Path) -> Path:
    path = path.resolve()
    if not path.is_dir():
        raise ValueError(f"input directory does not exist: {path}")
    return path


def _show_config(args: argparse.Namespace) -> int:
    print(json.dumps(load_config(args.config).as_dict(), indent=2)); return 0


def _inspect(args: argparse.Namespace) -> int:
    config, source = load_config(args.config), _directory(args.input_directory)
    print(json.dumps({"input_directory": str(source), "config": config.as_dict()}, indent=2))
    print("Image inspection is not implemented until V1 Task 2.", file=sys.stderr); return 0


def _build(args: argparse.Namespace) -> int:
    config, source = load_config(args.config), _directory(args.input_directory)
    root = args.output if args.output is not None else config.workspace.root
    workspace = RunWorkspace.create(root, args.run_id, source, config.as_dict())
    logging.getLogger(__name__).info("Initialized run workspace at %s", workspace.root)
    print(workspace.root); print("Image processing is not implemented until later V1 tasks.", file=sys.stderr); return 0


def _layout(args: argparse.Namespace) -> int:
    load_config(args.config)
    if not args.manifest.resolve().is_file():
        raise ValueError(f"manifest does not exist: {args.manifest.resolve()}")
    print("Layout is not implemented until V1 Task 9.", file=sys.stderr); return 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser(); args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        logging.basicConfig(level=getattr(logging, config.logging.level), format="%(levelname)s %(name)s: %(message)s")
        return int(args.handler(args))
    except (ConfigError, WorkspaceError, ValueError) as exc:
        parser.error(str(exc))
    return 2
