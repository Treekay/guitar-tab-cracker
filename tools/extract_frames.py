"""Mechanical video inventory/extraction; every timestamp is chosen by Codex.

python tools/extract_frames.py probe VIDEO --output result/source/source.json
python tools/extract_frames.py frames VIDEO --timestamps 1.25 8.5 --output result/frames

Requires ffprobe and ffmpeg on PATH, or explicit --ffprobe / --ffmpeg paths.
No sampling, content inspection, scene detection or measure inference.
"""

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import uuid


def run(command):
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ValueError(f"Executable unavailable: {command[0]}; provide its explicit path") from exc
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"{command[0]} failed: {exc.stderr.strip()}") from exc


def probe(video, executable):
    data = json.loads(run([
        executable, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "format=duration:stream=index,width,height,avg_frame_rate,duration",
        "-of", "json", str(video),
    ]).stdout)
    if not data.get("streams"):
        raise ValueError("No video stream found")
    stream = data["streams"][0]
    duration = stream.get("duration", data.get("format", {}).get("duration"))
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        duration = None
    if duration is not None and (not math.isfinite(duration) or duration <= 0):
        duration = None
    try:
        fps = float(Fraction(stream.get("avg_frame_rate", "0/0")))
    except (ValueError, ZeroDivisionError):
        fps = None
    with video.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    return {
        "local_path": str(video), "sha256": digest,
        "duration_seconds": duration, "width": stream["width"],
        "height": stream["height"], "approximate_fps": fps,
        "video_stream_index": stream["index"],
    }


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def extract(video, timestamps, destination, metadata, executable):
    # Validate all decisions before extracting anything. Preserve given order.
    names = []
    for timestamp in timestamps:
        if not math.isfinite(timestamp) or timestamp < 0:
            raise ValueError("Timestamps must be finite, nonnegative seconds")
        duration = metadata["duration_seconds"]
        if duration is not None and timestamp >= duration:
            raise ValueError(f"Timestamp {timestamp} is outside duration {duration}")
        names.append(f"t_{timestamp:.9f}.png")
    if len(set(names)) != len(names):
        raise ValueError("Duplicate timestamps at nanosecond filename precision")
    for name in names:
        if (destination / name).exists():
            raise ValueError(f"Existing frame would be overwritten: {destination / name}")
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    # A batch manifest records every successful frame, even if a later one fails.
    manifest = destination / f"extraction_{uuid.uuid4().hex}.json"
    try:
        for timestamp, name in zip(timestamps, names):
            with tempfile.TemporaryDirectory(prefix="extract-", dir=destination) as temp:
                frame = Path(temp) / "frame.png"
                run([
                    executable, "-hide_banner", "-loglevel", "error", "-nostdin",
                    "-ss", repr(timestamp), "-i", str(video), "-map", "0:v:0",
                    "-frames:v", "1", "-update", "1", "-n", str(frame),
                ])
                if not frame.is_file() or frame.stat().st_size == 0:
                    raise ValueError(f"No frame decoded at {timestamp}; choose another timestamp")
                frame.rename(destination / name)
            records.append({"requested_timestamp_seconds": timestamp, "file": name})
    finally:
        write_json(manifest, {
            "source": metadata, "frames": records,
            "requested_timestamps_seconds": timestamps,
            "complete": len(records) == len(timestamps),
            "note": "Requested seek times, not exact decoded PTS. Extraction does not imply visual inspection.",
        })
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("probe", "frames"):
        command = sub.add_parser(name)
        command.add_argument("video", type=Path)
        command.add_argument("--ffprobe", default="ffprobe")
        command.add_argument("--output", type=Path, required=True)
        if name == "probe":
            command.add_argument("--source-url", help="Original supplied URL; acquisition is external")
        else:
            command.add_argument("--ffmpeg", default="ffmpeg")
            command.add_argument("--timestamps", nargs="+", type=float, required=True)
    args = parser.parse_args()
    try:
        video = args.video.resolve(strict=True)
        metadata = probe(video, args.ffprobe)
        if args.action == "probe":
            metadata["supplied_source"] = args.source_url or str(args.video)
            write_json(args.output, metadata)
            print(json.dumps(metadata, indent=2))
        else:
            print(extract(video, args.timestamps, args.output.resolve(), metadata, args.ffmpeg))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
