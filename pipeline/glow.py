"""
OpenCV post-process: applies neon glow effect to Manim-rendered frames.
Simulates the Saber/AE bloom by screen-blending a gaussian-blurred
white channel over the original sharp strokes.
"""

import cv2
import numpy as np
import os
from pathlib import Path


def apply_glow_to_frame(frame_bgr: np.ndarray, blur_radius: int = 21,
                         intensity: float = 1.8, passes: int = 2) -> np.ndarray:
    """
    Apply neon glow to a single frame (numpy array, BGR).

    Steps:
    1. Extract the bright (white stroke) layer
    2. Apply gaussian blur N times
    3. Screen blend the blurred glow over the original
    4. Add subtle background noise for organic texture
    """
    if blur_radius % 2 == 0:
        blur_radius += 1

    # Convert to float for precision
    frame_f = frame_bgr.astype(np.float32) / 255.0

    # Build glow layer from the bright channel
    glow = frame_f.copy()
    for _ in range(passes):
        glow = cv2.GaussianBlur(glow, (blur_radius, blur_radius), 0)

    # Boost glow intensity
    glow = np.clip(glow * intensity, 0, 1)

    # Screen blend: result = 1 - (1-base)*(1-glow)
    result = 1.0 - (1.0 - frame_f) * (1.0 - glow)

    # Subtle pink/warm tint on the glow halo (matches ref color temperature)
    tint = np.zeros_like(result)
    tint[:, :, 2] = glow[:, :, 2] * 0.08   # slight red lift
    tint[:, :, 0] = glow[:, :, 0] * -0.04  # slight blue reduction
    result = np.clip(result + tint, 0, 1)

    # Background grain — organic texture on dark areas
    noise = np.random.normal(0, 0.018, result.shape).astype(np.float32)
    dark_mask = 1.0 - result  # noise only visible in dark regions
    result = np.clip(result + noise * dark_mask * 0.7, 0, 1)

    return (result * 255).astype(np.uint8)


def process_video(input_path: str, output_path: str,
                  blur_radius: int = 21, intensity: float = 1.8,
                  passes: int = 2) -> None:
    """
    Apply glow post-process to an entire video file.
    Reads frame by frame, processes, writes output.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    processed = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        glowed = apply_glow_to_frame(frame, blur_radius, intensity, passes)
        out.write(glowed)
        processed += 1
        if processed % 30 == 0:
            pct = processed / total * 100 if total > 0 else 0
            print(f"  glow: {processed}/{total} frames ({pct:.0f}%)")

    cap.release()
    out.release()
    print(f"  glow complete -> {output_path}")


def process_frames_dir(frames_dir: str, output_dir: str,
                       blur_radius: int = 21, intensity: float = 1.8,
                       passes: int = 2) -> None:
    """
    Apply glow to a directory of PNG frames.
    Output frames go to output_dir with same filenames.
    """
    frames_dir = Path(frames_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = sorted(frames_dir.glob("*.png"))
    total = len(frames)

    for i, frame_path in enumerate(frames):
        frame = cv2.imread(str(frame_path))
        if frame is None:
            continue
        glowed = apply_glow_to_frame(frame, blur_radius, intensity, passes)
        cv2.imwrite(str(output_dir / frame_path.name), glowed)
        if (i + 1) % 30 == 0:
            print(f"  glow frames: {i+1}/{total}")

    print(f"  glow frames complete -> {output_dir}")
