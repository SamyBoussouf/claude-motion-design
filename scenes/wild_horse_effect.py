"""
Wild Horse Effect — animation continue ~45s.
Style: chalk sketch sur fond noir, glow rose chaud, serpent dashed, scie à main réelle.

Scènes enchaînées sans coupure:
  S1 (0-13s)  : terrain + scie à main + serpent rampe depuis gauche
  S2 (13-26s) : serpent se love autour de la scie pour combattre
  S3 (26-34s) : le serpent s'épuise et meurt
  S4 (34-45s) : "The Wild Horse Effect" → "Calm is power."
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from scenes.base import (
    NeonScene, PANEL_CENTER_Y, PANEL_UNIT_W, PANEL_UNIT_H,
    MANIM_H, STROKE_WIDTH
)

config.pixel_width  = 1080
config.pixel_height = 1920
config.frame_rate   = 30
config.background_color = "#000000"
config.frame_width  = 4.5
config.frame_height = 8.0

# Layout — positions relatives à la référence
GROUND_Y   = PANEL_CENTER_Y - PANEL_UNIT_H * 0.08   # ligne de sol
SAW_CX     = PANEL_UNIT_W  * 0.28                    # centre scie (tiers droit)
SNAKE_X0   = -PANEL_UNIT_W * 0.47                    # départ queue gauche
SNAKE_LEN  = PANEL_UNIT_W  * 0.40                    # longueur corps


class WildHorseEffect(NeonScene):

    def construct(self):

        # ── Titre — plain bold blanc, pas de glow ─────────────────────────
        title = self.title_text("Not Everything Is Against You..")
        self.play(FadeIn(title), run_time=0.6)
        self.wait(0.4)

        # ── S1a : scie à main ────────────────────────────────────────────
        saw = self._handsaw(SAW_CX, GROUND_Y)
        self.play(Create(saw), run_time=1.4)
        self.wait(0.3)

        # ── S1b : serpent dashed rampe depuis la gauche ──────────────────
        snake = self._snake_dashed(SNAKE_X0, GROUND_Y)
        self.play(Create(snake), run_time=1.6, rate_func=linear)

        # progression en deux temps
        self.play(snake.animate.shift(RIGHT * SNAKE_LEN * 0.50),
                  run_time=2.0, rate_func=linear)
        self.play(snake.animate.shift(RIGHT * SNAKE_LEN * 0.55),
                  run_time=1.8, rate_func=rush_into)

        # ── S1c : contact + étincelles ───────────────────────────────────
        cut_pt = [SAW_CX - 0.18, GROUND_Y + 0.10, 0]
        self.flash_impact(cut_pt, run_time=0.5)
        sparks = self._sparks(cut_pt, n=8, length=0.24)
        self.play(Create(sparks), run_time=0.2)
        self.play(FadeOut(sparks), run_time=0.3)
        self.wait(0.5)

        # ── S2 : le serpent se love ──────────────────────────────────────
        coiled = self._snake_coiled(SAW_CX, GROUND_Y, tightness=1.0)
        self.play(Transform(snake, coiled), run_time=2.2, rate_func=smooth)
        self.wait(0.6)

        tighter = self._snake_coiled(SAW_CX, GROUND_Y, tightness=0.76)
        self.play(Transform(snake, tighter), run_time=1.8, rate_func=smooth)

        dmg = self._damage_lines(SAW_CX, GROUND_Y)
        self.play(Create(dmg), run_time=0.9)
        self.play(dmg.animate.scale(1.45).set_stroke(opacity=0.50), run_time=1.2)
        self.wait(0.3)

        # ── S3 : mort / épuisement ───────────────────────────────────────
        limp = self._snake_limp(SAW_CX, GROUND_Y)
        self.play(Transform(snake, limp), FadeOut(dmg),
                  run_time=1.8, rate_func=smooth)
        self.wait(0.3)
        self.play(snake.animate.set_stroke(opacity=0.15), run_time=1.4)

        # scie inchangée — il n'a jamais été menacé
        hl = saw.copy().set_stroke(opacity=1.0)
        self.play(GrowFromCenter(hl), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(hl), run_time=0.4)
        self.play(FadeOut(snake), FadeOut(saw), run_time=0.8)
        self.wait(0.15)

        # ── S4a : label ──────────────────────────────────────────────────
        lbl = Text("The Wild Horse Effect",
                   font="Arial", font_size=46, color=WHITE, weight=BOLD)
        lbl.move_to([0, PANEL_CENTER_Y + 0.30, 0])
        uline = Line(lbl.get_left() + DOWN * 0.26,
                     lbl.get_right() + DOWN * 0.26,
                     stroke_color=WHITE, stroke_width=1.6, stroke_opacity=0.45)
        self.play(Write(lbl), run_time=1.2)
        self.play(Create(uline), run_time=0.4)
        self.wait(1.2)
        self.play(FadeOut(lbl), FadeOut(uline), run_time=0.6)

        # ── S4b : conclusion ─────────────────────────────────────────────
        calm = Text("Calm is power.", font="Arial",
                    font_size=58, color=WHITE, weight=BOLD)
        calm.move_to([0, PANEL_CENTER_Y, 0])
        self.play(Write(calm), run_time=1.2)
        self.wait(2.5)
        self.play(FadeOut(calm), FadeOut(title), run_time=0.9)
        self.wait(0.5)

    # ── SCIE À MAIN (handsaw) ─────────────────────────────────────────────

    def _handsaw(self, cx: float, y: float) -> VGroup:
        """
        Scie à main fidèle à ref_001, taille réduite pour rester dans le panel.
        Corps trapézoïdal + dents denses + hachures + poignée en D.
        """
        g = VGroup()

        # Dimensions réduites — scie occupe ~22% de la largeur du panel
        W  = PANEL_UNIT_W * 0.22    # ~0.84u largeur lame
        HL = PANEL_UNIT_H * 0.32    # hauteur côté manche
        HR = PANEL_UNIT_H * 0.14    # hauteur côté pointe

        x0 = cx - W * 0.58          # bord gauche (manche)
        x1 = cx + W * 0.42          # bord droit  (pointe)
        yB = y

        # 1. Corps trapézoïdal
        corners = [
            np.array([x0, yB,      0]),
            np.array([x1, yB,      0]),
            np.array([x1, yB + HR, 0]),
            np.array([x0, yB + HL, 0]),
            np.array([x0, yB,      0]),
        ]
        blade = VMobject().set_points_as_corners(corners)
        blade.set_stroke(WHITE, width=4.0).set_fill(opacity=0)
        g.add(blade)

        # 2. Dents denses sur le bord supérieur (petites, nombreuses comme la ref)
        n_teeth = 20
        teeth_pts = [np.array([x0, yB + HL, 0])]
        for i in range(n_teeth):
            t   = i / n_teeth
            t1  = (i + 1) / n_teeth
            bx  = x0 + t  * (x1 - x0)
            ex  = x0 + t1 * (x1 - x0)
            mid = (bx + ex) / 2
            bh  = HL + t * (HR - HL)          # hauteur base interpolée
            th  = 0.050 - t * 0.018            # dents décroissantes
            teeth_pts.append(np.array([mid, yB + bh + th, 0]))
            teeth_pts.append(np.array([ex,  yB + bh,      0]))
        teeth = VMobject().set_points_as_corners(teeth_pts)
        teeth.set_stroke(WHITE, width=3.0)
        g.add(teeth)

        # 3. Hachures diagonales — volume 3D
        n_hatch = 6
        for i in range(n_hatch):
            t       = (i + 0.5) / n_hatch
            hx      = x0 + t * (x1 - x0)
            h_local = HL + t * (HR - HL)
            g.add(Line(
                np.array([hx + 0.030, yB + 0.02,          0]),
                np.array([hx - 0.030, yB + h_local * 0.86, 0]),
                stroke_color=WHITE, stroke_width=1.3, stroke_opacity=0.35
            ))

        # 4. Poignée en D — proportionnée à la hauteur HR du côté pointe
        ph  = HR * 1.30              # hauteur poignée
        hcx = x1 + ph * 0.52        # centre en X de l'arc
        hcy = yB + HR * 0.50        # centre en Y

        handle_arc = Arc(
            radius=ph * 0.50,
            start_angle=-PI / 2,
            angle=PI,
            arc_center=np.array([hcx, hcy, 0])
        )
        handle_arc.set_stroke(WHITE, width=3.5)
        g.add(handle_arc)

        g.add(Line(np.array([x1, yB,      0]),
                   np.array([hcx, hcy - ph * 0.50, 0]),
                   stroke_color=WHITE, stroke_width=3.2))
        g.add(Line(np.array([x1, yB + HR, 0]),
                   np.array([hcx, hcy + ph * 0.50, 0]),
                   stroke_color=WHITE, stroke_width=3.2))

        # Ovale intérieur
        inner = Ellipse(width=ph * 0.50, height=ph * 0.40)
        inner.move_to([hcx + ph * 0.02, hcy, 0])
        inner.set_stroke(WHITE, width=2.0).set_fill(opacity=0)
        g.add(inner)

        return g

    # ── SERPENT DASHED (écailles) ─────────────────────────────────────────

    def _snake_dashed(self, start_x: float, y: float) -> VGroup:
        """
        Corps en tirets réguliers pour simuler les écailles comme dans ref_001.
        Courbe organique, pas parfaitement sinusoïdale.
        """
        g    = VGroup()
        segs = 40

        # Courbe organique (variation d'amplitude le long du corps)
        pts = []
        for i in range(segs + 1):
            t  = i / segs
            x  = start_x + t * SNAKE_LEN
            # amplitude qui diminue vers la tête (queue large, tête effilée)
            amp = 0.12 * (1.0 - t * 0.35)
            dy  = np.sin(t * TAU * 1.7 + 0.3) * amp
            pts.append(np.array([x, y + dy, 0]))

        # Chemin de base (non visible, sert de gabarit au dashed)
        base_path = VMobject()
        base_path.set_points_smoothly(pts)

        # Dashes — effet écailles comme dans la référence
        body_dashed = DashedVMobject(base_path, num_dashes=26, dashed_ratio=0.60)
        body_dashed.set_stroke(WHITE, width=5.5)
        g.add(body_dashed)

        # Tête : petit oval légèrement aplati
        head_pos = np.array([start_x + SNAKE_LEN + 0.11, y + 0.01, 0])
        head = Ellipse(width=0.19, height=0.14)
        head.move_to(head_pos)
        head.set_stroke(WHITE, width=4.5).set_fill(opacity=0)
        g.add(head)

        # Petite langue fourchue
        tongue_base = head_pos + np.array([0.095, 0, 0])
        g.add(Line(tongue_base,
                   tongue_base + np.array([0.07,  0.04, 0]),
                   stroke_color=WHITE, stroke_width=1.8, stroke_opacity=0.7))
        g.add(Line(tongue_base,
                   tongue_base + np.array([0.07, -0.04, 0]),
                   stroke_color=WHITE, stroke_width=1.8, stroke_opacity=0.7))

        return g

    # ── SERPENT LOVEE (coil) ─────────────────────────────────────────────

    def _snake_coiled(self, saw_cx: float, y: float, tightness: float = 1.0) -> VGroup:
        g  = VGroup()
        cx = saw_cx + 0.08
        cy = y + PANEL_UNIT_H * 0.16
        turns = 1.88 * tightness
        segs  = 90
        pts   = []
        for i in range(segs + 1):
            t     = i / segs
            angle = t * TAU * turns
            r     = 0.78 - t * 0.26 * tightness
            pts.append(np.array([
                cx + r * np.cos(angle),
                cy + r * np.sin(angle) * 0.50,
                0
            ]))
        base = VMobject()
        base.set_points_smoothly(pts)
        body = DashedVMobject(base, num_dashes=28, dashed_ratio=0.62)
        body.set_stroke(WHITE, width=5.5)
        g.add(body)
        head = Ellipse(width=0.19, height=0.14).move_to(pts[-1])
        head.set_stroke(WHITE, width=4.5).set_fill(opacity=0)
        g.add(head)
        return g

    # ── SERPENT FLASQUE (mort) ─────────────────────────────────────────────

    def _snake_limp(self, saw_cx: float, y: float) -> VGroup:
        g  = VGroup()
        cx = saw_cx + 0.06
        pts = [
            np.array([cx - PANEL_UNIT_W * 0.26, y - 0.09, 0]),
            np.array([cx - PANEL_UNIT_W * 0.12, y + 0.05, 0]),
            np.array([cx + 0.00,                y + 0.01, 0]),
            np.array([cx + PANEL_UNIT_W * 0.09, y + 0.06, 0]),
            np.array([cx + PANEL_UNIT_W * 0.18, y - 0.09, 0]),
        ]
        base = VMobject()
        base.set_points_smoothly(pts)
        body = DashedVMobject(base, num_dashes=20, dashed_ratio=0.58)
        body.set_stroke(WHITE, width=5.0)
        g.add(body)
        head = Ellipse(width=0.18, height=0.13)
        head.move_to(pts[-1] + np.array([0.10, -0.04, 0]))
        head.set_stroke(WHITE, width=4).set_fill(opacity=0)
        g.add(head)
        return g

    # ── UTILITAIRES ────────────────────────────────────────────────────────

    def _sparks(self, center, n: int = 8, length: float = 0.22) -> VGroup:
        g = VGroup()
        for i in range(n):
            a = (TAU / n) * i + TAU / (n * 2.3)
            d = np.array([np.cos(a), np.sin(a), 0])
            g.add(Line(
                np.array(center) + d * 0.04,
                np.array(center) + d * length,
                stroke_color=WHITE, stroke_width=2.8, stroke_opacity=0.92
            ))
        return g

    def _damage_lines(self, saw_cx: float, y: float) -> VGroup:
        g  = VGroup()
        cx = saw_cx + 0.08
        cy = y + PANEL_UNIT_H * 0.16
        for angle_deg in [10, 60, 115, 170, 225, 280, 335]:
            a = np.radians(angle_deg)
            d = np.array([np.cos(a), np.sin(a) * 0.52, 0])
            g.add(Line(
                np.array([cx, cy, 0]) + d * 0.44,
                np.array([cx, cy, 0]) + d * 0.78,
                stroke_color=WHITE, stroke_width=2.0, stroke_opacity=0.72
            ))
        return g
