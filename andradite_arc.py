#!/usr/bin/env python3
"""Andradite Arc — neon curved-rail shard catcher for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/ANDRADITE_ARC_ElbowOS.mp4")
TITLE, HANDLE = "ANDRADITE ARC", "x.com/ElbowOS"
PLUM, WINE = (18, 4, 16), (48, 10, 28)
GOLD, AMBER = (255, 186, 64), (255, 118, 36)
LIME, CORAL, ICE = (176, 255, 78), (255, 78, 108), (90, 230, 255)
TEAL, WHITE = (36, 214, 176), (255, 246, 236)
CX, CY, RR = 540, 1620, 480

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.lg = pygame.font.SysFont("dejavusans", 68, bold=True)
        self.md = pygame.font.SysFont("dejavusans", 40, bold=True)
        self.sm = pygame.font.SysFont("dejavusans", 30, bold=True)
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.ang = 0.0
        self.shards, self.bolts, self.sparks = [], [], []
        self.score, self.lives, self.cool, self.t, self.flash = 0, 3, 0, 0, 0
        self.spawn = 8
        random.seed(11)

    def spawn_shard(self):
        self.shards.append({
            "x": float(random.randint(160, 920)), "y": -30.0,
            "vx": random.uniform(-2.4, 2.4), "vy": random.uniform(8.0, 13.0),
            "r": random.randint(24, 38), "a": random.random() * 6.2,
            "spin": random.uniform(-0.18, 0.18),
            "c": random.choice([LIME, CORAL, ICE, GOLD, AMBER]),
        })

    def player_pos(self):
        a = max(-1.05, min(1.05, self.ang))
        return CX + math.sin(a) * RR, CY - math.cos(a) * RR, a

    def burst(self, x, y, c):
        for _ in range(12):
            ang = random.random() * math.tau
            sp = random.uniform(2.5, 9)
            self.sparks.append({
                "x": x, "y": y, "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp,
                "life": random.randint(10, 20), "c": c,
            })

    def step(self, left, right, fire):
        self.t += 1
        self.ang = max(-1.05, min(1.05, self.ang + (0.05 if right else 0) - (0.05 if left else 0)))
        self.cool = max(0, self.cool - 1)
        self.flash = max(0, self.flash - 1)
        self.spawn -= 1
        if self.spawn <= 0 and len(self.shards) < 9:
            self.spawn_shard()
            self.spawn = random.randint(10, 18)
        px, py, a = self.player_pos()
        if fire and self.cool == 0:
            dx, dy = math.sin(a), -math.cos(a)
            self.bolts.append({"x": px, "y": py - 20, "vx": dx * 24, "vy": dy * 24, "life": 26})
            self.cool = 8
        rings = ((540, 680, 160), (250, 980, 88), (830, 980, 88))
        kept = []
        for s in self.shards:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["a"] += s["spin"]
            if s["x"] < 70 or s["x"] > W - 70:
                s["vx"] *= -1
                s["x"] = max(70, min(W - 70, s["x"]))
            for bx, by, br in rings:
                dx, dy = s["x"] - bx, s["y"] - by
                d = math.hypot(dx, dy) or 1
                if d < br + s["r"]:
                    nx, ny = dx / d, dy / d
                    s["x"], s["y"] = bx + nx * (br + s["r"] + 2), by + ny * (br + s["r"] + 2)
                    dot = s["vx"] * nx + s["vy"] * ny
                    s["vx"] -= 1.8 * dot * nx
                    s["vy"] -= 1.8 * dot * ny
                    s["vy"] = max(6.5, abs(s["vy"]))
            if math.hypot(s["x"] - px, s["y"] - py) < s["r"] + 42:
                self.score += 120
                self.burst(s["x"], s["y"], s["c"])
                continue
            if s["y"] > 1710:
                self.lives = max(0, self.lives - 1)
                self.flash = 8
                self.burst(s["x"], 1710, CORAL)
                continue
            kept.append(s)
        self.shards = kept
        nb = []
        for b in self.bolts:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            b["life"] -= 1
            hit = None
            for s in self.shards:
                if math.hypot(s["x"] - b["x"], s["y"] - b["y"]) < s["r"] + 18:
                    hit = s
                    break
            if hit:
                self.score += 180
                self.burst(hit["x"], hit["y"], GOLD)
                self.shards.remove(hit)
                continue
            if b["life"] > 0 and 0 < b["x"] < W and 40 < b["y"] < H:
                nb.append(b)
        self.bolts = nb
        self.sparks = [p for p in self.sparks if p.update({"life": p["life"] - 1, "x": p["x"] + p["vx"], "y": p["y"] + p["vy"], "vy": p["vy"] + 0.28}) or p["life"] > 0]

    def auto(self):
        px, py, a = self.player_pos()
        best, bd = None, 1e9
        for s in self.shards:
            if 180 < s["y"] < 1480:
                d = abs(s["x"] - px) + s["y"] * 0.15
                if d < bd:
                    best, bd = s, d
        left = right = fire = False
        if best:
            target = math.asin(max(-1, min(1, (best["x"] - CX) / RR)))
            left, right = target < self.ang - 0.03, target > self.ang + 0.03
            fire = abs(target - self.ang) < 0.14 and best["y"] > 280
        return left, right, fire

    def diamond(self, x, y, r, a, c):
        pts = [(x + math.cos(a + k * math.pi / 2) * r, y + math.sin(a + k * math.pi / 2) * r * 1.35) for k in range(4)]
        pygame.draw.polygon(self.screen, c, pts)
        pygame.draw.polygon(self.screen, WHITE, pts, 3)

    def draw(self):
        scr = self.screen
        scr.fill(PLUM)
        for i in range(16):
            pygame.draw.rect(scr, (24 + i * 2, 6, 22 + i), (0, i * 120, W, 120))
        rng = random.Random(4)
        for _ in range(70):
            pygame.draw.circle(scr, (110, 48, 72), (rng.randint(0, W), rng.randint(40, 1500)), 2)
        spin = self.t * 0.04
        for bx, by, br in ((540, 680, 160), (250, 980, 88), (830, 980, 88)):
            pygame.draw.circle(scr, (90, 28, 54), (bx, by), br, 10)
            pygame.draw.circle(scr, (255, 150, 70), (bx, by), br - 16, 3)
            for k in range(5):
                aa = spin + k * math.tau / 5
                pygame.draw.circle(scr, GOLD, (int(bx + math.cos(aa) * br), int(by + math.sin(aa) * br)), 9)
        pts = [(CX + math.sin(-1.15 + i * 2.3 / 36) * RR, CY - math.cos(-1.15 + i * 2.3 / 36) * RR) for i in range(37)]
        pygame.draw.lines(scr, (110, 42, 18), False, pts, 22)
        pygame.draw.lines(scr, GOLD, False, pts, 6)
        pygame.draw.rect(scr, (62, 14, 20), (0, 1748, W, 172))
        pygame.draw.rect(scr, AMBER if self.flash else (190, 54, 36), (0, 1748, W, 10))
        for s in self.shards:
            self.diamond(s["x"], s["y"], s["r"], s["a"], s["c"])
        for b in self.bolts:
            pygame.draw.line(scr, GOLD, (b["x"] - b["vx"], b["y"] - b["vy"]), (b["x"], b["y"]), 8)
            pygame.draw.circle(scr, WHITE, (int(b["x"]), int(b["y"])), 9)
        for p in self.sparks:
            pygame.draw.circle(scr, p["c"], (int(p["x"]), int(p["y"])), 4)
        px, py, a = self.player_pos()
        pygame.draw.circle(scr, TEAL, (int(px), int(py)), 40)
        pygame.draw.circle(scr, WHITE, (int(px), int(py)), 20)
        pygame.draw.circle(scr, GOLD, (int(px), int(py)), 44, 4)
        tip = (px + math.sin(a) * 54, py - math.cos(a) * 54)
        pygame.draw.circle(scr, ICE, (int(tip[0]), int(tip[1])), 8)
        title = self.lg.render(TITLE, True, GOLD)
        scr.blit(title, (W // 2 - title.get_width() // 2, 46))
        scr.blit(self.md.render(f"SCORE  {self.score}", True, WHITE), (56, 150))
        scr.blit(self.md.render("LIVES  " + "●" * self.lives, True, CORAL), (56, 208))
        sub = self.sm.render("SLIDE THE ARC   ·   FIRE THE BOLT", True, (230, 186, 160))
        scr.blit(sub, (W // 2 - sub.get_width() // 2, 1688))
        handle = self.sm.render(HANDLE, True, ICE)
        scr.blit(handle, (W // 2 - handle.get_width() // 2, 1844))

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
               "-preset", "veryfast", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                left, right, fire = self.auto()
                self.step(left, right, fire)
                self.draw()
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT)

    def play_interactive(self):
        while True:
            fire = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE,):
                    return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    self.reset()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    fire = True
            keys = pygame.key.get_pressed()
            self.step(keys[pygame.K_LEFT] or keys[pygame.K_a], keys[pygame.K_RIGHT] or keys[pygame.K_d], fire or keys[pygame.K_SPACE])
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

def main():
    g = Game()
    (g.play_interactive() if PLAY and not RECORD else g.record())
    pygame.quit()

if __name__ == "__main__":
    main()
