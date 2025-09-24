"""Utilitários e funções auxiliares."""

import os
import json
import time
import math
import pygame


class Utils:
    @staticmethod
    def load_font(path, size, bold=False):
        """Carrega fonte com fallback."""
        try:
            if os.path.exists(path):
                return pygame.font.Font(path, size)
        except:
            pass
        return pygame.font.SysFont("arial", size, bold=bold)

    @staticmethod
    def render_text_smooth(font, text, color):
        """Renderiza texto com anti-aliasing."""
        s = font.render(text, True, color)
        return s.convert_alpha() if (s.get_flags() & pygame.SRCALPHA) == 0 else s

    @staticmethod
    def draw_text(surf, font, text, x, y, color):
        """Desenha texto na superfície."""
        surf.blit(Utils.render_text_smooth(font, text, color), (x, y))

    @staticmethod
    def draw_text_outline_center(surf, txt, x, y, fill, outline, font, outer_px=2):
        """Desenha texto com contorno centralizado."""
        base = Utils.render_text_smooth(font, txt, fill)
        if outer_px > 0:
            for dx in (-outer_px, 0, outer_px):
                for dy in (-outer_px, 0, outer_px):
                    if dx == 0 and dy == 0:
                        continue
                    surf.blit(
                        Utils.render_text_smooth(font, txt, outline),
                        base.get_rect(center=(x + dx, y + dy)),
                    )
        surf.blit(base, base.get_rect(center=(x, y)))

    @staticmethod
    def fmt_secs(s):
        """Formata segundos em MM:SS.ss"""
        m = int(s // 60)
        sec = s - m * 60
        return f"{m:02d}:{sec:05.2f}"

    @staticmethod
    def luma(rgb):
        """Calcula luminância de uma cor."""
        r, g, b = rgb
        return (
            0.2126 * (r / 255) ** 2.2
            + 0.7152 * (g / 255) ** 2.2
            + 0.0722 * (b / 255) ** 2.2
        )

    @staticmethod
    def auto_text_colors(bg):
        """Determina cores de texto automáticas baseadas no fundo."""
        fill = (255, 255, 255) if Utils.luma(bg) < 0.36 else (0, 0, 0)
        outline = (0, 0, 0) if fill == (255, 255, 255) else (255, 255, 255)
        return fill, outline

    @staticmethod
    def scatter_chars(excluded, n, grid_w, grid_h):
        """Espalha caracteres em posições livres."""
        free_positions = [
            (x, y)
            for x in range(grid_w)
            for y in range(grid_h)
            if (x, y) not in excluded
        ]
        if len(free_positions) < n:
            return {}, {}

        import random

        positions = random.sample(free_positions, n)
        pos_by_idx = {i: positions[i] for i in range(n)}
        idx_by_pos = {positions[i]: i for i in range(n)}
        return pos_by_idx, idx_by_pos

    @staticmethod
    def head_hits_any(pos, pillars, spiders):
        """Verifica se a cabeça da cobra bateu em algo."""
        if any(p.pos == pos for p in pillars):
            return "Pilar"
        if any(s.pos == pos for s in spiders):
            return "Aranha"
        return None


class FileManager:
    """Gerencia operações de arquivo."""

    @staticmethod
    def load_json(filepath, default=None):
        """Carrega arquivo JSON com fallback."""
        if default is None:
            default = {}
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return default

    @staticmethod
    def save_json(filepath, data):
        """Salva dados em arquivo JSON."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False


class ScoreManager:
    """Gerencia sistema de pontuação."""

    def __init__(self, filepath):
        self.filepath = filepath

    def load_leaderboard(self):
        """Carrega ranking."""
        return FileManager.load_json(self.filepath, [])

    def add_score(self, name, seconds):
        """Adiciona nova pontuação."""
        lb = self.load_leaderboard()
        lb.append(
            {
                "name": name or "Jogador",
                "seconds": round(float(seconds), 3),
                "ts": int(time.time()),
            }
        )
        lb.sort(key=lambda x: x["seconds"])
        FileManager.save_json(self.filepath, lb[:100])
        return lb
