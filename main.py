#!/usr/bin/env python3
"""
Simple Flappy Bird clone using Pygame.

Controls:
- Space or Left Mouse Button: flap / start / restart
"""

import pygame
import random
import json
import os
import sys

# Config
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.45
FLAP_STRENGTH = -9
PIPE_GAP = 150
PIPE_WIDTH = 60
PIPE_SPEED = 2.6
PIPE_INTERVAL_MS = 1400
GROUND_HEIGHT = 20
HS_FILE = "highscore.json"

# Colors
SKY_TOP = (155, 231, 255)
SKY_BOTTOM = (112, 197, 206)
PIPE_COLOR = (46, 204, 113)
PIPE_CAP = (30, 132, 73)
GROUND_COLOR = (222, 216, 149)
BIRD_COLOR = (255, 204, 0)
BEAK_COLOR = (255, 139, 0)
TEXT_COLOR = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird — Pygame")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont(None, 48)
font_med = pygame.font.SysFont(None, 28)
font_small = pygame.font.SysFont(None, 20)


def load_highscore():
    try:
        if os.path.exists(HS_FILE):
            with open(HS_FILE, "r") as f:
                data = json.load(f)
                return int(data.get("high", 0))
    except Exception:
        pass
    return 0


def save_highscore(score):
    try:
        with open(HS_FILE, "w") as f:
            json.dump({"high": int(score)}, f)
    except Exception:
        pass


class Bird:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT // 2
        self.w = 34
        self.h = 24
        self.vy = 0
        self.alive = True

    def flap(self):
        self.vy = FLAP_STRENGTH

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy
        # keep inside top
        if self.y - self.h/2 < 0:
            self.y = self.h/2
            self.vy = 0

    def get_rect(self):
        return pygame.Rect(int(self.x - self.w/2), int(self.y - self.h/2), self.w, self.h)

    def draw(self, surf):
        # draw bird as ellipse + beak
        rect = self.get_rect()
        pygame.draw.ellipse(surf, BIRD_COLOR, rect)
        # beak
        p1 = (int(self.x + self.w/2), int(self.y))
        p2 = (int(self.x + self.w/2 + 10), int(self.y - 6))
        p3 = (int(self.x + self.w/2 + 10), int(self.y + 6))
        pygame.draw.polygon(surf, BEAK_COLOR, (p1, p2, p3))


class Pipe:
    def __init__(self, x):
        self.x = x
        top = 80 + random.random() * (HEIGHT - 300)
        self.top = int(top)
        self.bottom = self.top + PIPE_GAP
        self.width = PIPE_WIDTH
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def offscreen(self):
        return self.x + self.width < -50

    def draw(self, surf):
        # top rect
        pygame.draw.rect(surf, PIPE_COLOR, (int(self.x), 0, self.width, int(self.top)))
        # bottom rect
        pygame.draw.rect(surf, PIPE_COLOR, (int(self.x), int(self.bottom), self.width, HEIGHT - int(self.bottom)))
        # caps
        pygame.draw.rect(surf, PIPE_CAP, (int(self.x)-2, int(self.top)-8, self.width+4, 8))
        pygame.draw.rect(surf, PIPE_CAP, (int(self.x)-2, int(self.bottom), self.width+4, 8))

    def collides(self, bird: Bird):
        br = bird.get_rect()
        # check collision with top pipe rect
        top_rect = pygame.Rect(int(self.x), 0, self.width, int(self.top))
        bottom_rect = pygame.Rect(int(self.x), int(self.bottom), self.width, HEIGHT - int(self.bottom))
        return br.colliderect(top_rect) or br.colliderect(bottom_rect)


def draw_background(surf):
    grad = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(SKY_TOP[0] * (1 - t) + SKY_BOTTOM[0] * t)
        g = int(SKY_TOP[1] * (1 - t) + SKY_BOTTOM[1] * t)
        b = int(SKY_TOP[2] * (1 - t) + SKY_BOTTOM[2] * t)
        pygame.draw.line(grad, (r, g, b), (0, y), (WIDTH, y))
    surf.blit(grad, (0, 0))


def main():
    highscore = load_highscore()
    bird = Bird()
    pipes = []
    score = 0
    last_pipe_time = pygame.time.get_ticks()
    state = "start"  # start | playing | gameover

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if event.key == pygame.K_SPACE:
                    if state == "start":
                        state = "playing"
                        bird.flap()
                        last_pipe_time = pygame.time.get_ticks()
                        pipes = []
                        score = 0
                    elif state == "playing":
                        bird.flap()
                    elif state == "gameover":
                        # restart
                        bird = Bird()
                        pipes = []
                        score = 0
                        state = "start"
                # other keys ignored
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "start":
                    state = "playing"
                    bird.flap()
                    last_pipe_time = pygame.time.get_ticks()
                    pipes = []
                    score = 0
                elif state == "playing":
                    bird.flap()
                elif state == "gameover":
                    bird = Bird()
                    pipes = []
                    score = 0
                    state = "start"

        # update
        if state == "playing":
            bird.update()
            # spawn pipes
            now = pygame.time.get_ticks()
            if now - last_pipe_time > PIPE_INTERVAL_MS:
                pipes.append(Pipe(WIDTH))
                last_pipe_time = now
            # update pipes
            for p in pipes:
                p.update()
                if not p.passed and p.x + p.width < bird.x:
                    score += 1
                    p.passed = True
                    if score > highscore:
                        highscore = score
                        save_highscore(highscore)
            pipes = [p for p in pipes if not p.offscreen()]

            # collisions
            # ground collision
            if bird.y + bird.h/2 >= HEIGHT - GROUND_HEIGHT:
                state = "gameover"
            for p in pipes:
                if p.collides(bird):
                    state = "gameover"

        # draw
        draw_background(screen)
        for p in pipes:
            p.draw(screen)
        # ground
        pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        bird.draw(screen)

        # HUD and overlays
        if state in ("playing", "gameover"):
            score_surf = font_large.render(str(score), True, TEXT_COLOR)
            screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 40))

        if state == "start":
            # overlay
            overlay_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay_surf.fill((0, 0, 0, 0))
            title = font_large.render("Flappy Bird", True, TEXT_COLOR)
            hint = font_med.render("Space / Click to flap and start", True, TEXT_COLOR)
            start_btn = font_med.render("Start", True, (255, 255, 255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 - 40))

            # draw Start button-like rect
            btn_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 - 10, 120, 36)
            pygame.draw.rect(screen, (255, 107, 107), btn_rect, border_radius=6)
            screen.blit(start_btn, (btn_rect.centerx - start_btn.get_width()//2, btn_rect.centery - start_btn.get_height()//2))
        elif state == "gameover":
            # game over panel
            panel_w, panel_h = 280, 140
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            screen.blit(panel, (WIDTH//2 - panel_w//2, HEIGHT//2 - panel_h//2 - 20))
            go = font_med.render("Game Over", True, TEXT_COLOR)
            sc = font_med.render(f"Score: {score}", True, TEXT_COLOR)
            hs = font_med.render(f"High: {highscore}", True, TEXT_COLOR)
            restart = font_small.render("Space / Click to restart", True, TEXT_COLOR)
            screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 70))
            screen.blit(sc, (WIDTH//2 - sc.get_width()//2, HEIGHT//2 - 40))
            screen.blit(hs, (WIDTH//2 - hs.get_width()//2, HEIGHT//2 - 15))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 30))

        # small highscore display top-left
        small = font_small.render(f"High: {highscore}", True, (3, 51, 51))
        screen.blit(small, (8, 8))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
