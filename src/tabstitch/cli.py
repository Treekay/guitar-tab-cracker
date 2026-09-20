"""CLI boundary for V1 image ingestion and inspection."""

import argparse
from dataclasses import replace
import json
import logging
from pathlib import Path
import sys
from typing import Sequence
from tabstitch.config import AppConfig, WorkspaceConfig, load_config
from tabstitch.images.pipeline import build_run, inspect_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tabstitch")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)
    config = commands.add_parser("config", help="print resolved configuration")
    _config_option(config)
    config.set_defaults(handler=_show_config)
    inspect = commands.add_parser("inspect", help="validate images and report metadata/ROI")
    inspect.add_argument("input_directory", type=Path)
    inspect.add_argument("--preview", type=Path, help="save ROI contact sheet to a new PNG")
    _config_option(inspect)
    inspect.set_defaults(handler=_inspect)
    build = commands.add_parser("build", help="copy inputs and generate ROI artifacts/preview")
    build.add_argument("input_directory", type=Path)
    build.add_argument("--run-id", required=True)
    build.add_argument("--output", type=Path, help="workspace root (run-id is appended)")
    _config_option(build)
    build.set_defaults(handler=_build)
    layout = commands.add_parser("layout", help="layout command scaffold")
    layout.add_argument("manifest", type=Path)
    _config_option(layout)
    layout.set_defaults(handler=_layout)
    return parser


def _config_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, help="optional TOML configuration file")


def _show_config(args: argparse.Namespace, config: AppConfig) -> int:
    print(json.dumps(config.as_dict(), indent=2))
    return 0


def _inspect(args: argparse.Namespace, config: AppConfig) -> int:
    print(json.dumps(inspect_directory(args.input_directory, config, args.preview), indent=2))
    return 0


def _build(args: argparse.Namespace, config: AppConfig) -> int:
    root = args.output if args.output is not None else config.workspace.root
    effective = replace(config, workspace=WorkspaceConfig(root.resolve()))
    workspace = build_run(args.input_directory, args.run_id, effective)
    logging.getLogger(__name__).info("Image ingestion complete at %s", workspace.root)
    print(workspace.root)
    print("No measure detection has been performed.", file=sys.stderr)
    return 0


def _layout(args: argparse.Namespace, config: AppConfig) -> int:
    if not args.manifest.resolve().is_file():
        raise ValueError(f"manifest does not exist: {args.manifest.resolve()}")
    print("Layout is not implemented until V1 Task 9.", file=sys.stderr)
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        logging.basicConfig(level=getattr(logging, config.logging.level), format="%(levelname)s %(name)s: %(message)s")
        return int(args.handler(args, config))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 2
