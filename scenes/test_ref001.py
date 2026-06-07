"""
Test scene — reproduction visuelle de ref_001 (Wild Horse Effect).
Valide le style neon, le draw-on, les labels, l'impact burst.
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


class WildHorseEffectScene(NeonScene):
    """
    Reproduction of the snake-crawling-into-saw scene from ref_001.
    Scene sequence:
      1. Title appears
      2. Ground terrain drawn
      3. Saw drawn at right
      4. Snake path drawn from left (word: 'snake')
      5. Snake moves toward saw (words: 'while', 'crawling')
      6. Snake reaches saw (word: 'accidentally')
      7. Impact burst + collision (word: 'cut', 'saw')
      8. Hold on scene
    """

    def construct(self):
        # ── Title ─────────────────────────────────────────────────────────
        title = self.title_text("Not Everything Is Against You..")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.6)
        self.wait(0.3)

        # ── Ground / terrain lines ─────────────────────────────────────────
        # Already added by setup() via _draw_panel_bg()
        # Add a primary ground line across the panel
        ground_y = PANEL_CENTER_Y - PANEL_UNIT_H * 0.28
        ground_line = self.neon_line(
            [-PANEL_UNIT_W * 0.48, ground_y, 0],
            [PANEL_UNIT_W * 0.48, ground_y, 0],
            stroke_width=1.5,
            opacity=0.4
        )
        self.play(Create(ground_line), run_time=0.4)

        # ── Saw (trap) at right side ─────────────────────────────────────
        saw_x = PANEL_UNIT_W * 0.18
        saw_y = ground_y
        saw = self._draw_saw(saw_x, saw_y)
        self.play(Create(saw), run_time=1.0)
        self.wait(0.2)

        # ── Snake body (initial position, left side) ──────────────────────
        snake_start_x = -PANEL_UNIT_W * 0.38
        snake = self._draw_snake(snake_start_x, ground_y)

        word_y = PANEL_CENTER_Y - PANEL_UNIT_H * 0.5 - 0.5
        label_pos = [0, word_y, 0]

        self.draw_in(snake, run_time=1.2)

        # Word: snake
        label_snake = self.word_label("snake", label_pos, font_size=38)
        self.play(FadeIn(label_snake, shift=UP * 0.1), run_time=0.15)
        self.wait(0.5)
        self.play(FadeOut(label_snake), run_time=0.2)

        # ── Animate snake crawling toward saw ─────────────────────────────
        # Word: while
        label_while = self.word_label("while", label_pos, font_size=38)
        self.play(FadeIn(label_while, shift=UP * 0.1), run_time=0.15)
        self.play(
            snake.animate.shift(RIGHT * 0.8),
            run_time=0.8, rate_func=linear
        )
        self.play(FadeOut(label_while), run_time=0.15)

        # Word: crawling
        label_crawl = self.word_label("crawling", label_pos, font_size=38)
        self.play(FadeIn(label_crawl, shift=UP * 0.1), run_time=0.15)
        self.play(
            snake.animate.shift(RIGHT * 0.9),
            run_time=1.0, rate_func=linear
        )
        self.play(FadeOut(label_crawl), run_time=0.15)

        # Word: accidentally
        label_acc = self.word_label("accidentally", label_pos, font_size=38)
        self.play(FadeIn(label_acc, shift=UP * 0.1), run_time=0.15)
        self.play(
            snake.animate.shift(RIGHT * 0.5),
            run_time=0.6, rate_func=linear
        )
        self.play(FadeOut(label_acc), run_time=0.15)

        # Word: cut
        label_cut = self.word_label("cut", label_pos, font_size=38)
        self.play(FadeIn(label_cut, shift=UP * 0.1), run_time=0.15)

        # ── Impact burst at saw contact point ─────────────────────────────
        impact_pos = [saw_x - 0.3, saw_y, 0]
        self.flash_impact(impact_pos, run_time=0.5)

        self.play(FadeOut(label_cut), run_time=0.15)

        # Word: saw
        label_saw = self.word_label("saw", label_pos, font_size=38)
        self.play(FadeIn(label_saw, shift=UP * 0.1), run_time=0.15)
        self.wait(0.8)
        self.play(FadeOut(label_saw), run_time=0.2)

        # ── Word: the (transition to next beat) ───────────────────────────
        label_the = self.word_label("the", label_pos, font_size=38)
        self.play(FadeIn(label_the, shift=UP * 0.1), run_time=0.15)
        self.wait(0.4)
        self.play(FadeOut(label_the), run_time=0.15)

        self.wait(1.0)

    def _draw_saw(self, x: float, y: float) -> VMobject:
        """Draw a saw/trap shape — jagged teeth on a rectangle body."""
        group = VGroup()

        # Body rectangle
        body = Rectangle(width=1.1, height=0.55)
        body.move_to([x + 0.2, y + 0.12, 0])
        body.set_stroke(color=WHITE, width=4)
        body.set_fill(opacity=0)
        group.add(body)

        # Jagged teeth on top
        teeth_points = []
        n_teeth = 8
        x_start = x - 0.25
        x_end = x + 0.65
        tooth_spacing = (x_end - x_start) / n_teeth
        base_y = y + 0.38

        for i in range(n_teeth):
            tx = x_start + i * tooth_spacing
            teeth_points.append([tx, base_y, 0])
            teeth_points.append([tx + tooth_spacing * 0.5, base_y + 0.22, 0])

        teeth_points.append([x_end, base_y, 0])

        teeth = VMobject()
        teeth.set_points_as_corners([np.array(p) for p in teeth_points])
        teeth.set_stroke(color=WHITE, width=3.5)
        group.add(teeth)

        # Small circle detail (screw/pivot)
        screw = self.neon_circle([x + 0.55, y + 0.12, 0], radius=0.12)
        screw.set_stroke(width=3)
        group.add(screw)

        return group

    def _draw_snake(self, start_x: float, y: float) -> VMobject:
        """Draw a snake as a sinuous path with a small head circle."""
        group = VGroup()

        # Sinuous body path
        body_points = []
        length = 1.6
        segments = 20
        for i in range(segments + 1):
            t = i / segments
            px = start_x + t * length
            py = y + np.sin(t * np.pi * 2.5) * 0.12
            body_points.append([px, py, 0])

        body = VMobject()
        body.set_points_smoothly([np.array(p) for p in body_points])
        body.set_stroke(color=WHITE, width=5)
        group.add(body)

        # Head
        head = self.neon_circle(
            [start_x + length + 0.12, y, 0],
            radius=0.10
        )
        head.set_stroke(width=4)
        group.add(head)

        return group
