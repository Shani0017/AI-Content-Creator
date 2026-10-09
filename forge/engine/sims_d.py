"""Batch 2 - eater variants (18)."""
import math
from eater import *


def grad(h0, h1, s=0.7, v=1.0):
    return lambda u, vv, c, r, cols, rows: hsv(h0 + (h1 - h0) * (r / max(1, rows - 1)), s, v)


def gradx(h0, h1, s=0.7, v=1.0):
    return lambda u, vv, c, r, cols, rows: hsv(h0 + (h1 - h0) * (c / max(1, cols - 1)), s, v)


class HeartBreaker(Eater):
    TITLE, SUB = "HEART BREAKER", "BALLS BREAK THE HEART  -  EVERY BREAK CLONES"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 101, (255, 110, 160), "marimba", 262.0, (16, 6, 12)
    COUNTER = "HEART BROKEN"
    M0, MOTION, CLONE, CAP0, CAPK, NB = 260, "grav", 0.3, 3, 0.1, 3

    def layout(self):
        return mask_layout(m_heart, self.M0, self.REGION, grad(0.93, 1.02, 0.75, 1.0))


class PyramidSmash(Eater):
    TITLE, SUB = "PYRAMID SMASH", "A CANNON SIEGE  -  STONE BY STONE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 102, (255, 200, 90), "pluck", 196.0, (14, 10, 6)
    COUNTER = "PYRAMID DESTROYED"
    M0, MOTION, SPAWN, SPEED, BR = 300, "cannon", 2.4, 820, 8

    def layout(self):
        return mask_layout(m_pyramid, self.M0, (110, 470, 970, 1150), grad(0.09, 0.13, 0.65, 1.0))


class DiamondMine(Eater):
    TITLE, SUB = "DIAMOND MINE", "BOUNCING BALLS CRACK THE GEM"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 103, (120, 230, 255), "glass", 294.0, (6, 10, 18)
    COUNTER = "GEM MINED"
    M0, MOTION, SPEED, CLONE, NB, CAP0, CAPK = 320, "bounce", 520, 0.12, 4, 4, 0.08

    def layout(self):
        return mask_layout(m_diamond, self.M0, (100, 520, 980, 1400), gradx(0.5, 0.78, 0.65, 1.0))


class RainbowArcs(Eater):
    TITLE, SUB = "RAINBOW ARCS", "BOUNCE UP THROUGH SEVEN COLOURS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 104, (255, 160, 90), "marimba", 262.0, (8, 8, 18)
    COUNTER = "RAINBOW BROKEN"
    M0, MOTION, CLONE, NB = 360, "grav", 0.25, 3
    SCALE = MAJOR

    def layout(self):
        out = []
        n = self.M0
        radii = [150 + 52 * k for k in range(7)]
        tot = sum(radii)
        for k, R in enumerate(radii):
            cnt = max(8, int(n * R / tot))
            for i in range(cnt):
                a = math.pi + math.pi * (i + 0.5) / cnt
                out.append(circ_el(540 + R * math.cos(a), 1130 + R * math.sin(a), 11, hsv(k / 7 * 0.85), k / 7))
        return out


class CheckerChomp(Eater):
    TITLE, SUB = "CHECKER CHOMP", "ONE BALL  -  IT GROWS WITH EVERY SQUARE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 105, (255, 255, 255), "click", 330.0, (10, 10, 14)
    COUNTER = "BOARD CLEARED"
    M0, MOTION, SPEED, NB, GROW, BR, SOLID = 300, "bounce", 520, 1, 2.0, 10, False

    def layout(self):
        def col(u, v, c, r, cols, rows):
            return (235, 235, 240) if (c + r) % 4 == 0 else (200, 60, 70)
        return mask_layout(m_checker, self.M0, (90, 480, 990, 1380), col)


class BubblePack(Eater):
    TITLE, SUB = "BUBBLE PACK", "FALLING BALLS  -  POP EVERY BUBBLE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 106, (150, 255, 230), "pop", 262.0, (6, 14, 18)
    COUNTER = "BUBBLES POPPED"
    M0, MOTION, CLONE, NB = 120, "grav", 0.3, 3

    def layout(self):
        return scatter_layout(self.rng, self.M0, self.REGION, 16, 42, lambda x, y: hsv(0.45 + 0.3 * x + 0.1 * y, 0.5, 1.0))


