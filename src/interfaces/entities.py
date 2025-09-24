"""Entidades do jogo."""

import math
import random
import pygame

# Import do Config com fallback
try:
    from ..configs.config import Config
except ImportError:
    try:
        from src.configs.config import Config
    except ImportError:
        import sys
        import os

        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")
        sys.path.append(config_dir)
        from config import Config


class Particle:
    """Partícula para efeitos visuais."""

    def __init__(self, x, y, color, velocity, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt):
        """Atualiza partícula."""
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.age += dt
        return self.age < self.lifetime

    def draw(self, surf):
        """Desenha partícula."""
        alpha = 255 * (1 - self.age / self.lifetime)
        r, g, b = self.color
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, int(alpha)), (2, 2), 2)
        surf.blit(s, (int(self.x) - 2, int(self.y) - 2))


class Bullet:
    """Projétil."""

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 15.0
        self.distance = 0
        self.max_distance = Config.GRID_W // 2

    def update(self, dt):
        """Atualiza projétil."""
        dx, dy = self.direction
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self.distance += self.speed * dt
        return self.distance < self.max_distance * Config.CELL

    def draw(self, surf):
        """Desenha projétil."""
        px = self.x
        py = Config.FIELD_Y + self.y
        pygame.draw.circle(surf, (255, 255, 100), (int(px), int(py)), 4)
        pygame.draw.circle(surf, (255, 200, 50), (int(px), int(py)), 2)

        # Rastro
        for i in range(1, 4):
            trail_x = self.x - self.direction[0] * i * 3
            trail_y = self.y - self.direction[1] * i * 3
            pygame.draw.circle(
                surf,
                (255, 200, 50),
                (int(trail_x), int(Config.FIELD_Y + trail_y)),
                3 - i,
            )

    def get_grid_pos(self):
        """Posição na grade."""
        # Corrigir o cálculo da posição do projétil na grade
        return int(self.x // Config.CELL), int((self.y - Config.FIELD_Y) // Config.CELL)


class Spider:
    """Aranha inimiga."""

    def __init__(self, pos, step_time=0.45, drop_rate=0.25):
        self.pos = pos
        self.acc = 0.0
        self.step_time = step_time
        self.drop_rate = drop_rate

    def _best_step(self, target, blocked):
        """Encontra melhor movimento."""
        tx, ty = target
        x, y = self.pos
        choices = []

        if tx > x:
            choices.append((1, 0))
        if tx < x:
            choices.append((-1, 0))
        if ty > y:
            choices.append((0, 1))
        if ty < y:
            choices.append((0, -1))

        random.shuffle(choices)

        for dx, dy in choices:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < Config.GRID_W
                and 0 <= ny < Config.GRID_H
                and (nx, ny) not in blocked
            ):
                return (nx, ny), (dx, dy)

        # Fallback
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < Config.GRID_W
                and 0 <= ny < Config.GRID_H
                and (nx, ny) not in blocked
            ):
                return (nx, ny), (dx, dy)

        return (x, y), (0, 0)

    def update(self, dt, target, blocked, pillars):
        """Atualiza aranha."""
        self.acc += dt
        dropped = None

        while self.acc >= self.step_time:
            self.acc -= self.step_time
            old = self.pos
            new, _ = self._best_step(target, blocked | {p.pos for p in pillars})
            self.pos = new

            if new != old and random.random() < self.drop_rate:
                dropped = Pillar(old, ttl=5.0)

        return dropped

    def draw(self, surf):
        """Desenha aranha."""
        x, y = self.pos
        px = x * Config.CELL + Config.CELL // 2
        py = Config.FIELD_Y + y * Config.CELL + Config.CELL // 2

        body = (200, 40, 40)
        pygame.draw.circle(surf, body, (px, py), Config.CELL // 2 - 4)
        pygame.draw.circle(surf, (120, 20, 20), (px + 2, py - 2), Config.CELL // 2 - 8)

        leg = (255, 210, 210)
        for i in range(-3, 4):
            lx = px - (Config.CELL // 2) + 2
            rx = px + (Config.CELL // 2) - 2
            ly = py + i * 2
            pygame.draw.line(surf, leg, (lx, ly), (lx + 6, ly - 2), 2)
            pygame.draw.line(surf, leg, (rx, ly), (rx - 6, ly - 2), 2)


class Pillar:
    """Pilar obstáculo."""

    def __init__(self, pos, ttl=6.0):
        self.pos = pos
        self.ttl = ttl

    def update(self, dt):
        """Atualiza pilar."""
        self.ttl -= dt
        return self.ttl <= 0

    def draw(self, surf):
        """Desenha pilar."""
        x, y = self.pos
        px = x * Config.CELL + Config.CELL // 2
        py = Config.FIELD_Y + y * Config.CELL + Config.CELL // 2
        r = Config.CELL // 2 - 4

        base = (70, 120, 255)
        pygame.draw.rect(surf, base, (px - r, py - r, 2 * r, 2 * r), border_radius=6)
        pygame.draw.rect(
            surf, (22, 40, 90), (px - r, py - r, 2 * r, 2 * r), 2, border_radius=6
        )


class PowerUp:
    """Power-up coletável."""

    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_
        self.colors = {
            "speed": (0, 255, 255),
            "freeze": (0, 0, 255),
            "shield": (255, 215, 0),
            "time": (50, 205, 50),
            "kill": (255, 50, 50),
        }
        self.symbols = {
            "speed": "S",
            "freeze": "F",
            "shield": "D",
            "time": "T",
            "kill": "K",
        }

    def draw(self, surf, font):
        """Desenha power-up."""
        x, y = self.pos
        px = x * Config.CELL + Config.CELL // 2
        py = Config.FIELD_Y + y * Config.CELL + Config.CELL // 2

        pygame.draw.circle(surf, self.colors[self.type], (px, py), Config.CELL // 2 - 2)
        pygame.draw.circle(surf, (255, 255, 255), (px, py), Config.CELL // 2 - 2, 2)

        symbol = self.symbols[self.type]
        text = font.render(symbol, True, (255, 255, 255))
        surf.blit(text, text.get_rect(center=(px, py)))
