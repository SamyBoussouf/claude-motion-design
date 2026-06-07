"""
Wild Horse Effect — full animation, ~45s.
Beat map:
  0-2s    Title fade in
  2-5s    Terrain + saw draw
  5-14s   Snake slithers in, crosses saw, gets cut
  14-23s  Snake coils around saw to fight back
  23-31s  Coiling tighter — damage radiates
  31-37s  Snake goes limp / dies
  37-43s  Wild Horse Effect label
  43-55s  Lesson: reaction diagram + calm
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from scenes.base import NeonScene, PANEL_CENTER_Y, PANEL_UNIT_W, PANEL_UNIT_H, MANIM_H

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.background_color = "#000000"
config.frame_width = 4.5
config.frame_height = 8.0

# Scene layout constants
GROUND_Y = PANEL_CENTER_Y - PANEL_UNIT_H * 0.22   # ground line y
SAW_X    = PANEL_UNIT_W * 0.22                     # saw center x
SNAKE_X0 = -PANEL_UNIT_W * 0.44                    # snake start x


class WildHorseEffect(NeonScene):

    def construct(self):

        # ── 1. Title ─────────────────────────────────────────────────────
        title = self.title_text("Not Everything Is Against You..")
        self.play(FadeIn(title, shift=DOWN * 0.08), run_time=0.7)
        self.wait(0.5)

        # ── 2. Terrain ────────────────────────────────────────────────────
        terrain = self._build_terrain()
        self.play(Create(terrain), run_time=0.7)

        # ── 3. Saw ────────────────────────────────────────────────────────
        saw = self._build_saw(SAW_X, GROUND_Y)
        self.play(Create(saw), run_time=1.3)
        self.wait(0.3)

        # ── 4. Snake draws in ─────────────────────────────────────────────
        snake = self._build_snake_straight(SNAKE_X0, GROUND_Y)
        self.play(Create(snake), run_time=1.5, rate_func=linear)
        self.wait(0.2)

        # Snake crawls right toward saw
        self.play(snake.animate.shift(RIGHT * 1.1), run_time=2.0, rate_func=linear)
        self.play(snake.animate.shift(RIGHT * 0.9), run_time=1.6, rate_func=linear)
        self.play(snake.animate.shift(RIGHT * 0.45), run_time=0.7, rate_func=rush_into)

        # ── 5. Contact / cut ──────────────────────────────────────────────
        cut_pos = [SAW_X - 0.35, GROUND_Y + 0.08, 0]
        self.flash_impact(cut_pos, run_time=0.5)
        sparks = self._cut_sparks(cut_pos)
        self.play(Create(sparks), run_time=0.25)
        self.wait(0.4)
        self.play(FadeOut(sparks), run_time=0.3)
        self.wait(0.5)

        # ── 6. Snake coils around saw (fighting back) ─────────────────────
        coiled = self._build_snake_coiled(SAW_X, GROUND_Y, tightness=1.0)
        self.play(Transform(snake, coiled), run_time=2.2, rate_func=smooth)
        self.wait(0.7)

        # Tighten further
        coiled_tight = self._build_snake_coiled(SAW_X, GROUND_Y, tightness=0.80)
        self.play(Transform(snake, coiled_tight), run_time=1.8, rate_func=smooth)

        # Damage lines radiate
        damage = self._build_damage_lines(SAW_X, GROUND_Y)
        self.play(Create(damage), run_time=1.0)
        self.play(damage.animate.scale(1.35).set_stroke(opacity=0.65), run_time=1.2)
        self.wait(0.4)

        # ── 7. Snake dies ─────────────────────────────────────────────────
        limp = self._build_snake_limp(SAW_X, GROUND_Y)
        self.play(
            Transform(snake, limp),
            FadeOut(damage),
            run_time=1.8, rate_func=smooth
        )
        self.wait(0.4)
        self.play(snake.animate.set_stroke(opacity=0.22), run_time=1.4)

        # Saw highlight — it was never threatened
        hl = saw.copy().set_stroke(opacity=1.0)
        self.play(GrowFromCenter(hl), run_time=0.7)
        self.wait(0.3)
        self.play(FadeOut(hl), run_time=0.5)

        # ── 8. Transition out ─────────────────────────────────────────────
        self.play(FadeOut(snake), FadeOut(saw), FadeOut(terrain), run_time=1.0)
        self.wait(0.2)

        # ── 9. Wild Horse Effect label ────────────────────────────────────
        whe = Text("The Wild Horse Effect", font="Arial",
                   font_size=52, color=WHITE, weight=BOLD)
        whe.move_to([0, PANEL_CENTER_Y + 0.5, 0])
        underline = Line(
            whe.get_left() + DOWN * 0.32,
            whe.get_right() + DOWN * 0.32,
            stroke_color=WHITE, stroke_width=2, stroke_opacity=0.55
        )
        self.play(Write(whe), run_time=1.4)
        self.play(Create(underline), run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(whe), FadeOut(underline), run_time=0.7)

        # ── 10. Reaction diagram ──────────────────────────────────────────
        person   = self._build_person([-1.7, PANEL_CENTER_Y - 0.2, 0])
        arrow_in = self._build_arrow(
            [-0.7, PANEL_CENTER_Y - 0.2, 0],
            [0.5, PANEL_CENTER_Y - 0.2, 0],
            label="reaction"
        )
        chaos    = self._build_chaos_arrows([1.4, PANEL_CENTER_Y - 0.2, 0])

        self.play(Create(person), run_time=1.0)
        self.wait(0.2)
        self.play(Create(arrow_in), run_time=0.8)
        self.play(Create(chaos), run_time=1.0)
        self.wait(0.9)

        # Strike through chaos
        strike = Line(
            chaos.get_left() + LEFT * 0.15,
            chaos.get_right() + RIGHT * 0.15,
            stroke_color=WHITE, stroke_width=5
        )
        self.play(Create(strike), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(chaos), FadeOut(strike), run_time=0.7)

        # Replace with calm straight arrow
        calm_arrow = Arrow(
            [0.5, PANEL_CENTER_Y - 0.2, 0],
            [2.1, PANEL_CENTER_Y - 0.2, 0],
            stroke_color=WHITE, stroke_width=4,
            buff=0, max_tip_length_to_length_ratio=0.18
        )
        self.play(Create(calm_arrow), run_time=0.8)
        self.wait(0.7)

        # ── 11. Calm is power ─────────────────────────────────────────────
        self.play(FadeOut(person), FadeOut(arrow_in),
                  FadeOut(calm_arrow), run_time=0.7)
        calm = Text("Calm is power.", font="Arial",
                    font_size=60, color=WHITE, weight=BOLD)
        calm.move_to([0, PANEL_CENTER_Y, 0])
        self.play(Write(calm), run_time=1.4)
        self.wait(2.5)
        self.play(FadeOut(calm), run_time=0.9)
        self.wait(0.5)

    # ── Element builders ───────────────────────────────────────────────────

    def _build_terrain(self) -> VGroup:
        g = VGroup()
        # Primary ground — bold, slightly above GROUND_Y
        g.add(self.neon_line(
            [-PANEL_UNIT_W * 0.49, GROUND_Y, 0],
            [PANEL_UNIT_W * 0.49, GROUND_Y, 0],
            stroke_width=2.2, opacity=0.60
        ))
        # Secondary depth lines below
        for offset, op in [(-0.18, 0.20), (-0.34, 0.11)]:
            g.add(self.neon_line(
                [-PANEL_UNIT_W * 0.47, GROUND_Y + offset, 0],
                [PANEL_UNIT_W * 0.47, GROUND_Y + offset, 0],
                stroke_width=1.3, opacity=op
            ))
        # Pebbles
        for px, pr in [(-2.5, 0.055), (0.6, 0.045), (2.0, 0.050)]:
            d = Dot([px, GROUND_Y + 0.04, 0], radius=pr,
                    color=WHITE).set_opacity(0.28)
            g.add(d)
        return g

    def _build_saw(self, x: float, y: float) -> VGroup:
        """Larger saw matching ref_001 proportions."""
        g = VGroup()
        W, H = 1.30, 0.66
        body = Rectangle(width=W, height=H)
        body.move_to([x + W * 0.15, y + H * 0.25, 0])
        body.set_stroke(WHITE, width=5.0).set_fill(opacity=0)
        g.add(body)

        # Teeth row across the top
        n = 12
        x0, x1 = x - W * 0.35, x + W * 0.65
        base_y = y + H * 0.52
        tooth_h = 0.26
        sp = (x1 - x0) / n
        pts = []
        for i in range(n):
            tx = x0 + i * sp
            pts += [np.array([tx, base_y, 0]),
                    np.array([tx + sp * 0.5, base_y + tooth_h, 0])]
        pts.append(np.array([x1, base_y, 0]))
        teeth = VMobject().set_points_as_corners(pts)
        teeth.set_stroke(WHITE, width=4.0)
        g.add(teeth)

        # Pivot circle
        pivot = Circle(radius=0.13).move_to([x + W * 0.42, y + H * 0.25, 0])
        pivot.set_stroke(WHITE, width=3.5).set_fill(opacity=0)
        g.add(pivot)
        return g

    def _build_snake_straight(self, start_x: float, y: float) -> VGroup:
        """Larger snake with sinuous body."""
        g = VGroup()
        length, segs = 2.0, 28
        pts = [
            np.array([start_x + (i / segs) * length,
                       y + np.sin((i / segs) * TAU * 1.4) * 0.155, 0])
            for i in range(segs + 1)
        ]
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=6.5)
        g.add(body)
        head = Circle(radius=0.135).move_to(
            [start_x + length + 0.135, y + 0.01, 0]
        )
        head.set_stroke(WHITE, width=5).set_fill(opacity=0)
        g.add(head)
        return g

    def _build_snake_coiled(self, saw_x: float, y: float,
                             tightness: float = 1.0) -> VGroup:
        g = VGroup()
        cx, cy = saw_x + 0.20, y + 0.28
        turns, segs = 1.9 * tightness, 70
        pts = []
        for i in range(segs + 1):
            t = i / segs
            angle = t * TAU * turns
            r = 0.95 - t * 0.30 * tightness
            pts.append(np.array([
                cx + r * np.cos(angle),
                cy + r * np.sin(angle) * 0.58, 0
            ]))
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=6.5)
        g.add(body)
        head = Circle(radius=0.135).move_to(pts[-1])
        head.set_stroke(WHITE, width=5).set_fill(opacity=0)
        g.add(head)
        return g

    def _build_snake_limp(self, saw_x: float, y: float) -> VGroup:
        g = VGroup()
        cx = saw_x + 0.18
        pts = [
            np.array([cx - 1.3, y - 0.14, 0]),
            np.array([cx - 0.7, y + 0.07, 0]),
            np.array([cx - 0.1, y + 0.02, 0]),
            np.array([cx + 0.35, y + 0.09, 0]),
            np.array([cx + 0.72, y - 0.12, 0]),
        ]
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=5.5)
        g.add(body)
        head = Circle(radius=0.12).move_to([cx + 0.80, y - 0.17, 0])
        head.set_stroke(WHITE, width=4).set_fill(opacity=0)
        g.add(head)
        return g

    def _cut_sparks(self, center, n=6, length=0.30) -> VGroup:
        g = VGroup()
        for i in range(n):
            a = (TAU / n) * i + TAU / (n * 2)
            d = np.array([np.cos(a), np.sin(a), 0])
            g.add(Line(np.array(center) + d * 0.06,
                       np.array(center) + d * length,
                       stroke_color=WHITE, stroke_width=3, stroke_opacity=0.88))
        return g

    def _build_damage_lines(self, saw_x: float, y: float) -> VGroup:
        g = VGroup()
        cx, cy = saw_x + 0.20, y + 0.28
        for angle in [25, 80, 140, 195, 255, 315]:
            a = np.radians(angle)
            d = np.array([np.cos(a), np.sin(a) * 0.58, 0])
            g.add(Line(np.array([cx, cy, 0]) + d * 0.55,
                       np.array([cx, cy, 0]) + d * 0.95,
                       stroke_color=WHITE, stroke_width=2.2, stroke_opacity=0.72))
        return g

    def _build_person(self, center) -> VGroup:
        g = VGroup()
        cx, cy, _ = center
        # Head
        g.add(Circle(radius=0.24).move_to([cx, cy + 0.75, 0])
              .set_stroke(WHITE, 4.5).set_fill(opacity=0))
        # Body
        g.add(Line([cx, cy + 0.51, 0], [cx, cy - 0.24, 0],
                   stroke_color=WHITE, stroke_width=4.5))
        # Arms
        g.add(Line([cx - 0.40, cy + 0.18, 0], [cx + 0.40, cy + 0.18, 0],
                   stroke_color=WHITE, stroke_width=4.0))
        # Legs
        g.add(Line([cx, cy - 0.24, 0], [cx - 0.30, cy - 0.75, 0],
                   stroke_color=WHITE, stroke_width=4.0))
        g.add(Line([cx, cy - 0.24, 0], [cx + 0.30, cy - 0.75, 0],
                   stroke_color=WHITE, stroke_width=4.0))
        return g

    def _build_arrow(self, start, end, label: str = "") -> VGroup:
        g = VGroup()
        arr = Arrow(np.array(start), np.array(end),
                    stroke_color=WHITE, stroke_width=4, buff=0,
                    max_tip_length_to_length_ratio=0.18)
        g.add(arr)
        if label:
            lbl = Text(label, font="Arial", font_size=30, color=WHITE)
            lbl.move_to(np.array([(start[0]+end[0])/2, start[1]+0.34, 0]))
            g.add(lbl)
        return g

    def _build_chaos_arrows(self, center) -> VGroup:
        g = VGroup()
        cx, cy, _ = center
        for angle, length in [(40, 0.55), (95, 0.48), (155, 0.52),
                               (-25, 0.50), (-100, 0.45)]:
            a = np.radians(angle)
            end = np.array([cx + np.cos(a)*length, cy + np.sin(a)*length, 0])
            g.add(Arrow(np.array([cx, cy, 0]), end,
                        stroke_color=WHITE, stroke_width=3.5,
                        buff=0, max_tip_length_to_length_ratio=0.22))
        return g