class CometEater(Eater):
    TITLE, SUB = "COMET", "A FAST COMET EATS THE STARS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 107, (190, 170, 255), "glass", 330.0, (6, 6, 16)
    COUNTER = "STARS EATEN"
    M0, MOTION, SOLID, SPEED, NB, GROW, BR, TURN = 520, "home", False, 640, 1, 1.5, 9, 3.0

    def layout(self):
        return scatter_layout(self.rng, self.M0, (90, 470, 990, 1640), 5, 8, lambda x, y: hsv(0.55 + 0.35 * x, 0.35, 1.0))


class AsmrLetters(Eater):
    TITLE, SUB = "ASMR LETTERS", "BALLS ERASE THE WORD"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 108, (255, 120, 200), "marimba", 262.0, (12, 6, 16)
    COUNTER = "WORD ERASED"
    M0, MOTION, SPEED, CLONE, NB, CAP0, CAPK = 450, "bounce", 520, 0.2, 3, 3, 0.1

    def layout(self):
        return mask_layout(m_text("ASMR"), self.M0, (80, 560, 1000, 1160), gradx(0.0, 0.85, 0.7, 1.0))


class Dartboard(Eater):
    TITLE, SUB = "DARTBOARD", "BALLS RAIN DOWN ON THE BOARD"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 109, (255, 90, 90), "click", 392.0, (10, 10, 12)
    COUNTER = "BOARD CLEARED"
    M0, MOTION, SPAWN, CAPMAX, GRAV = 360, "rain", 2.0, 40, 900

    def layout(self):
        def col(t, f):
            return (210, 50, 50) if int(f * 20) % 2 == 0 else (60, 160, 90) if t > 0.15 else (240, 230, 200)
        return ring_layout(self.M0, 540, 1050, 60, 430, col, nrings=9)


class HoneycombRain(Eater):
    TITLE, SUB = "HONEYCOMB RAIN", "BALLS TUMBLE THROUGH A HIVE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 110, (255, 190, 60), "glass", 247.0, (16, 11, 4)
    COUNTER = "HIVE CLEARED"
    M0, MOTION, SPAWN, CAPMAX, GRAV = 400, "rain", 2.0, 40, 900

    def layout(self):
        out = []
        n = int(math.sqrt(self.M0 * 1.3))
        sp = 880 / n
        rows = int(self.M0 / n) + 1
        for r in range(rows):
            for c in range(n):
                x = 100 + c * sp + (sp / 2 if r % 2 else 0)
                y = 560 + r * sp * 0.87 * (1.0 if rows * sp * 0.87 < 1000 else 1000 / (rows * sp * 0.87))
                if x < 1000 and len(out) < self.M0:
                    out.append(circ_el(x, y, sp * 0.32, hsv(0.1 + 0.04 * (r / rows), 0.8, 1.0), c / n))
        return out


class WaveBricks(Eater):
    TITLE, SUB = "WAVE BRICKS", "RIDE THE WAVE  -  BREAK THE WAVE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 111, (90, 220, 255), "pluck", 294.0, (6, 10, 16)
    COUNTER = "WAVE BROKEN"
    M0, MOTION, CLONE, NB = 300, "grav", 0.3, 3

    def layout(self):
        return mask_layout(m_wave, self.M0, (80, 470, 1000, 1000), gradx(0.5, 0.9, 0.7, 1.0))


