"""
Main orchestrator.
Receives a video spec dict (produced by script_generator) and runs the full pipeline:
  1. Render Manim animation
  2. Apply glow post-process
  3. Generate TTS audio + word timestamps
  4. Compose final MP4

Usage (called by me, Claude, directly from conversation):
    from pipeline.run import run_pipeline
    run_pipeline(spec)
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.glow import process_video
from pipeline.tts import generate_voiceover
from pipeline.composer import compose


def run_pipeline(spec: dict) -> str:
    """
    spec keys:
        title        : str  — hook title shown on screen
        script       : str  — full narration text for TTS
        scene_file   : str  — path to generated Manim scene Python file
        scene_class  : str  — Manim scene class name inside scene_file
        slug         : str  — short identifier for output filenames

    Returns path to final MP4.
    """
    slug = spec.get("slug", datetime.now().strftime("%Y%m%d_%H%M%S"))
    work_dir = ROOT / "output" / "videos" / slug
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== PIPELINE START: {slug} ===\n")

    # ── 1. Render Manim ──────────────────────────────────────────────────────
    raw_video = work_dir / "animation_raw.mp4"
    _render_manim(
        scene_file=spec["scene_file"],
        scene_class=spec["scene_class"],
        output_path=raw_video
    )

    # ── 2. Glow post-process ─────────────────────────────────────────────────
    glow_video = work_dir / "animation_glow.mp4"
    process_video(str(raw_video), str(glow_video))

    # ── 3. TTS + timestamps ──────────────────────────────────────────────────
    audio_path = work_dir / "voiceover.mp3"
    tts_result = generate_voiceover(
        script=spec["script"],
        output_path=str(audio_path)
    )

    # ── 4. Compose final video ───────────────────────────────────────────────
    final_path = ROOT / "output" / "videos" / f"{slug}_final.mp4"
    compose(
        animation_video=str(glow_video),
        audio_path=tts_result["audio_path"],
        word_timestamps=tts_result["word_timestamps"],
        title=spec["title"],
        output_path=str(final_path),
        audio_duration=tts_result["duration"]
    )

    print(f"\n=== PIPELINE COMPLETE ===")
    print(f"    Output: {final_path}\n")
    return str(final_path)


def _render_manim(scene_file: str, scene_class: str, output_path: Path) -> None:
    """
    Run Manim CLI to render a scene to MP4.
    Uses high quality settings for 1080x1920.
    """
    python = str(ROOT / ".venv" / "bin" / "python")

    # Manim output goes to a temp dir, then we move to expected output_path
    tmp_output_dir = ROOT / "output" / "videos" / "_manim_tmp"
    tmp_output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        python, "-m", "manim", "render",
        scene_file,
        scene_class,
        "--output_file", scene_class,
        "--media_dir", str(tmp_output_dir),
        "--format", "mp4",
        "--fps", "30",
        "-r", "1080,1920",
        "-q", "h",
        "--disable_caching",
    ]

    print(f"  manim: rendering {scene_class}...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))

    if result.returncode != 0:
        print(result.stdout[-1000:])
        print(result.stderr[-2000:])
        raise RuntimeError(f"Manim render failed for {scene_class}")

    # Find the rendered file and move it
    rendered = list(tmp_output_dir.rglob(f"{scene_class}.mp4"))
    if not rendered:
        rendered = list(tmp_output_dir.rglob("*.mp4"))
    if not rendered:
        raise RuntimeError("Manim rendered successfully but output MP4 not found")

    import shutil
    shutil.move(str(rendered[0]), str(output_path))
    shutil.rmtree(str(tmp_output_dir), ignore_errors=True)
    print(f"  manim: render complete -> {output_path}")
