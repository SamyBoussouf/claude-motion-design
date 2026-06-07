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
# Default Manim uses 14.2 x 8 (16:9), which distorts portrait renders.
# Setting frame_width = 8 * (9/16) = 4.5 gives square pixels: 1 unit = 240px.
config.frame_width = 4.5
config.frame_height = 8.0

MANIM_W = 4.5   # total frame width in Manim units
MANIM_H = 8.0   # total frame height in Manim units

# Panel: 16:9 landscape window centered in the 9:16 portrait frame
# Takes ~27% of frame height, matching ref_001 layout
PANEL_UNIT_W = MANIM_W * 0.88          # 3.96 units ~ 950px
PANEL_UNIT_H = PANEL_UNIT_W * 0.5625   # 2.23 units ~ 535px (16:9)
PANEL_CENTER_Y = -0.5                   # slightly below center, matching ref_001


class NeonScene(Scene):
    """
    Base class for all psychovius-style neon animation scenes.
    Provides helpers for drawing glowing strokes, labels, and impact effects.
    All subclasses should call super().setup() and use the provided helpers.
    """

    def setup(self):
        self.camera.background_color = BG_COLOR
        self._draw_panel_bg()

    def _draw_panel_bg(self):
        # Subtle ground lines inside the panel — matches ref_001 terrain texture
        ground = VGroup()
        y_positions = np.linspace(
            PANEL_CENTER_Y - PANEL_UNIT_H * 0.5 * 0.6,
            PANEL_CENTER_Y - PANEL_UNIT_H * 0.5 * 0.9,
            4
        )
        for y in y_positions:
            line = Line(
                [-PANEL_UNIT_W * 0.48, y, 0],
                [PANEL_UNIT_W * 0.48, y, 0],
                stroke_color=WHITE,
                stroke_width=0.8,
                stroke_opacity=0.18
            )
            ground.add(line)
        self.add(ground)

    def neon_path(self, points, stroke_width=STROKE_WIDTH, color=WHITE, opacity=1.0):
        """Create a VMobject path from a list of [x,y,0] points."""
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

    def word_label(self, text, position, font_size=36, color=WHITE):
        """Single word label that appears as narration subtitle."""
        label = Text(
            text,
            font="Arial",
            font_size=font_size,
            color=color,
            weight=NORMAL
        )
        label.move_to(position)
        return label

    def title_text(self, text, font_size=52, color=WHITE):
        """Persistent title hook — upper third of frame.
        With 1 unit = 240px: y=2.3 → 240px from top edge."""
        title = Text(
            text,
            font="Arial",
            font_size=font_size,
            color=color,
            weight=BOLD,
        )
        # Scale to fit within frame width with margins
        if title.width > MANIM_W * 0.85:
            title.scale_to_fit_width(MANIM_W * 0.85)
        # Position: upper third — y = MANIM_H/2 - 1.0 ≈ 3.0 → ~240px from top
        title.move_to([-0.0, MANIM_H * 0.5 - 1.2, 0])
        return title

    def impact_burst(self, center, n_rays=8, ray_length=0.9):
        """Star-burst flash effect for collision/impact moments."""
        rays = VGroup()
        for i in range(n_rays):
            angle = (TAU / n_rays) * i
            direction = np.array([np.cos(angle), np.sin(angle), 0])
            ray = Line(
                np.array(center) + direction * 0.15,
                np.array(center) + direction * ray_length,
                stroke_color=WHITE,
                stroke_width=3,
                stroke_opacity=0.9
            )
            rays.add(ray)
        return rays

    def draw_in(self, mobject, run_time=1.5):
        """Animate a path being drawn progressively (neon draw-on effect)."""
        self.play(Create(mobject), run_time=run_time, rate_func=linear)

    def flash_impact(self, center, run_time=0.4):
        """Play impact burst animation."""
        burst = self.impact_burst(center)
        self.play(
            Create(burst),
            run_time=run_time * 0.5,
            rate_func=rush_into
        )
        self.play(
            FadeOut(burst),
            run_time=run_time * 0.5,
            rate_func=rush_from
        )

    def show_word(self, text, position=None, duration=0.6, font_size=36):
        """Pop a single narration word, hold it, then fade out."""
        if position is None:
            position = [0, PANEL_CENTER_Y - PANEL_UNIT_H * 0.5 - 0.4, 0]
        label = self.word_label(text, position, font_size=font_size)
        self.play(FadeIn(label, shift=UP * 0.1), run_time=0.15)
        self.wait(duration)
        self.play(FadeOut(label), run_time=0.15)
