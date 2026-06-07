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
PANEL_CENTER_Y = 0.40         # panel centered at 45% from top (matches ref_001)
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
        """
        Terrain lines on pure black — NO background rectangle.
        The warm glow effect comes from OpenCV post-processing only, matching ref_001.
        """
        ground_y = PANEL_CENTER_Y - PANEL_UNIT_H * 0.08
        terrain  = VGroup()

        # Many horizontal sketch lines at varying opacity/width — ref_001 style
        line_defs = [
            # (y_offset, opacity, stroke_width, x_scale)
            ( 0.00,  0.60, 2.0, 1.00),   # main ground line
            (-0.20,  0.25, 1.2, 0.97),
            (-0.35,  0.14, 1.0, 0.94),
            (-0.50,  0.08, 0.8, 0.90),
            (-0.64,  0.05, 0.7, 0.86),
            ( 0.16,  0.12, 0.9, 0.96),
            ( 0.30,  0.06, 0.7, 0.92),
            (-0.12,  0.18, 1.1, 0.98),
        ]
        steps = 40
        for i, (offset, op, sw, xs) in enumerate(line_defs):
            y  = ground_y + offset
            x0 = -PANEL_UNIT_W * 0.50 * xs
            x1 =  PANEL_UNIT_W * 0.50 * xs
            pts = []
            for s in range(steps + 1):
                t  = s / steps
                x  = x0 + t * (x1 - x0)
                dy = np.sin(t * TAU * (1.5 + i * 0.6) + i * 1.1) * 0.016
                pts.append(np.array([x, y + dy, 0]))
            ln = VMobject()
            ln.set_points_smoothly(pts)
            ln.set_stroke(WHITE, width=sw, opacity=op)
            terrain.add(ln)

        # Pebbles
        for px, pr, op in [(-1.60, 0.04, 0.22), (0.35, 0.03, 0.17), (1.25, 0.04, 0.19)]:
            terrain.add(Dot([px, ground_y + 0.03, 0], radius=pr,
                            color=WHITE).set_opacity(op))

        self.add(terrain)

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
