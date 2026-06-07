"""
FFmpeg composition module.
Assembles animation video + audio + title overlay + word-sync captions
into the final 1080x1920 MP4.
"""

import subprocess
import json
import os
import shlex
from pathlib import Path
from config.style import (
    CANVAS_W, CANVAS_H, FPS,
    TITLE_FONT_SIZE, WORD_FONT_SIZE,
    TITLE_X, TITLE_Y, PANEL_Y_CENTER
)


def _run(cmd: list[str], label: str = "") -> None:
    print(f"  ffmpeg [{label}]: {' '.join(shlex.quote(c) for c in cmd[:6])}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError(f"FFmpeg failed at step: {label}")


def _escape(text: str) -> str:
    """Escape text for ffmpeg drawtext filter."""
    return (text
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace(":", "\\:")
            .replace(",", "\\,")
            .replace("[", "\\[")
            .replace("]", "\\]"))


def build_word_filter(word_timestamps: list[dict], canvas_h: int = CANVAS_H,
                       font_size: int = WORD_FONT_SIZE) -> str:
    """
    Build an ffmpeg drawtext filter chain for word-by-word caption sync.
    Each word appears for its duration, then disappears.
    Words are centered horizontally, positioned just below the panel.
    """
    filters = []
    # Vertical position: center of canvas (panel area) + offset below
    y_pos = canvas_h // 2 + 80

    for wt in word_timestamps:
        word = _escape(wt["word"].upper())
        t_in = wt["start"]
        t_out = wt["end"] + 0.05  # tiny hold after end

        f = (
            f"drawtext=text='{word}'"
            f":fontfile=/System/Library/Fonts/Helvetica.ttc"
            f":fontsize={font_size}"
            f":fontcolor=white"
            f":x=(w-text_w)/2"
            f":y={y_pos}"
            f":enable='between(t,{t_in:.3f},{t_out:.3f})'"
        )
        filters.append(f)

    return ",".join(filters)


def build_title_filter(title: str, font_size: int = TITLE_FONT_SIZE,
                        x: int = TITLE_X, y: int = TITLE_Y) -> str:
    """
    Build ffmpeg drawtext filter for the persistent title hook.
    Renders for the full duration of the video.
    """
    escaped = _escape(title)
    # Word-wrap at ~22 chars — insert newlines manually if needed
    lines = _wrap_title(title, max_chars=22)
    result = []
    line_y = y
    line_height = font_size + 12

    for line in lines:
        result.append(
            f"drawtext=text='{_escape(line)}'"
            f":fontfile=/System/Library/Fonts/Helvetica.ttc"
            f":fontsize={font_size}"
            f":fontcolor=white"
            f":x={x}"
            f":y={line_y}"
            f":box=0"
        )
        line_y += line_height

    return ",".join(result)


def _wrap_title(text: str, max_chars: int = 22) -> list[str]:
    """Break title into lines of max_chars words."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars or not current:
            current = (current + " " + w).strip()
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def compose(
    animation_video: str,
    audio_path: str,
    word_timestamps: list[dict],
    title: str,
    output_path: str,
    audio_duration: float
) -> str:
    """
    Full composition pipeline:
    1. Pad/trim animation to match audio duration
    2. Overlay title text (persistent)
    3. Overlay word-sync captions
    4. Mix in audio
    5. Encode final MP4

    Returns path to final video.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = output_path.parent / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    # Step 1: Loop animation to cover full audio duration, add audio
    tmp_with_audio = str(tmp_dir / "with_audio.mp4")
    _run([
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", animation_video,
        "-i", audio_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(audio_duration + 0.5),
        "-shortest",
        "-vf", f"scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=decrease,"
               f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:(oh-ih)/2:black",
        tmp_with_audio
    ], "loop+audio")

    # Step 2: Build text filters
    title_filter = build_title_filter(title)
    word_filter = build_word_filter(word_timestamps)

    full_filter = title_filter + "," + word_filter if word_timestamps else title_filter

    # Step 3: Apply text overlays and encode final output
    _run([
        "ffmpeg", "-y",
        "-i", tmp_with_audio,
        "-vf", full_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path)
    ], "text_overlay+encode")

    # Cleanup temp
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"  composer: final video -> {output_path}")
    return str(output_path)
