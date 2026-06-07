"""
Composition module.
Assembles animation + audio + text overlays into the final 1080x1920 MP4.

Text overlays (title + word captions) are rendered via PIL/Pillow since
the installed FFmpeg was built without libfreetype (no drawtext filter).

Pipeline:
  1. Decode animation frames (OpenCV)
  2. For each frame: composite title + word caption via PIL
  3. Re-encode frames to video (OpenCV VideoWriter -> FFmpeg re-encode for quality)
  4. Merge with audio via FFmpeg
"""

import subprocess
import shlex
import shutil
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from config.style import (
    CANVAS_W, CANVAS_H, FPS,
    TITLE_FONT_SIZE, WORD_FONT_SIZE,
    TITLE_X, TITLE_Y,
)

# System fonts available on macOS
FONT_BOLD_PATH = "/System/Library/Fonts/Helvetica.ttc"
FONT_REGULAR_PATH = "/System/Library/Fonts/Helvetica.ttc"


def _load_font(path: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size=size)
    except Exception:
        return ImageFont.load_default()


def _wrap_title(text: str, max_chars: int = 24) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars or not current:
            current = (current + " " + w).strip()
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _render_title_overlay(title: str, w: int, h: int) -> np.ndarray:
    """
    Render persistent title as RGBA PIL image, return as numpy BGRA.
    Pre-rendered once and reused on every frame.
    """
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _load_font(FONT_BOLD_PATH, TITLE_FONT_SIZE, bold=True)

    lines = _wrap_title(title)
    x, y = TITLE_X, TITLE_Y
    line_h = TITLE_FONT_SIZE + 14

    for line in lines:
        # Subtle shadow for depth
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 120))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_h

    return np.array(img)


def _build_word_index(word_timestamps: list[dict], fps: float) -> dict[int, str]:
    """
    Build a frame_number -> word mapping.
    Each frame that falls within a word's time window gets that word.
    """
    index = {}
    for wt in word_timestamps:
        t_in = float(wt["start"])
        t_out = float(wt["end"]) + 0.05
        frame_in = int(t_in * fps)
        frame_out = int(t_out * fps)
        word = wt["word"].upper()
        for f in range(frame_in, frame_out + 1):
            index[f] = word
    return index


def _composite_frame(
    frame_bgr: np.ndarray,
    title_overlay: np.ndarray,
    word: str | None,
    word_font: ImageFont.FreeTypeFont,
    canvas_w: int,
    canvas_h: int,
) -> np.ndarray:
    """
    Composite title overlay and optional word caption onto a single BGR frame.
    Returns BGR frame.
    """
    # Convert frame to PIL RGBA
    frame_rgba = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGBA))

    # Paste title overlay (RGBA alpha composite)
    title_img = Image.fromarray(title_overlay, mode="RGBA")
    frame_rgba = Image.alpha_composite(frame_rgba, title_img)

    # Word caption
    if word:
        word_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(word_img)
        # Measure text for centering
        bbox = d.textbbox((0, 0), word, font=word_font)
        tw = bbox[2] - bbox[0]
        wx = (canvas_w - tw) // 2
        wy = canvas_h // 2 + 85
        # Shadow
        d.text((wx + 2, wy + 2), word, font=word_font, fill=(0, 0, 0, 140))
        d.text((wx, wy), word, font=word_font, fill=(255, 255, 255, 255))
        frame_rgba = Image.alpha_composite(frame_rgba, word_img)

    return cv2.cvtColor(np.array(frame_rgba), cv2.COLOR_RGBA2BGR)


def _ffmpeg_run(cmd: list[str], label: str) -> None:
    print(f"  ffmpeg [{label}]...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-1500:])
        raise RuntimeError(f"FFmpeg failed: {label}")


def compose(
    animation_video: str,
    audio_path: str,
    word_timestamps: list[dict],
    title: str,
    output_path: str,
    audio_duration: float,
) -> str:
    """
    Full composition pipeline. Returns path to final MP4.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_path.parent / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    # ── 1. Open source video ─────────────────────────────────────────────
    cap = cv2.VideoCapture(animation_video)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or FPS
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_src = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_out = int(audio_duration * src_fps) + 5

    print(f"  composer: {src_w}x{src_h} @ {src_fps}fps, {total_src} src frames -> {total_out} output frames")

    # Title is already baked into the Manim animation with neon glow.
    # We only overlay word captions via PIL.
    word_font = _load_font(FONT_REGULAR_PATH, WORD_FONT_SIZE)
    word_index = _build_word_index(word_timestamps, src_fps)

    # Blank title overlay (transparent — no PIL title, Manim handles it)
    blank_title = np.zeros((src_h, src_w, 4), dtype=np.uint8)

    # ── 3. Write composited frames to raw video ──────────────────────────
    raw_out = str(tmp_dir / "composited_raw.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(raw_out, fourcc, src_fps, (src_w, src_h))

    frame_num = 0
    src_frame_num = 0

    while frame_num < total_out:
        # Loop source video if needed
        if src_frame_num >= total_src:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            src_frame_num = 0

        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            src_frame_num = 0
            ret, frame = cap.read()
            if not ret:
                break

        word = word_index.get(frame_num)
        composited = _composite_frame(frame, blank_title, word, word_font, src_w, src_h)
        writer.write(composited)

        frame_num += 1
        src_frame_num += 1

        if frame_num % 90 == 0:
            pct = frame_num / total_out * 100
            print(f"  composer: {frame_num}/{total_out} frames ({pct:.0f}%)")

    cap.release()
    writer.release()
    print(f"  composer: frame compositing complete")

    # ── 4. Re-encode with FFmpeg (better compression) + add audio ────────
    _ffmpeg_run([
        "ffmpeg", "-y",
        "-i", raw_out,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path)
    ], "encode+audio")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"  composer: final video -> {output_path}")
    return str(output_path)