class PianoSmash(Eater):
    TITLE, SUB = "PIANO SMASH", "EVERY KEY PLAYS A NOTE WHEN IT BREAKS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 112, (255, 240, 200), "bell", 220.0, (8, 8, 12)
    COUNTER = "KEYS SMASHED"
    M0, MOTION, SPAWN, SPEED, BR = 300, "cannon", 2.4, 820, 8
    SCALE = MAJOR

    def layout(self):
        cols = 14
        rows = max(3, self.M0 // cols)
        cw = 880 / cols
        ch = 620 / rows
        out = []
        for c in range(cols):
            for r in range(rows):
                out.append(rect_el(100 + c * cw + 1, 480 + r * ch + 1, cw - 2, ch - 2, hsv(c / cols * 0.85, 0.6, 1.0 - 0.3 * (r / rows)), (c + 0.5) / cols))
        return out


class SpiralGalaxy(Eater):
    TITLE, SUB = "SPIRAL GALAXY", "ORBITING BALLS DEVOUR THE ARMS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 113, (190, 150, 255), "glass", 262.0, (6, 4, 14)
    COUNTER = "GALAXY EATEN"
    M0, MOTION, ARENA, RAD, CLONE, NB, CAP0, CAPK = 450, "orbit", "circle", 520, 0.12, 4, 4, 0.1

    def layout(self):
        return spiral_layout(self.M0, 540, 1050, 440, lambda t, f: hsv(0.7 - 0.35 * t, 0.6, 1.0), arms=3)


class TargetRings(Eater):
    TITLE, SUB = "TARGET RINGS", "BOUNCING INSIDE THE CIRCLE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 114, (255, 120, 90), "marimba", 247.0, (14, 8, 6)
    COUNTER = "RINGS CLEARED"
    M0, MOTION, ARENA, RAD, SPEED, CLONE, NB = 380, "bounce", "circle", 520, 480, 0.15, 3

    def layout(self):
        return ring_layout(self.M0, 540, 1050, 90, 470, lambda t, f: hsv(0.02 + 0.12 * t, 0.8, 1.0), nrings=8)


class ZigzagLanes(Eater):
    TITLE, SUB = "ZIGZAG LANES", "SIX BALLS  -  ONE LIGHTNING ROAD"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 115, (120, 255, 160), "pluck", 330.0, (6, 14, 10)
    COUNTER = "ZIGZAG CLEARED"
    M0, MOTION, NB, CLONE = 340, "grav", 6, 0.0

    def layout(self):
        return mask_layout(m_zigzag, self.M0, (80, 470, 1000, 1050), gradx(0.3, 0.55, 0.75, 1.0))


class SmileyEater(Eater):
    TITLE, SUB = "SMILEY", "BALLS ERASE THE SMILE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 116, (255, 220, 70), "pop", 262.0, (14, 12, 4)
    COUNTER = "SMILE ERASED"
    M0, MOTION, SPEED, CLONE, NB = 360, "bounce", 500, 0.15, 3

    def layout(self):
        return mask_layout(m_smiley, self.M0, (110, 520, 970, 1380), lambda u, v, c, r, cols, rows: (255, 220, 60) if math.hypot(u, v) > 0.7 else (60, 40, 20))


class TreasureGrid(Eater):
    TITLE, SUB = "TREASURE", "FALLING BALLS  -  COLLECT COINS AND GEMS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 117, (255, 215, 90), "bell", 330.0, (12, 10, 6)
    COUNTER = "TREASURE FOUND"
    M0, MOTION, CLONE, NB = 220, "grav", 0.2, 3
    SCALE = MAJOR

    def layout(self):
        def col(x, y):
            return (255, 205, 60)
        out = scatter_layout(self.rng, self.M0, self.REGION, 10, 15, col)
        for e in out[::9]:
            e[2] = 19
            e[5] = (90, 230, 255)
            e[7] = 0.9
        return out


class LightningBolt(Eater):
    TITLE, SUB = "LIGHTNING", "A CANNON SHATTERS THE BOLT"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 118, (255, 240, 90), "click", 392.0, (8, 8, 18)
    COUNTER = "BOLT SHATTERED"
    M0, MOTION, SPAWN, SPEED, BR = 320, "cannon", 2.4, 820, 8

    def layout(self):
        return mask_layout(m_bolt, self.M0, (160, 470, 920, 1250), lambda u, v, c, r, cols, rows: hsv(0.14 + 0.03 * (r / rows), 0.55 + 0.3 * (r / rows), 1.0))


BATCH_D = [HeartBreaker, PyramidSmash, DiamondMine, RainbowArcs, CheckerChomp, BubblePack, CometEater, AsmrLetters, Dartboard,
           HoneycombRain, WaveBricks, PianoSmash, SpiralGalaxy, TargetRings, ZigzagLanes, SmileyEater, TreasureGrid, LightningBolt]
