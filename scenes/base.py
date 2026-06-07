import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np

config.pixel_width  = 1080
config.pixel_height = 1920
config.frame_rate   = 30
config.background_color = "#000000"
config.frame_width  = 4.5
config.frame_height = 8.0

MANIM_W = 4.5
MANIM_H = 8.0

# Panel dimensions — calibrated from ref_001 pixel measurements:
#   panel rows 38-62% of frame height, center at ~50%
#   panel cols 10-90% of frame width
PANEL_CENTER_Y = 0.0          # Manim Y=0 is frame center → panel centered at 50%
PANEL_UNIT_W   = 3.80         # 3.80 × 240px = 912px wide  (84% of 1080)
PANEL_UNIT_H   = 2.00         # 2.00 × 240px = 480px tall  (25% of 1920)

# Title vertical position: 30% from top → Manim Y = 4.0 - 0.30×8.0 = 1.60
TITLE_Y_MANIM  = 1.60

# Panel background color matching ref (very dark warm near-black)
PANEL_BG_HEX   = "#0b0507"

STROKE_WIDTH   = 5


class NeonScene(Scene):

    def setup(self):
        self.camera.background_color = "#000000"
        self._draw_panel()

    def _draw_panel(self):
        """Dark warm-tinted panel background with terrain sketch lines."""
        bg = Rectangle(
            width=PANEL_UNIT_W + 0.10,
            height=PANEL_UNIT_H + 0.10,
        )
        bg.move_to([0, PANEL_CENTER_Y, 0])
        bg.set_fill(color=PANEL_BG_HEX, opacity=1.0)
        bg.set_stroke(opacity=0)
        self.add(bg)

        # Terrain — horizontal sketch lines crossing the panel
        ground_y   = PANEL_CENTER_Y - PANEL_UNIT_H * 0.08
        terrain_grp = VGroup()
        for i, (offset, op, sw) in enumerate([
            (0,      0.55, 1.8),
            (-0.22,  0.22, 1.1),
            (-0.38,  0.12, 0.9),
            (-0.52,  0.07, 0.7),
            ( 0.18,  0.10, 0.8),
        ]):
            y = ground_y + offset
            # Slight waviness per line
            pts = []
            steps = 30
            x0, x1 = -PANEL_UNIT_W * 0.48, PANEL_UNIT_W * 0.48
            for s in range(steps + 1):
                t  = s / steps
                x  = x0 + t * (x1 - x0)
                dy = np.sin(t * TAU * (2 + i * 0.7) + i) * 0.018
                pts.append([x, y + dy, 0])
            ln = VMobject()
            ln.set_points_smoothly([np.array(p) for p in pts])
            ln.set_stroke(WHITE, width=sw, opacity=op)
            terrain_grp.add(ln)

        # A few pebble dots
        for px, pr, op in [(-1.55, 0.04, 0.25), (0.40, 0.03, 0.20), (1.30, 0.04, 0.22)]:
            d = Dot([px, ground_y + 0.03, 0], radius=pr, color=WHITE).set_opacity(op)
            terrain_grp.add(d)

        self.add(terrain_grp)

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

    def title_text(self, text, font_size=52, color=WHITE):
        """
        Hook title — upper-left, plain bold white, NO glow (matching ref_001).
        Position: 30% from top, left-aligned.
        """
        title = Text(text, font="Arial", font_size=font_size, color=color, weight=BOLD)
        max_w = MANIM_W * 0.86
        if title.width > max_w:
            title.scale_to_fit_width(max_w)
        title.to_edge(LEFT, buff=0.28)
        title.set_y(TITLE_Y_MANIM)
        return title

    # ── Animation helpers ──────────────────────────────────────────────────

    def impact_burst(self, center, n_rays=8, ray_length=0.45):
        rays = VGroup()
        for i in range(n_rays):
            angle = (TAU / n_rays) * i
            d = np.array([np.cos(angle), np.sin(angle), 0])
            rays.add(Line(
                np.array(center) + d * 0.08,
                np.array(center) + d * ray_length,
                stroke_color=WHITE, stroke_width=3, stroke_opacity=0.9
            ))
        return rays

    def flash_impact(self, center, run_time=0.4):
        burst = self.impact_burst(center)
        self.play(Create(burst), run_time=run_time * 0.5, rate_func=rush_into)
        self.play(FadeOut(burst), run_time=run_time * 0.5)
