"""Gerenciadores de sistema."""

import os
import pygame

# Imports com fallback
try:
    from ..configs.config import Config
    from ..utils.utils import FileManager
except ImportError:
    try:
        from src.configs.config import Config
        from src.utils.utils import FileManager
    except ImportError:
        import sys

        current_dir = os.path.dirname(__file__)
        config_dir = os.path.join(os.path.dirname(current_dir), "configs")
        utils_dir = os.path.join(os.path.dirname(current_dir), "utils")
        sys.path.extend([config_dir, utils_dir])
        from config import Config
        from utils import FileManager


class ThemeManager:
    """Gerencia temas visuais."""

    def __init__(self):
        self.themes = {
            "CLEAN": {
                "name": "Cobra d'água",
                "BG_BASE": (16, 18, 22),
                "GRID": (52, 56, 64),
                "FG": (238, 240, 243),
                "HEAD": (64, 196, 140),
                "DANGER": (235, 87, 87),
                "PALETA": [
                    (251, 191, 36),
                    (99, 102, 241),
                    (16, 185, 129),
                    (59, 130, 246),
                    (244, 114, 182),
                ],
                "SNAKE_PATTERN": [(64, 196, 140), (56, 189, 248), (96, 165, 250)],
                "SNAKE_TYPE": "água",
                "BG_IMAGE": None,
            },
            "NEON": {
                "name": "Cobra coral",
                "BG_BASE": (22, 24, 28),
                "GRID": (42, 44, 50),
                "FG": (240, 240, 240),
                "HEAD": (30, 210, 130),
                "DANGER": (235, 70, 70),
                "PALETA": [
                    (255, 215, 0),
                    (255, 120, 80),
                    (155, 85, 245),
                    (80, 220, 120),
                    (80, 190, 255),
                ],
                "SNAKE_PATTERN": [(255, 50, 50), (255, 120, 80), (155, 85, 245)],
                "SNAKE_TYPE": "coral",
                "BG_IMAGE": None,
            },
            "RETRO70": {
                "name": "Cascavel",
                "BG_BASE": (20, 18, 16),
                "GRID": (58, 54, 50),
                "FG": (245, 235, 220),
                "HEAD": (206, 148, 72),
                "DANGER": (204, 70, 56),
                "PALETA": [
                    (225, 169, 95),
                    (140, 154, 99),
                    (211, 108, 61),
                    (167, 199, 231),
                    (174, 230, 197),
                ],
                "SNAKE_PATTERN": [(206, 148, 72), (211, 108, 61), (174, 230, 197)],
                "SNAKE_TYPE": "cascavel",
                "BG_IMAGE": None,
            },
        }

        self.theme_order = ["CLEAN", "NEON", "RETRO70"]
        self.current_index = 0
        self.bg_config = FileManager.load_json(Config.BG_CFG_PATH, {})
        self._apply_saved_backgrounds()

    def _apply_saved_backgrounds(self):
        """Aplica fundos salvos."""
        for theme_name in self.themes:
            path = self.bg_config.get(theme_name)
            if path and os.path.exists(path):
                self.themes[theme_name]["BG_IMAGE"] = path

    @property
    def current_theme_name(self):
        return self.theme_order[self.current_index]

    @property
    def current_theme(self):
        return self.themes[self.current_theme_name]

    def set_theme(self, index):
        """Define tema por índice."""
        self.current_index = index % len(self.theme_order)

    def next_theme(self):
        """Vai para o próximo tema."""
        self.current_index = (self.current_index + 1) % len(self.theme_order)

    def previous_theme(self):
        """Vai para o tema anterior."""
        self.current_index = (self.current_index - 1) % len(self.theme_order)

    def choose_background_image(self):
        """Abre seletor de imagem."""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            path = filedialog.askopenfilename(
                parent=root,
                title="Escolher fundo",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")],
            )

            root.destroy()

            if path:
                theme_name = self.current_theme_name
                self.themes[theme_name]["BG_IMAGE"] = path
                self.bg_config[theme_name] = path
                FileManager.save_json(Config.BG_CFG_PATH, self.bg_config)
                return True
        except:
            pass
        return False

    def clear_background_image(self):
        """Remove imagem de fundo."""
        theme_name = self.current_theme_name
        self.themes[theme_name]["BG_IMAGE"] = None
        self.bg_config[theme_name] = None
        FileManager.save_json(Config.BG_CFG_PATH, self.bg_config)

    def rebuild_surfaces_callback(self):
        """Callback para rebuild de superfícies após mudança de tema."""
        # This will be called by the game when theme changes
        pass


class AudioManager:
    """Gerencia áudio."""

    def __init__(self):
        self.enabled = False
        self.mixer_ok = self._init_mixer()
        self.sfx = {}
        self.music_tracks = {
            "CLEAN": "music/clean_theme.mp3",
            "NEON": "music/neon_theme.mp3",
            "RETRO70": "music/retro_theme.mp3",
        }
        self._load_sfx()

    def _init_mixer(self):
        """Inicializa mixer."""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            return True
        except:
            return False

    def _load_sfx(self):
        """Carrega efeitos sonoros."""
        if not self.mixer_ok:
            return

        sfx_files = {
            "collect": ("sfx/collect.wav", 0.6),
            "error": ("sfx/error.wav", 0.75),
            "kill": ("sfx/kill.wav", 0.7),
            "powerup": ("sfx/powerup.wav", 0.8),
            "shoot": ("sfx/shoot.wav", 0.6),
        }

        for name, (path, volume) in sfx_files.items():
            try:
                if os.path.exists(path):
                    self.sfx[name] = pygame.mixer.Sound(path)
                    self.sfx[name].set_volume(volume)
            except:
                pass

    def play_sfx(self, name):
        """Reproduz efeito sonoro."""
        if name in self.sfx:
            self.sfx[name].play()

    def play_theme_music(self, theme_name):
        """Reproduz música de tema."""
        if not (self.enabled and self.mixer_ok):
            return

        track_path = self.music_tracks.get(theme_name)
        if track_path and os.path.exists(track_path):
            try:
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.7)
            except:
                pass

    def stop_music(self):
        """Para música."""
        if self.mixer_ok:
            try:
                pygame.mixer.music.stop()
            except:
                pass

    def set_enabled(self, enabled):
        """Liga/desliga música."""
        self.enabled = enabled
        if not enabled:
            self.stop_music()

    def refresh_music(self, stop_only=False):
        """Atualiza música baseado no estado atual."""
        self.stop_music()
        if not stop_only and self.enabled:
            # Será implementado pelo game para tocar música do tema atual
            pass
