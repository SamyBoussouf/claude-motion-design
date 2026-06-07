"""
Pipeline simplifié: Manim render → glow → MP4 final.
Pas de TTS, pas de captions (le créateur ajoute audio + sous-titres dans CapCut).

Usage:
    from pipeline.run import render
    render("scenes/wild_horse_effect.py", "WildHorseEffect", "wild_horse_effect")
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.glow import process_video

OUTPUT_DIR = ROOT / "output" / "renders"


def render(scene_file: str, scene_class: str, slug: str) -> str:
    """
    Render scene_class from scene_file, apply glow, save to output/renders/{slug}.mp4
    Returns final MP4 path.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_dir = ROOT / "output" / "_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Manim render
    raw_path = tmp_dir / f"{scene_class}_raw.mp4"
    _render_manim(scene_file, scene_class, tmp_dir, raw_path)

    # 2. Glow post-process
    final_path = OUTPUT_DIR / f"{slug}.mp4"
    process_video(str(raw_path), str(final_path))

    shutil.rmtree(str(tmp_dir), ignore_errors=True)
    print(f"\n=== DONE: {final_path} ===\n")
    return str(final_path)


def _render_manim(scene_file: str, scene_class: str, tmp_dir: Path, output_path: Path) -> None:
    python = str(ROOT / ".venv" / "bin" / "python")
    cmd = [
        python, "-m", "manim", "render",
        scene_file, scene_class,
        "--output_file", scene_class,
        "--media_dir", str(tmp_dir),
        "--format", "mp4",
        "--fps", "30",
        "-r", "1080,1920",
        "-q", "h",
        "--disable_caching",
    ]
    print(f"  rendering {scene_class}...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        print(result.stdout[-800:])
        print(result.stderr[-1500:])
        raise RuntimeError(f"Manim render failed")

    rendered = list(tmp_dir.rglob(f"{scene_class}.mp4"))
    if not rendered:
        rendered = list(tmp_dir.rglob("*.mp4"))
    if not rendered:
        raise RuntimeError("Manim output MP4 not found")

    shutil.move(str(rendered[0]), str(output_path))
    print(f"  raw render -> {output_path}")
