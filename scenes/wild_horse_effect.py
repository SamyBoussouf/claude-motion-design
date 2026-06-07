"""
Wild Horse Effect — full 55-second animation.
Narration is handled externally (ElevenLabs + FFmpeg).
This scene is pure visual storytelling, no baked-in word labels.

Beat map (approximate, tuned to the script pacing):
  0-2s    Title fade in
  2-5s    Terrain + saw draw
  5-13s   Snake slithers in, crosses saw, gets cut
  13-22s  Snake coils around saw to fight back
  22-30s  Coiling tighter — damage radiates
  30-36s  Snake goes limp / dies
  36-42s  Wild Horse Effect title card
  42-55s  Lesson scenes — reaction diagram + calm
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from scenes.base import NeonScene, PANEL_CENTER_Y, PANEL_UNIT_W, PANEL_UNIT_H

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30
config.background_color = "#000000"
config.frame_width = 4.5
config.frame_height = 8.0

GROUND_Y = PANEL_CENTER_Y - PANEL_UNIT_H * 0.28
SAW_X = PANEL_UNIT_W * 0.20
SNAKE_START_X = -PANEL_UNIT_W * 0.42


class WildHorseEffect(NeonScene):

    def construct(self):
        # ── Title — persists through the whole video ──────────────────────
        title = self.title_text("Not Everything Is Against You..")
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.7)
        self.wait(0.5)

        # ── Terrain ───────────────────────────────────────────────────────
        terrain = self._build_terrain()
        self.play(Create(terrain), run_time=0.8)

        # ── Saw ───────────────────────────────────────────────────────────
        saw_group = self._build_saw(SAW_X, GROUND_Y)
        self.play(Create(saw_group), run_time=1.2)
        self.wait(0.4)

        # ── Snake enters from left ────────────────────────────────────────
        snake = self._build_snake_straight(SNAKE_START_X, GROUND_Y)
        self.play(Create(snake), run_time=1.4, rate_func=linear)
        self.wait(0.2)

        # Snake crawls toward the saw
        self.play(
            snake.animate.shift(RIGHT * 1.0),
            run_time=2.0, rate_func=linear
        )
        self.play(
            snake.animate.shift(RIGHT * 0.9),
            run_time=1.8, rate_func=linear
        )

        # ── Contact: snake tip reaches saw — small cut ────────────────────
        cut_pos = [SAW_X - 0.5, GROUND_Y + 0.1, 0]
        self.play(
            snake.animate.shift(RIGHT * 0.4),
            run_time=0.6, rate_func=rush_into
        )
        self.flash_impact(cut_pos, run_time=0.45)

        # Small cut marks radiating from contact
        cut_marks = self._cut_sparks(cut_pos, n=5, length=0.25)
        self.play(Create(cut_marks), run_time=0.3)
        self.wait(0.5)
        self.play(FadeOut(cut_marks), run_time=0.4)
        self.wait(0.6)

        # ── Snake coils around saw (fighting back) ────────────────────────
        coiled = self._build_snake_coiled(SAW_X, GROUND_Y)
        self.play(
            Transform(snake, coiled),
            run_time=2.2, rate_func=smooth
        )
        self.wait(0.8)

        # Tighten — second coil pass
        coiled_tight = self._build_snake_coiled(SAW_X, GROUND_Y, tightness=0.82)
        self.play(
            Transform(snake, coiled_tight),
            run_time=1.8, rate_func=smooth
        )

        # Damage: bleeding lines grow from contact
        damage = self._build_damage_lines(SAW_X, GROUND_Y)
        self.play(Create(damage), run_time=1.0)
        self.play(
            damage.animate.scale(1.4).set_stroke(opacity=0.7),
            run_time=1.2
        )
        self.wait(0.5)

        # ── Snake dies — goes limp ────────────────────────────────────────
        limp = self._build_snake_limp(SAW_X, GROUND_Y)
        self.play(
            Transform(snake, limp),
            FadeOut(damage),
            run_time=2.0, rate_func=smooth
        )
        self.wait(0.5)

        # Fade snake (death)
        self.play(
            snake.animate.set_stroke(opacity=0.25),
            run_time=1.5, rate_func=smooth
        )
        self.wait(0.8)

        # ── Saw unmoved — stays perfectly still ───────────────────────────
        # (saw_group never moved — this is the visual irony)
        highlight_saw = saw_group.copy().set_stroke(opacity=0.9)
        self.play(
            GrowFromCenter(highlight_saw),
            run_time=0.8
        )
        self.wait(0.4)
        self.play(FadeOut(highlight_saw), run_time=0.5)

        # ── Clear scene, transition to lesson ─────────────────────────────
        self.play(
            FadeOut(snake),
            FadeOut(saw_group),
            FadeOut(terrain),
            run_time=1.2
        )
        self.wait(0.3)

        # ── Wild Horse Effect label ────────────────────────────────────────
        whe_label = Text(
            "The Wild Horse Effect",
            font="Arial",
            font_size=54,
            color=WHITE,
            weight=BOLD
        )
        whe_label.move_to([0, PANEL_CENTER_Y + 0.6, 0])
        underline = Line(
            whe_label.get_left() + DOWN * 0.35,
            whe_label.get_right() + DOWN * 0.35,
            stroke_color=WHITE,
            stroke_width=2,
            stroke_opacity=0.6
        )
        self.play(
            Write(whe_label),
            run_time=1.5
        )
        self.play(Create(underline), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(whe_label), FadeOut(underline), run_time=0.8)

        # ── Reaction diagram — person figure + stimulus/response ──────────
        person = self._build_person_figure([-1.8, PANEL_CENTER_Y - 0.3, 0])
        stimulus = self._build_arrow(
            [-0.7, PANEL_CENTER_Y - 0.3, 0],
            [0.7, PANEL_CENTER_Y - 0.3, 0],
            label="reaction"
        )
        chaos = self._build_chaos_arrows([1.6, PANEL_CENTER_Y - 0.3, 0])

        self.play(Create(person), run_time=1.0)
        self.wait(0.3)
        self.play(Create(stimulus), run_time=0.8)
        self.play(Create(chaos), run_time=1.0)
        self.wait(1.0)

        # Strike through chaos — show the right path
        strike = Line(
            chaos.get_left() + LEFT * 0.2,
            chaos.get_right() + RIGHT * 0.2,
            stroke_color=WHITE,
            stroke_width=5,
            stroke_opacity=0.9
        )
        self.play(Create(strike), run_time=0.5)
        self.wait(0.6)
        self.play(
            FadeOut(chaos),
            FadeOut(strike),
            run_time=0.8
        )

        # Replace chaos with calm arrow (straight, smooth)
        calm_arrow = Arrow(
            [0.7, PANEL_CENTER_Y - 0.3, 0],
            [2.4, PANEL_CENTER_Y - 0.3, 0],
            stroke_color=WHITE,
            stroke_width=4,
            buff=0
        )
        self.play(Create(calm_arrow), run_time=0.8)
        self.wait(0.8)

        # ── Final: Calm is power ──────────────────────────────────────────
        self.play(
            FadeOut(person),
            FadeOut(stimulus),
            FadeOut(calm_arrow),
            run_time=0.8
        )

        calm_text = Text(
            "Calm is power.",
            font="Arial",
            font_size=62,
            color=WHITE,
            weight=BOLD
        )
        calm_text.move_to([0, PANEL_CENTER_Y, 0])
        self.play(Write(calm_text), run_time=1.4)
        self.wait(2.5)
        self.play(FadeOut(calm_text), run_time=1.0)
        self.wait(0.5)

    # ── Visual element builders ────────────────────────────────────────────

    def _build_terrain(self) -> VGroup:
        g = VGroup()
        # Primary ground
        g.add(self.neon_line(
            [-PANEL_UNIT_W * 0.48, GROUND_Y, 0],
            [PANEL_UNIT_W * 0.48, GROUND_Y, 0],
            stroke_width=2.0, opacity=0.55
        ))
        # Secondary ground depth lines
        for offset, opacity in [(-0.22, 0.18), (-0.42, 0.10)]:
            g.add(self.neon_line(
                [-PANEL_UNIT_W * 0.46, GROUND_Y + offset, 0],
                [PANEL_UNIT_W * 0.46, GROUND_Y + offset, 0],
                stroke_width=1.2, opacity=opacity
            ))
        # Small rocks / pebbles
        for rx, ry, rr in [(-2.8, GROUND_Y + 0.05, 0.07),
                             (0.8, GROUND_Y + 0.04, 0.05),
                             (2.2, GROUND_Y + 0.06, 0.06)]:
            g.add(Dot([rx, ry, 0], radius=rr, color=WHITE).set_opacity(0.3))
        return g

    def _build_saw(self, x: float, y: float) -> VGroup:
        g = VGroup()
        # Body
        body = Rectangle(width=1.15, height=0.58)
        body.move_to([x + 0.22, y + 0.14, 0])
        body.set_stroke(WHITE, width=4.5)
        body.set_fill(opacity=0)
        g.add(body)
        # Teeth
        n, x0, x1 = 10, x - 0.28, x + 0.70
        base_y = y + 0.42
        spacing = (x1 - x0) / n
        pts = []
        for i in range(n):
            tx = x0 + i * spacing
            pts.append(np.array([tx, base_y, 0]))
            pts.append(np.array([tx + spacing * 0.5, base_y + 0.24, 0]))
        pts.append(np.array([x1, base_y, 0]))
        teeth = VMobject()
        teeth.set_points_as_corners(pts)
        teeth.set_stroke(WHITE, width=3.5)
        g.add(teeth)
        # Pivot screw
        screw = Circle(radius=0.115).move_to([x + 0.58, y + 0.14, 0])
        screw.set_stroke(WHITE, width=3).set_fill(opacity=0)
        g.add(screw)
        return g

    def _build_snake_straight(self, start_x: float, y: float) -> VGroup:
        g = VGroup()
        segments = 24
        length = 1.7
        pts = [
            np.array([start_x + (i / segments) * length,
                       y + np.sin((i / segments) * TAU * 1.2) * 0.13, 0])
            for i in range(segments + 1)
        ]
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=5.5)
        g.add(body)
        head = Circle(radius=0.11).move_to(
            [start_x + length + 0.11, y + 0.01, 0]
        )
        head.set_stroke(WHITE, width=4).set_fill(opacity=0)
        g.add(head)
        return g

    def _build_snake_coiled(self, saw_x: float, y: float,
                             tightness: float = 1.0) -> VGroup:
        g = VGroup()
        cx, cy = saw_x + 0.22, y + 0.25
        turns = 1.8 * tightness
        segments = 60
        pts = []
        for i in range(segments + 1):
            t = i / segments
            angle = t * TAU * turns
            r = 0.85 - t * 0.28 * tightness
            pts.append(np.array([
                cx + r * np.cos(angle),
                cy + r * np.sin(angle) * 0.55,
                0
            ]))
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=5.5)
        g.add(body)
        # Head at end of coil
        end = pts[-1]
        head = Circle(radius=0.11).move_to(end)
        head.set_stroke(WHITE, width=4).set_fill(opacity=0)
        g.add(head)
        return g

    def _build_snake_limp(self, saw_x: float, y: float) -> VGroup:
        """Snake in a collapsed, defeated position below the saw."""
        g = VGroup()
        cx = saw_x + 0.15
        pts = [
            np.array([cx - 1.2, y - 0.12, 0]),
            np.array([cx - 0.7, y + 0.06, 0]),
            np.array([cx - 0.2, y + 0.02, 0]),
            np.array([cx + 0.3, y + 0.08, 0]),
            np.array([cx + 0.65, y - 0.10, 0]),
        ]
        body = VMobject()
        body.set_points_smoothly(pts)
        body.set_stroke(WHITE, width=4.5)
        g.add(body)
        head = Circle(radius=0.10).move_to([cx + 0.72, y - 0.14, 0])
        head.set_stroke(WHITE, width=3.5).set_fill(opacity=0)
        g.add(head)
        return g

    def _cut_sparks(self, center, n: int = 5, length: float = 0.25) -> VGroup:
        g = VGroup()
        for i in range(n):
            angle = (TAU / n) * i + TAU / (n * 2)
            d = np.array([np.cos(angle), np.sin(angle), 0])
            g.add(Line(
                np.array(center) + d * 0.05,
                np.array(center) + d * length,
                stroke_color=WHITE, stroke_width=2.5, stroke_opacity=0.85
            ))
        return g

    def _build_damage_lines(self, saw_x: float, y: float) -> VGroup:
        g = VGroup()
        cx, cy = saw_x + 0.22, y + 0.25
        for angle in [30, 90, 145, 200, 260, 320]:
            a = np.radians(angle)
            d = np.array([np.cos(a), np.sin(a) * 0.55, 0])
            g.add(Line(
                np.array([cx, cy, 0]) + d * 0.5,
                np.array([cx, cy, 0]) + d * 0.9,
                stroke_color=WHITE, stroke_width=2, stroke_opacity=0.7
            ))
        return g

    def _build_person_figure(self, center) -> VGroup:
        g = VGroup()
        cx, cy, _ = center
        # Head
        g.add(Circle(radius=0.22).move_to([cx, cy + 0.72, 0])
              .set_stroke(WHITE, 4).set_fill(opacity=0))
        # Body
        g.add(Line([cx, cy + 0.50, 0], [cx, cy - 0.22, 0],
                   stroke_color=WHITE, stroke_width=4))
        # Arms
        g.add(Line([cx - 0.38, cy + 0.15, 0], [cx + 0.38, cy + 0.15, 0],
                   stroke_color=WHITE, stroke_width=3.5))
        # Legs
        g.add(Line([cx, cy - 0.22, 0], [cx - 0.28, cy - 0.72, 0],
                   stroke_color=WHITE, stroke_width=3.5))
        g.add(Line([cx, cy - 0.22, 0], [cx + 0.28, cy - 0.72, 0],
                   stroke_color=WHITE, stroke_width=3.5))
        return g

    def _build_arrow(self, start, end, label: str = "") -> VGroup:
        g = VGroup()
        arr = Arrow(np.array(start), np.array(end),
                    stroke_color=WHITE, stroke_width=4, buff=0,
                    max_tip_length_to_length_ratio=0.18)
        g.add(arr)
        if label:
            lbl = Text(label, font="Arial", font_size=28, color=WHITE)
            lbl.move_to(np.array([
                (start[0] + end[0]) / 2,
                start[1] + 0.32,
                0
            ]))
            g.add(lbl)
        return g

    def _build_chaos_arrows(self, center) -> VGroup:
        g = VGroup()
        cx, cy, _ = center
        for angle, length in [(35, 0.55), (90, 0.45), (150, 0.50),
                               (-30, 0.48), (-110, 0.42)]:
            a = np.radians(angle)
            end = np.array([cx + np.cos(a) * length,
                             cy + np.sin(a) * length, 0])
            arr = Arrow(np.array([cx, cy, 0]), end,
                        stroke_color=WHITE, stroke_width=3,
                        buff=0, max_tip_length_to_length_ratio=0.22)
            g.add(arr)
        return g
