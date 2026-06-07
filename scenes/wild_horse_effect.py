"""
Wild Horse Effect — animation continue ~45s.

Scènes enchaînées sans coupure:
  S1 (0-13s)  : terrain + saw + snake apparaît à gauche, rampe vers la scie, se fait couper
  S2 (13-26s) : le serpent se love autour de la scie pour combattre — spirale serrée
  S3 (26-34s) : le serpent s'épuise et devient flasque / meurt
  S4 (34-45s) : label "The Wild Horse Effect", puis "Calm is power."

Aucune caption/sous-titre — le créateur ajoute audio + texte dans CapCut.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from scenes.base import (
    NeonScene, PANEL_CENTER_Y, PANEL_UNIT_W, PANEL_UNIT_H, MANIM_H, STROKE_WIDTH
)

config.pixel_width  = 1080
config.pixel_height = 1920
config.frame_rate   = 30
config.background_color = "#000000"
config.frame_width  = 4.5
config.frame_height = 8.0

# Layout — all relative to panel constants imported from base
GROUND_Y  = PANEL_CENTER_Y - PANEL_UNIT_H * 0.10   # ground line (just below center)
SAW_CX    = PANEL_UNIT_W  * 0.32                    # saw center x (right third)
SNAKE_X0  = -PANEL_UNIT_W * 0.47                    # snake tail start x (left edge)
SNAKE_LEN = PANEL_UNIT_W  * 0.42                    # snake body length


class WildHorseEffect(NeonScene):

    def construct(self):

        # ── Title — persistent, plain bold white ──────────────────────────
        title = self.title_text("Not Everything Is Against You..")
        self.play(FadeIn(title), run_time=0.6)
        self.wait(0.4)

        # ── S1a: saw appears ──────────────────────────────────────────────
        saw = self._saw(SAW_CX, GROUND_Y)
        self.play(Create(saw), run_time=1.2)
        self.wait(0.2)

        # ── S1b: snake draws in from left ─────────────────────────────────
        snake = self._snake_straight(SNAKE_X0, GROUND_Y)
        self.play(Create(snake), run_time=1.4, rate_func=linear)

        # crawl toward saw in two moves
        self.play(snake.animate.shift(RIGHT * SNAKE_LEN * 0.55),
                  run_time=2.2, rate_func=linear)
        self.play(snake.animate.shift(RIGHT * SNAKE_LEN * 0.55),
                  run_time=1.8, rate_func=linear)

        # ── S1c: contact + cut flash ──────────────────────────────────────
        cut_pt = [SAW_CX - PANEL_UNIT_W * 0.05, GROUND_Y + 0.06, 0]
        self.flash_impact(cut_pt, run_time=0.5)
        sparks = self._sparks(cut_pt, n=7, length=0.28)
        self.play(Create(sparks), run_time=0.2)
        self.play(FadeOut(sparks), run_time=0.3)
        self.wait(0.5)

        # ── S2: snake coils around saw ────────────────────────────────────
        coiled = self._snake_coiled(SAW_CX, GROUND_Y, tightness=1.0)
        self.play(Transform(snake, coiled), run_time=2.2, rate_func=smooth)
        self.wait(0.6)

        # tighten — fighting harder
        tighter = self._snake_coiled(SAW_CX, GROUND_Y, tightness=0.78)
        self.play(Transform(snake, tighter), run_time=1.8, rate_func=smooth)

        # damage radiates from the saw
        dmg = self._damage(SAW_CX, GROUND_Y)
        self.play(Create(dmg), run_time=0.9)
        self.play(dmg.animate.scale(1.4).set_stroke(opacity=0.55), run_time=1.2)
        self.wait(0.4)

        # ── S3: snake exhausted — fades, goes limp ────────────────────────
        limp = self._snake_limp(SAW_CX, GROUND_Y)
        self.play(
            Transform(snake, limp),
            FadeOut(dmg),
            run_time=1.8, rate_func=smooth
        )
        self.wait(0.3)
        self.play(snake.animate.set_stroke(opacity=0.18), run_time=1.5)

        # saw unchanged — it was never threatened
        saw_hl = saw.copy().set_stroke(opacity=1.0)
        self.play(GrowFromCenter(saw_hl), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(saw_hl), run_time=0.4)

        # ── Transition: fade scene out ────────────────────────────────────
        self.play(FadeOut(snake), FadeOut(saw), run_time=0.8)
        self.wait(0.15)

        # ── S4a: "The Wild Horse Effect" ──────────────────────────────────
        label = Text("The Wild Horse Effect",
                     font="Arial", font_size=46, color=WHITE, weight=BOLD)
        label.move_to([0, PANEL_CENTER_Y + 0.35, 0])
        uline = Line(
            label.get_left() + DOWN * 0.28,
            label.get_right() + DOWN * 0.28,
            stroke_color=WHITE, stroke_width=1.8, stroke_opacity=0.5
        )
        self.play(Write(label), run_time=1.2)
        self.play(Create(uline), run_time=0.4)
        self.wait(1.2)
        self.play(FadeOut(label), FadeOut(uline), run_time=0.6)

        # ── S4b: "Calm is power." ─────────────────────────────────────────
        calm = Text("Calm is power.", font="Arial",
                    font_size=58, color=WHITE, weight=BOLD)
        calm.move_to([0, PANEL_CENTER_Y, 0])
        self.play(Write(calm), run_time=1.2)
        self.wait(2.5)
        self.play(FadeOut(calm), FadeOut(title), run_time=0.9)
        self.wait(0.5)

    # ── Element builders ──────────────────────────────────────────────────

    def _saw(self, cx: float, y: float) -> VGroup:
        """
        Bear-trap style saw matching ref_001:
        rectangular body with jagged teeth on top, circular gear/pivot detail.
        Sized to occupy ~28% of panel width.
        """
        g  = VGroup()
        W  = PANEL_UNIT_W * 0.30   # ~0.90 units wide
        H  = PANEL_UNIT_H * 0.46   # ~0.46 units tall

        # Body rectangle
        body = Rectangle(width=W, height=H)
        body.move_to([cx + W * 0.05, y + H * 0.28, 0])
        body.set_stroke(WHITE, width=5.5).set_fill(opacity=0)
        g.add(body)

        # Teeth across the top
        n = 12
        x0 = cx - W * 0.43
        x1 = cx + W * 0.57
        by = y + H * 0.57
        th = H * 0.36
        sp = (x1 - x0) / n
        pts = [np.array([x0, by, 0])]
        for i in range(n):
            tx = x0 + i * sp
            pts.append(np.array([tx + sp * 0.5, by + th, 0]))
            pts.append(np.array([tx + sp, by, 0]))
        teeth = VMobject().set_points_as_corners(pts)
        teeth.set_stroke(WHITE, width=4.5)
        g.add(teeth)

        # Circular pivot
        pivot_r = W * 0.13
        pivot = Circle(radius=pivot_r)
        pivot.move_to([cx + W * 0.38, y + H * 0.28, 0])
        pivot.set_stroke(WHITE, width=4.0).set_fill(opacity=0)
        g.add(pivot)

        # Inner dot of pivot
        inner = Dot([cx + W * 0.38, y + H * 0.28, 0],
                    radius=pivot_r * 0.32, color=WHITE).set_opacity(0.7)
        g.add(inner)

        return g

    def _snake_straight(self, start_x: float, y: float) -> VGroup:
        """Sinuous snake body + head, sized to match ref_001."""
        g    = VGroup()
        segs = 32
        pts  = [
            np.array([
                start_x + (i / segs) * SNAKE_LEN,
                y + np.sin((i / segs) * TAU * 1.6) * 0.13,
                0
            ])
            for i in range(segs + 1)
        ]
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=6.0)
        g.add(body)

        head_pos = np.array([start_x + SNAKE_LEN + 0.12, y + 0.01, 0])
        head = Circle(radius=0.12)
        head.move_to(head_pos)
        head.set_stroke(WHITE, width=5).set_fill(opacity=0)
        g.add(head)
        return g

    def _snake_coiled(self, saw_cx: float, y: float, tightness: float = 1.0) -> VGroup:
        """Spiral coil around the saw."""
        g  = VGroup()
        cx = saw_cx + 0.10
        cy = y + PANEL_UNIT_H * 0.18
        turns = 1.85 * tightness
        segs  = 80
        pts = []
        for i in range(segs + 1):
            t     = i / segs
            angle = t * TAU * turns
            r     = 0.82 - t * 0.28 * tightness
            pts.append(np.array([
                cx + r * np.cos(angle),
                cy + r * np.sin(angle) * 0.52,
                0
            ]))
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=6.0)
        g.add(body)
        head = Circle(radius=0.11).move_to(pts[-1])
        head.set_stroke(WHITE, width=4.5).set_fill(opacity=0)
        g.add(head)
        return g

    def _snake_limp(self, saw_cx: float, y: float) -> VGroup:
        """Dead/exhausted snake draped below the saw."""
        g  = VGroup()
        cx = saw_cx + 0.08
        pts = [
            np.array([cx - PANEL_UNIT_W * 0.28, y - 0.11, 0]),
            np.array([cx - PANEL_UNIT_W * 0.14, y + 0.06, 0]),
            np.array([cx + 0.00,                y + 0.02, 0]),
            np.array([cx + PANEL_UNIT_W * 0.10, y + 0.07, 0]),
            np.array([cx + PANEL_UNIT_W * 0.20, y - 0.10, 0]),
        ]
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=5.5)
        g.add(body)
        head = Circle(radius=0.10).move_to(pts[-1] + np.array([0.09, -0.04, 0]))
        head.set_stroke(WHITE, width=4).set_fill(opacity=0)
        g.add(head)
        return g

    def _sparks(self, center, n: int = 7, length: float = 0.26) -> VGroup:
        g = VGroup()
        for i in range(n):
            a = (TAU / n) * i + TAU / (n * 2)
            d = np.array([np.cos(a), np.sin(a), 0])
            g.add(Line(
                np.array(center) + d * 0.05,
                np.array(center) + d * length,
                stroke_color=WHITE, stroke_width=3, stroke_opacity=0.9
            ))
        return g

    def _damage(self, saw_cx: float, y: float) -> VGroup:
        """Short radiating lines around saw — energy/frustration."""
        g  = VGroup()
        cx = saw_cx + 0.10
        cy = y + PANEL_UNIT_H * 0.18
        for angle_deg in [0, 55, 110, 170, 225, 285, 340]:
            a = np.radians(angle_deg)
            d = np.array([np.cos(a), np.sin(a) * 0.55, 0])
            g.add(Line(
                np.array([cx, cy, 0]) + d * 0.48,
                np.array([cx, cy, 0]) + d * 0.82,
                stroke_color=WHITE, stroke_width=2.2, stroke_opacity=0.75
            ))
        return g
