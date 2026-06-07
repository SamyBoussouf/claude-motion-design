import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from config.style import (
    BG_COLOR, STROKE_COLOR, STROKE_WIDTH,
    PANEL_W, PANEL_H, CANVAS_W, CANVAS_H, FPS
)

# Manim config for 1080x1920 vertical format
config.pixel_width = CANVAS_W
config.pixel_height = CANVAS_H
config.frame_rate = FPS
config.background_color = BG_COLOR

# Force correct aspect ratio for 9:16 portrait
# 1 unit = 240px in both axes (square pixels)
config.frame_width = 4.5
config.frame_height = 8.0

MANIM_W = 4.5
MANIM_H = 8.0

# Panel: landscape 16:9 strip within the portrait frame
# Matches ref_001: panel centered at ~45% down the frame, filling most of the width
PANEL_UNIT_W = MANIM_W * 0.92          # 4.14 units  ~  994px
PANEL_UNIT_H = PANEL_UNIT_W * 0.5625   # 2.33 units  ~  559px  (16:9)
PANEL_CENTER_Y = 0.80                   # upper-center → ~768px from top (40% down)


class NeonScene(Scene):
    """
    Base class for all psychovius-style neon animation scenes.
    """

    def setup(self):
        self.camera.background_color = BG_COLOR
        self._draw_panel_bg()

    def _draw_panel_bg(self):
        """Subtle horizontal ground lines — ref_001 terrain texture."""
        ground = VGroup()
        y_positions = np.linspace(
            PANEL_CENTER_Y - PANEL_UNIT_H * 0.30,
            PANEL_CENTER_Y - PANEL_UNIT_H * 0.48,
            4
        )
        for y in y_positions:
            line = Line(
                [-PANEL_UNIT_W * 0.49, y, 0],
                [PANEL_UNIT_W * 0.49, y, 0],
                stroke_color=WHITE,
                stroke_width=1.0,
                stroke_opacity=0.22
            )
            ground.add(line)
        self.add(ground)

    # ── Primitive builders ─────────────────────────────────────────────────

    def neon_path(self, points, stroke_width=STROKE_WIDTH, color=WHITE, opacity=1.0):
        path = VMobject()
        path.set_points_smoothly([np.array(p) for p in points])
        path.set_stroke(color=color, width=stroke_width, opacity=opacity)
        path.set_fill(opacity=0)
        return path

    def neon_circle(self, center, radius, stroke_width=STROKE_WIDTH, color=WHITE):
        c = Circle(radius=radius)
        c.move_to(center)
        c.set_stroke(color=color, width=stroke_width)
        c.set_fill(opacity=0)
        return c

    def neon_line(self, start, end, stroke_width=STROKE_WIDTH, color=WHITE, opacity=1.0):
        return Line(
            np.array(start), np.array(end),
            stroke_color=color,
            stroke_width=stroke_width,
            stroke_opacity=opacity
        )

    # ── Text helpers ───────────────────────────────────────────────────────

    def title_text(self, text, font_size=56, color=WHITE):
        """
        Persistent hook title — upper-left of frame, matching ref_001.
        Position: ~200px from top, ~80px from left.
        """
        title = Text(
            text,
            font="Arial",
            font_size=font_size,
            color=color,
            weight=BOLD,
        )
        max_w = MANIM_W * 0.88
        if title.width > max_w:
            title.scale_to_fit_width(max_w)
        # Left-align: shift left edge to frame left + margin
        title.to_edge(LEFT, buff=0.28)
        # Vertical: upper area — ~200px from top  →  y = 4.0 - 200/240 ≈ 3.17
        title.set_y(MANIM_H * 0.5 - 1.0)
        return title

    def word_label(self, text, position, font_size=38, color=WHITE):
        label = Text(text, font="Arial", font_size=font_size,
                     color=color, weight=NORMAL)
        label.move_to(position)
        return label

    # ── Animation helpers ──────────────────────────────────────────────────

    def impact_burst(self, center, n_rays=8, ray_length=0.55):
        rays = VGroup()
        for i in range(n_rays):
            angle = (TAU / n_rays) * i
            d = np.array([np.cos(angle), np.sin(angle), 0])
            rays.add(Line(
                np.array(center) + d * 0.10,
                np.array(center) + d * ray_length,
                stroke_color=WHITE, stroke_width=3, stroke_opacity=0.9
            ))
        return rays

    def draw_in(self, mobject, run_time=1.5):
        self.play(Create(mobject), run_time=run_time, rate_func=linear)

    def flash_impact(self, center, run_time=0.4):
        burst = self.impact_burst(center)
        self.play(Create(burst), run_time=run_time * 0.5, rate_func=rush_into)
        self.play(FadeOut(burst), run_time=run_time * 0.5, rate_func=rush_from)

    def show_word(self, text, position=None, duration=0.6, font_size=38):
        if position is None:
            position = [0, PANEL_CENTER_Y - PANEL_UNIT_H * 0.5 - 0.35, 0]
        label = self.word_label(text, position, font_size=font_size)
        self.play(FadeIn(label, shift=UP * 0.08), run_time=0.12)
        self.wait(duration)
        self.play(FadeOut(label), run_time=0.12)
