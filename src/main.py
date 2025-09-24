"""Jogo Snake - MECATRONICA
Arquivo principal do jogo.
"""

import sys
import os
import time
import random
import math
import pygame

# Adicionar o diretório pai ao path para permitir imports absolutos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Tentar imports relativos primeiro (quando executado como módulo)
    from .configs.config import Config
    from .utils.utils import Utils, ScoreManager
    from .handlers.managers import ThemeManager, AudioManager
    from .interfaces.entities import Particle, Bullet, Spider, Pillar, PowerUp
except ImportError:
    # Fallback para imports absolutos (quando executado diretamente)
    try:
        from src.configs.config import Config
        from src.utils.utils import Utils, ScoreManager
        from src.handlers.managers import ThemeManager, AudioManager
        from src.interfaces.entities import Particle, Bullet, Spider, Pillar, PowerUp
    except ImportError:
        # Último fallback - imports locais diretos
        try:
            import sys
            import os

            # Adicionar os diretórios específicos ao path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            configs_dir = os.path.join(current_dir, "configs")
            utils_dir = os.path.join(current_dir, "utils")
            handlers_dir = os.path.join(current_dir, "handlers")
            interfaces_dir = os.path.join(current_dir, "interfaces")

            for dir_path in [configs_dir, utils_dir, handlers_dir, interfaces_dir]:
                if dir_path not in sys.path:
                    sys.path.append(dir_path)

            from config import Config
            from utils import Utils, ScoreManager
            from managers import ThemeManager, AudioManager
            from entities import Particle, Bullet, Spider, Pillar, PowerUp
        except ImportError as e:
            print(f"Erro crítico de importação: {e}")
            print("Verifique se todos os arquivos estão na estrutura correta:")
            print("src/configs/config.py")
            print("src/utils/utils.py")
            print("src/handlers/managers.py")
            print("src/interfaces/entities.py")
            sys.exit(1)


class GameState:
    """Estados do jogo."""

    MENU = "menu"
    ENTER_NAME = "enter_name"
    PLAYING = "play"
    PAUSED = "pause"
    LEVEL = "level"
    GAME_OVER = "over"
    VICTORY = "win"
    LEADERBOARD = "leaderboard"
    OPTIONS = "options"
    THEME = "theme"
    BG = "bg"
    MUSIC = "music"
    SCREEN = "screen"


class Timer:
    """Gerencia tempo do jogo."""

    def __init__(self):
        self.start_time = None
        self.accumulated = 0.0

    def reset(self):
        """Reset do timer."""
        self.start_time = None
        self.accumulated = 0.0

    def start(self):
        """Inicia timer."""
        self.start_time = time.time()

    def pause(self):
        """Pausa timer."""
        if self.start_time:
            self.accumulated += time.time() - self.start_time
            self.start_time = None

    def resume(self):
        """Resume timer."""
        if self.start_time is None:
            self.start_time = time.time()

    def elapsed(self):
        """Tempo decorrido."""
        return self.accumulated + (
            time.time() - self.start_time if self.start_time else 0.0
        )


class SnakeGame:
    """Classe principal do jogo."""

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        # Managers
        self.theme_manager = ThemeManager()
        self.audio_manager = AudioManager()
        self.score_manager = ScoreManager(Config.LB_PATH)
        self.timer = Timer()

        # Window setup
        self.window_w, self.window_h = Config.WIN_W, Config.WIN_H
        self._create_window()
        self._load_fonts()

        # Game state
        self.state = GameState.MENU
        self.player_name = ""
        self.tick = 0.0

        # Particles system
        self.particles = []

        # Initialize game
        self._init_game_state()
        self._rebuild_field_bg()

    def _create_window(self):
        """Cria janela do jogo."""
        try:
            self.window = pygame.display.set_mode(
                (self.window_w, self.window_h), flags=pygame.SCALED, vsync=1
            )
        except TypeError:
            self.window = pygame.display.set_mode((self.window_w, self.window_h))

        pygame.display.set_caption("Snake - MECATRONICA")
        self.screen = pygame.Surface((Config.WIN_W, Config.WIN_H)).convert_alpha()

    def _load_fonts(self):
        """Carrega fontes."""
        self.fonts = {
            "huge": Utils.load_font("fonts/CooperBlack.ttf", 60),
            "big": Utils.load_font("fonts/CooperBlack.ttf", 44),
            "normal": Utils.load_font("fonts/Arial.ttf", 24),
            "small": Utils.load_font("fonts/Arial.ttf", 18),
            "token": Utils.load_font("fonts/CooperBlack.ttf", 32),
            "segment": Utils.load_font("fonts/CooperBlack.ttf", 24),
        }

    def _init_game_state(self):
        """Inicializa estado do jogo."""
        self.phase = 1
        self.snake = [(Config.GRID_W // 2, Config.GRID_H // 2)]
        self.labels = [None]
        self.direction = (1, 0)
        self.velocity = Config.BASE_SPEED[1]
        self.move_acc = 0.0
        self.char_index = 0

        # Letter positions
        self.pos_by_idx = {}
        self.idx_by_pos = {}

        # Enemies
        self.spiders = []
        self.pillars = []

        # Shooting system
        self.bullets = 0
        self.active_bullets = []

        # Power-ups
        self.power_ups = []
        self.power_up_timer = 0.0
        self.power_up_effects = {
            "speed": {"active": False, "end_time": 0, "multiplier": 1.5},
            "freeze": {"active": False, "end_time": 0, "multiplier": 0.5},
            "shield": {"active": False, "end_time": 0},
        }

        # Stats
        self.spider_kills = 0
        self.death_reason = ""

        self.timer.reset()

    def _rebuild_field_bg(self):
        """Reconstrói fundo do campo."""
        surf = pygame.Surface((Config.FIELD_W, Config.FIELD_H)).convert()
        theme = self.theme_manager.current_theme

        img_path = theme.get("BG_IMAGE")
        if img_path and os.path.exists(img_path):
            try:
                img = pygame.image.load(img_path).convert()
                img = pygame.transform.smoothscale(
                    img, (Config.FIELD_W, Config.FIELD_H)
                )
                surf.blit(img, (0, 0))
                shade = pygame.Surface(
                    (Config.FIELD_W, Config.FIELD_H), pygame.SRCALPHA
                )
                shade.fill((0, 0, 0, 48))
                surf.blit(shade, (0, 0))
            except Exception:
                surf.fill(theme["BG_BASE"])
        else:
            surf.fill(theme["BG_BASE"])

        # Grid
        grid = pygame.Surface((Config.FIELD_W, Config.FIELD_H), pygame.SRCALPHA)
        col = (*theme["GRID"], 28)
        for x in range(0, Config.FIELD_W, Config.CELL):
            pygame.draw.line(grid, col, (x, 0), (x, Config.FIELD_H))
        for y in range(0, Config.FIELD_H, Config.CELL):
            pygame.draw.line(grid, col, (0, y), (Config.FIELD_W, y))

        surf.blit(grid, (0, 0))
        self.field_bg = surf

    def run(self):
        """Loop principal."""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            self.tick += dt

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not self._handle_key_event(event):
                        running = False

            # Update
            self._update(dt)

            # Draw
            self._draw()

        pygame.quit()
        sys.exit()

    def _handle_key_event(self, event):
        """Processa eventos de teclado."""
        key = event.key

        if self.state == GameState.MENU:
            return self._handle_menu_keys(key)
        elif self.state == GameState.ENTER_NAME:
            return self._handle_name_keys(key, event)
        elif self.state == GameState.PLAYING:
            return self._handle_game_keys(key)
        elif self.state == GameState.LEADERBOARD:
            return self._handle_leaderboard_keys(key)
        elif self.state == GameState.OPTIONS:
            return self._handle_options_keys(key)
        elif self.state == GameState.THEME:
            return self._handle_theme_keys(key)
        elif self.state == GameState.BG:
            return self._handle_bg_keys(key)
        elif self.state == GameState.MUSIC:
            return self._handle_music_keys(key)
        elif self.state == GameState.SCREEN:
            return self._handle_screen_keys(key)
        elif self.state == GameState.LEVEL:
            return self._handle_level_keys(key)
        elif self.state == GameState.GAME_OVER:
            return self._handle_game_over_keys(key)
        elif self.state == GameState.VICTORY:
            return self._handle_victory_keys(key)
        elif self.state == GameState.PAUSED:
            return self._handle_pause_keys(key)

        return True

    def _handle_menu_keys(self, key):
        """Teclas do menu."""
        if key == pygame.K_1:
            self.state = GameState.ENTER_NAME
        elif key == pygame.K_2:
            self.state = GameState.LEADERBOARD
        elif key == pygame.K_3:
            self.state = GameState.OPTIONS
        elif key == pygame.K_4:
            self.state = GameState.SCREEN
        elif key == pygame.K_5:
            return False
        return True

    def _handle_name_keys(self, key, event):
        """Teclas da entrada de nome."""
        if key == pygame.K_RETURN and self.player_name:
            self._start_new_game()
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif event.unicode.isprintable() and len(self.player_name) < 15:
            self.player_name += event.unicode
        return True

    def _handle_game_keys(self, key):
        """Teclas do jogo."""
        # Movement
        if key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
            self.direction = (1, 0)
        elif key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
            self.direction = (0, 1)

        # Shooting
        elif key == pygame.K_SPACE and self.bullets > 0:
            self._shoot()

        # Pause
        elif key == pygame.K_0:
            self.timer.pause()
            self.state = GameState.PAUSED

        return True

    def _handle_leaderboard_keys(self, key):
        """Teclas do leaderboard."""
        if key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        return True

    def _handle_options_keys(self, key):
        """Teclas das opções."""
        if key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif key == pygame.K_1:
            self.state = GameState.THEME
        elif key == pygame.K_2:
            self.state = GameState.BG
        elif key == pygame.K_3:
            self.state = GameState.MUSIC
        return True

    def _handle_theme_keys(self, key):
        """Teclas do menu de temas."""
        if key == pygame.K_ESCAPE:
            self.state = GameState.OPTIONS
        elif key == pygame.K_1:
            self.theme_manager.set_theme(0)
            self._rebuild_field_bg()
            self.state = GameState.OPTIONS
        elif key == pygame.K_2:
            self.theme_manager.set_theme(1)
            self._rebuild_field_bg()
            self.state = GameState.OPTIONS
        elif key == pygame.K_3:
            self.theme_manager.set_theme(2)
            self._rebuild_field_bg()
            self.state = GameState.OPTIONS
        return True

    def _handle_bg_keys(self, key):
        """Teclas do menu de fundo."""
        if key == pygame.K_ESCAPE:
            self.state = GameState.OPTIONS
        elif key == pygame.K_1:
            if self.theme_manager.choose_background_image():
                self._rebuild_field_bg()
            self.state = GameState.OPTIONS
        elif key == pygame.K_2:
            self.theme_manager.clear_background_image()
            self._rebuild_field_bg()
            self.state = GameState.OPTIONS
        return True

    def _handle_music_keys(self, key):
        """Teclas do menu de música."""
        if key == pygame.K_ESCAPE:
            self.state = GameState.OPTIONS
        elif key == pygame.K_1:
            self.audio_manager.set_enabled(True)
            self.audio_manager.play_theme_music(self.theme_manager.current_theme_name)
            self.state = GameState.OPTIONS
        elif key == pygame.K_2:
            self.audio_manager.set_enabled(False)
            self.state = GameState.OPTIONS
        return True

    def _handle_screen_keys(self, key):
        """Teclas do menu de resolução."""
        if key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif key == pygame.K_1:
            self.window_w, self.window_h = 800, 600
            self._create_window()
            self.state = GameState.MENU
        elif key == pygame.K_2:
            self.window_w, self.window_h = 1280, 720
            self._create_window()
            self.state = GameState.MENU
        elif key == pygame.K_3:
            self.window_w, self.window_h = 1600, 900
            self._create_window()
            self.state = GameState.MENU
        return True

    def _handle_level_keys(self, key):
        """Teclas da transição de fase."""
        if key == pygame.K_RETURN:
            self._place_letters()
            self.timer.resume()
            self.state = GameState.PLAYING
        return True

    def _handle_game_over_keys(self, key):
        """Teclas do game over."""
        if key == pygame.K_1:  # Repetir fase
            self._restart_phase()
        elif key == pygame.K_2:  # Novo jogo
            self._start_new_game()
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        return True

    def _handle_victory_keys(self, key):
        """Teclas da vitória."""
        if key == pygame.K_1:  # Jogar de novo
            self._start_new_game()
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        return True

    def _handle_pause_keys(self, key):
        """Teclas do menu de pausa."""
        if key == pygame.K_1:  # Continuar
            self.timer.resume()
            self.state = GameState.PLAYING
        elif key == pygame.K_2:  # Reiniciar fase
            self._restart_phase()
        elif key == pygame.K_3:  # Opções
            self.state = GameState.OPTIONS
        elif key == pygame.K_4:  # Menu principal
            self.state = GameState.MENU
        return True

    def _restart_phase(self):
        """Reinicia a fase atual."""
        current_phase = self.phase  # Salvar fase atual
        self._init_game_state()
        self.phase = current_phase  # Restaurar fase
        self._spawn_enemies()
        self._place_letters()
        self.timer.reset()
        self.timer.start()
        self.state = GameState.PLAYING

    def _shoot(self):
        """Dispara projétil."""
        if self.bullets <= 0:
            return

        hx, hy = self.snake[0]
        bullet_x = hx * Config.CELL + Config.CELL // 2
        bullet_y = Config.FIELD_Y + hy * Config.CELL + Config.CELL // 2
        self.active_bullets.append(Bullet(bullet_x, bullet_y, self.direction))
        self.bullets -= 1
        self.audio_manager.play_sfx("shoot")

    def _start_new_game(self):
        """Inicia novo jogo."""
        self._init_game_state()
        self._spawn_enemies()
        self._place_letters()
        self.timer.start()
        self.state = GameState.PLAYING

    def _spawn_enemies(self):
        """Gera inimigos."""
        self.spiders = []
        count = Config.SPIDERS_BY_PHASE[self.phase]
        step_time = Config.SPIDER_STEP_BY_PHASE[self.phase]
        drop_rate = Config.DROP_RATE_BY_PHASE[self.phase]

        blocked = set(self.snake)
        free_positions = [
            (x, y)
            for x in range(Config.GRID_W)
            for y in range(Config.GRID_H)
            if (x, y) not in blocked
        ]

        for _ in range(min(count, len(free_positions))):
            pos = random.choice(free_positions)
            free_positions.remove(pos)
            self.spiders.append(Spider(pos, step_time, drop_rate))

    def _place_letters(self):
        """Posiciona letras com tentativas de segurança."""
        blocked = (
            set(self.snake)
            | {s.pos for s in self.spiders}
            | {p.pos for p in self.pillars}
        )

        self.pos_by_idx, self.idx_by_pos = Utils.scatter_chars(
            blocked, Config.NCHARS, Config.GRID_W, Config.GRID_H
        )

        # Try multiple times if snake head conflicts with letters
        tries = 0
        while (not self.pos_by_idx or self.snake[0] in self.idx_by_pos) and tries < 40:
            self.pos_by_idx, self.idx_by_pos = Utils.scatter_chars(
                blocked, Config.NCHARS, Config.GRID_W, Config.GRID_H
            )
            tries += 1

    def _update(self, dt):
        """Atualização principal."""
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]

        if self.state == GameState.PLAYING:
            self._update_game(dt)

    def _update_game(self, dt):
        """Atualiza lógica do jogo."""
        # Update bullets
        self.active_bullets = [
            bullet for bullet in self.active_bullets if bullet.update(dt)
        ]

        # Check bullet-spider collisions
        for bullet in self.active_bullets[:]:
            bullet_pos = bullet.get_grid_pos()
            for i, spider in enumerate(self.spiders):
                if bullet_pos == spider.pos:
                    self.spiders.pop(i)
                    self.spider_kills += 1
                    if bullet in self.active_bullets:
                        self.active_bullets.remove(bullet)
                    self.audio_manager.play_sfx("kill")
                    self._add_particles(
                        spider.pos[0] * Config.CELL + Config.CELL // 2,
                        Config.FIELD_Y + spider.pos[1] * Config.CELL + Config.CELL // 2,
                        (255, 50, 50),
                        25,
                    )
                    break

        # Update power-ups
        self.power_up_timer += dt
        if self.power_up_timer >= Config.POWER_UP_SPAWN_TIME:
            if self._spawn_power_up():
                self.power_up_timer = 0.0

        # Check power-up effects expiration
        current_time = self.timer.elapsed()
        for effect in self.power_up_effects.values():
            if effect.get("active", False) and current_time >= effect.get(
                "end_time", 0
            ):
                effect["active"] = False

        # Apply power-up effects to velocity
        effective_vel = self.velocity
        if self.power_up_effects["speed"]["active"]:
            effective_vel *= self.power_up_effects["speed"]["multiplier"]
        if self.power_up_effects["freeze"]["active"]:
            effective_vel *= self.power_up_effects["freeze"]["multiplier"]

        # Snake movement
        self.move_acc += dt
        step = 1.0 / max(effective_vel, 0.0001)

        while self.move_acc >= step:
            self.move_acc -= step
            if not self._move_snake():
                break

        # Update enemies
        if self.state == GameState.PLAYING:
            blocked = set(self.snake)
            new_pillars = []
            for spider in self.spiders:
                pillar = spider.update(dt, self.snake[0], blocked, self.pillars)
                if pillar:
                    new_pillars.append(pillar)
            self.pillars.extend(new_pillars)
            self.pillars = [p for p in self.pillars if not p.update(dt)]

            # Check power-up collection
            for i, power_up in enumerate(self.power_ups):
                if self.snake[0] == power_up.pos:
                    self._apply_power_up(power_up.type)
                    self._add_particles(
                        self.snake[0][0] * Config.CELL + Config.CELL // 2,
                        Config.FIELD_Y
                        + self.snake[0][1] * Config.CELL
                        + Config.CELL // 2,
                        power_up.colors[power_up.type],
                        20,
                    )
                    self.power_ups.pop(i)
                    break

            # Check spider bites snake
            if (
                self._any_spider_bites_snake()
                and not self.power_up_effects["shield"]["active"]
            ):
                self._game_over("Aranha")

    def _any_spider_bites_snake(self):
        """Verifica se alguma aranha mordeu a cobra."""
        snake_set = set(self.snake)
        return any(s.pos in snake_set for s in self.spiders)

    def _move_snake(self):
        """Move a cobra."""
        hx, hy = self.snake[0]
        nx, ny = hx + self.direction[0], hy + self.direction[1]

        # Check boundary collisions
        if nx < 0 or nx >= Config.GRID_W or ny < 0 or ny >= Config.GRID_H:
            self._game_over("Parede")
            return False

        # Check self collision
        if (nx, ny) in self.snake[:-1]:
            self._game_over("Corpo")
            return False

        # Check enemy collisions (only if shield is not active)
        if not self.power_up_effects["shield"]["active"]:
            # Check spider collision
            if any(s.pos == (nx, ny) for s in self.spiders):
                self._game_over("Aranha")
                return False
            # Check pillar collision
            if any(p.pos == (nx, ny) for p in self.pillars):
                self._game_over("Pilar")
                return False

        # Move snake
        self.snake.insert(0, (nx, ny))
        self.labels.insert(0, None)

        # Check letter collection
        if (nx, ny) in self.idx_by_pos:
            idx = self.idx_by_pos[(nx, ny)]
            if idx == self.char_index:
                self._collect_letter(idx)
            else:
                self._game_over("Letra errada")
                return False
        else:
            # If not collecting a letter, remove tail
            self.snake.pop()
            self.labels.pop()

        return True

    def _collect_letter(self, idx):
        """Coleta uma letra."""
        self.labels[0] = Config.SEQUENCE[idx]
        self.char_index += 1
        self.bullets += 1
        self.velocity = min(
            Config.GLOBAL_CAP,
            min(Config.PHASE_CAP[self.phase], self.velocity + Config.INC_PER_CHAR),
        )

        # Remove letter from positions
        pos = self.pos_by_idx[idx]
        del self.idx_by_pos[pos]
        del self.pos_by_idx[idx]

        self.audio_manager.play_sfx("collect")

        # Add particles
        self._add_particles(
            self.snake[0][0] * Config.CELL + Config.CELL // 2,
            Config.FIELD_Y + self.snake[0][1] * Config.CELL + Config.CELL // 2,
            self.theme_manager.current_theme["PALETA"][
                (idx) % len(self.theme_manager.current_theme["PALETA"])
            ],
            15,
        )

        # Check if phase completed
        if self.char_index >= Config.NCHARS:
            self._complete_phase()

    def _complete_phase(self):
        """Completa uma fase."""
        self.char_index = 0
        self.pos_by_idx.clear()
        self.idx_by_pos.clear()

        if self.phase >= 3:
            self._win_game()
        else:
            self.phase += 1
            # Reset match but keep snake and labels
            self._reset_match_keep_snake()
            self.timer.pause()
            self.state = GameState.LEVEL

    def _reset_match_keep_snake(self):
        """Reset match mantendo cobra e labels."""
        self.velocity = Config.BASE_SPEED[self.phase]
        self.move_acc = 0.0
        self.pos_by_idx = {}
        self.idx_by_pos = {}

        # Spawn new enemies
        self._spawn_enemies()

    def _game_over(self, reason):
        """Game over."""
        self.death_reason = reason
        self.timer.pause()
        self.audio_manager.play_sfx("error")
        self._add_particles(
            self.snake[0][0] * Config.CELL + Config.CELL // 2,
            Config.FIELD_Y + self.snake[0][1] * Config.CELL + Config.CELL // 2,
            (235, 70, 70),
            20,
        )
        self.state = GameState.GAME_OVER

    def _win_game(self):
        """Vitória."""
        self.timer.pause()
        self.score_manager.add_score(
            self.player_name or "Jogador", self.timer.elapsed()
        )
        self.state = GameState.VICTORY

    def _spawn_power_up(self):
        """Gera power-up."""
        occupied = (
            set(self.snake)
            | {s.pos for s in self.spiders}
            | {p.pos for p in self.pillars}
            | set(self.pos_by_idx.values())
        )

        free_positions = [
            (x, y)
            for x in range(Config.GRID_W)
            for y in range(Config.GRID_H)
            if (x, y) not in occupied
        ]

        if free_positions:
            pos = random.choice(free_positions)
            power_type = random.choice(["speed", "freeze", "shield", "time", "kill"])
            self.power_ups.append(PowerUp(pos, power_type))
            return True
        return False

    def _apply_power_up(self, power_type):
        """Aplica efeito do power-up."""
        now = self.timer.elapsed()

        if power_type == "speed":
            self.power_up_effects["speed"]["active"] = True
            self.power_up_effects["speed"]["end_time"] = now + 10.0
        elif power_type == "freeze":
            self.power_up_effects["freeze"]["active"] = True
            self.power_up_effects["freeze"]["end_time"] = now + 8.0
        elif power_type == "shield":
            self.power_up_effects["shield"]["active"] = True
            self.power_up_effects["shield"]["end_time"] = now + 12.0
        elif power_type == "time":
            # Subtract 5 seconds from accumulated time
            self.timer.accumulated -= 5.0
            if self.timer.start_time is not None:
                self.timer.accumulated -= time.time() - self.timer.start_time
                self.timer.start_time = time.time()
        elif power_type == "kill":
            self.bullets += 3

        self.audio_manager.play_sfx("powerup")

    def _add_particles(self, x, y, color, count=10):
        """Adiciona partículas."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(20, 100)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(
                Particle(x, y, color, (vx, vy), random.uniform(0.5, 1.5))
            )

    def _draw(self):
        """Desenho principal."""
        self.screen.fill((0, 0, 0))

        # Draw HUD
        self._draw_hud()

        # Draw field background
        self.screen.blit(self.field_bg, (0, Config.FIELD_Y))

        # Draw game objects
        if self.state in (
            GameState.PLAYING,
            GameState.PAUSED,
            GameState.GAME_OVER,
            GameState.VICTORY,
            GameState.LEVEL,
        ):
            self._draw_game_objects()

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw UI overlay
        self._draw_ui_overlay()

        # Scale to window
        scaled = pygame.transform.smoothscale(
            self.screen, (self.window_w, self.window_h)
        )
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()

    def _draw_hud(self):
        """Desenha HUD superior."""
        # Painel escuro de fundo
        pygame.draw.rect(
            self.screen, Config.DARK_PANEL, (0, 0, Config.WIN_W, Config.TOP_PANEL_H)
        )

        # Vidro transparente
        glass = pygame.Surface((Config.WIN_W, Config.TOP_PANEL_H), pygame.SRCALPHA)
        glass.fill((255, 255, 255, 16))
        self.screen.blit(glass, (0, 0))

        pad = 16
        theme = self.theme_manager.current_theme

        # Nome do jogador e tempo
        Utils.draw_text(
            self.screen,
            self.fonts["normal"],
            f"Jogador: {self.player_name or 'Jogador'}",
            pad,
            12,
            theme["FG"],
        )
        if self.state in (
            GameState.PLAYING,
            GameState.PAUSED,
            GameState.GAME_OVER,
            GameState.VICTORY,
            GameState.LEVEL,
        ):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                f"Tempo: {Utils.fmt_secs(self.timer.elapsed())}",
                pad,
                44,
                theme["FG"],
            )

        # Fase e próxima letra
        mid = f"Fase {self.phase}/3"
        Utils.draw_text(
            self.screen,
            self.fonts["normal"],
            mid,
            Config.WIN_W // 2 - self.fonts["normal"].size(mid)[0] // 2,
            12,
            theme["FG"],
        )

        prox_char = (
            Config.SEQUENCE[self.char_index] if self.char_index < Config.NCHARS else "-"
        )
        ri1 = f"Próximo: {prox_char}"
        ri2 = f"Vel: {self.velocity:.1f}"
        right_x = (
            Config.WIN_W
            - pad
            - max(self.fonts["normal"].size(ri1)[0], self.fonts["normal"].size(ri2)[0])
        )
        Utils.draw_text(
            self.screen, self.fonts["normal"], ri1, right_x, 12, theme["FG"]
        )
        Utils.draw_text(
            self.screen, self.fonts["normal"], ri2, right_x, 44, theme["FG"]
        )

        # Aranhas abatidas
        if self.spider_kills > 0:
            kills_text = f"Aranhas: {self.spider_kills}"
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                kills_text,
                Config.WIN_W // 2 - self.fonts["normal"].size(kills_text)[0] // 2,
                44,
                theme["FG"],
            )

        # Indicador de balas
        if self.bullets > 0:
            bullets_text = f"Tiros: {self.bullets}"
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                bullets_text,
                Config.WIN_W - pad - self.fonts["normal"].size(bullets_text)[0],
                Config.TOP_PANEL_H - 30,
                (255, 200, 50),
            )

        # Pílulas de progresso
        self._draw_progress_pills()

    def _draw_progress_pills(self):
        """Desenha as pílulas de progresso das letras."""
        pill_w, pill_h = 34, 26
        start_x = Config.WIN_W // 2 - (Config.NCHARS * (pill_w + 6) - 6) // 2
        y = 64

        for i, ch in enumerate(Config.SEQUENCE):
            x = start_x + i * (pill_w + 6)
            if i < self.char_index:
                bg = (24, 142, 96)
                fg = (18, 24, 22)
            elif i == self.char_index:
                bg = (32, 170, 120)
                fg = (18, 24, 22)
            else:
                bg = (64, 68, 76)
                fg = (238, 238, 238)

            pygame.draw.rect(self.screen, bg, (x, y, pill_w, pill_h), border_radius=8)
            pygame.draw.rect(
                self.screen, (255, 255, 255), (x, y, pill_w, pill_h), 1, border_radius=8
            )

            text_x = x + (pill_w - self.fonts["small"].size(ch)[0]) // 2
            text_y = y + (pill_h - self.fonts["small"].get_height()) // 2
            Utils.draw_text(self.screen, self.fonts["small"], ch, text_x, text_y, fg)

    def _draw_game_objects(self):
        """Desenha objetos do jogo."""
        theme = self.theme_manager.current_theme

        # Desenhar letras
        for i, pos in self.pos_by_idx.items():
            self._draw_letter_token(
                pos,
                Config.SEQUENCE[i],
                theme["PALETA"][i % len(theme["PALETA"])],
                i == self.char_index,
            )

        # Desenhar power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen, self.fonts["small"])

        # Desenhar inimigos
        for pillar in self.pillars:
            pillar.draw(self.screen)
        for spider in self.spiders:
            spider.draw(self.screen)

        # Desenhar projéteis
        for bullet in self.active_bullets:
            bullet.draw(self.screen)

        # Desenhar cobra
        self._draw_snake()

    def _draw_letter_token(self, pos, char, color, is_next=False):
        """Desenha um token de letra."""
        x, y = pos
        px = x * Config.CELL + Config.CELL // 2
        py = Config.FIELD_Y + y * Config.CELL + Config.CELL // 2
        R = Config.CELL // 2 - 3

        pygame.draw.circle(self.screen, color, (px, py), R)
        pygame.draw.circle(self.screen, (245, 246, 248), (px, py), R, 2)

        # Efeito de brilho para a próxima letra
        if is_next:
            glow = pygame.Surface((Config.CELL * 3, Config.CELL * 3), pygame.SRCALPHA)
            pygame.draw.circle(
                glow,
                (255, 255, 255, 70),
                (Config.CELL + Config.CELL // 2, Config.CELL + Config.CELL // 2),
                R + 8,
            )
            self.screen.blit(
                glow,
                (
                    px - (Config.CELL + Config.CELL // 2),
                    py - (Config.CELL + Config.CELL // 2),
                ),
                special_flags=pygame.BLEND_PREMULTIPLIED,
            )

        # Desenhar a letra
        text = Utils.render_text_smooth(self.fonts["token"], str(char), (255, 255, 255))
        shadow = Utils.render_text_smooth(self.fonts["token"], str(char), (0, 0, 0))
        rect = text.get_rect(center=(px, py))
        self.screen.blit(shadow, rect.move(1, 1))
        self.screen.blit(text, rect)

    def _draw_snake(self):
        """Desenha a cobra com animação."""
        theme = self.theme_manager.current_theme
        pattern = theme["SNAKE_PATTERN"]

        # Desenhar segmentos do corpo (do rabo para a cabeça)
        total = len(self.snake)
        for i in range(total - 1, 0, -1):
            x, y = self.snake[i]
            px = x * Config.CELL + Config.CELL // 2
            py = Config.FIELD_Y + y * Config.CELL + Config.CELL // 2

            # Calcular direção do segmento
            prev_idx = max(0, i - 1)
            next_idx = min(total - 1, i + 1)
            vx, vy = self._seg_dir(
                self.snake[next_idx if next_idx < total else i], self.snake[prev_idx]
            )

            # Aplicar efeito de ondulação
            ampl = Config.SLITHER_AMPL * (0.6 + 0.4 * math.sin(self.tick * 2.0))
            px, py = self._apply_slither(px, py, vx, vy, k=(total - i), base_ampl=ampl)

            color = pattern[i % len(pattern)]
            self._draw_snake_segment(
                px, py, color, self.labels[i] if i < len(self.labels) else None
            )

        # Desenhar cabeça com interpolação suave
        hx, hy = self.snake[0]
        head_now = self._head_pixel_pos(hx, hy)
        prev_pos = self._head_pixel_pos(
            *(self.snake[1] if len(self.snake) > 1 else self.snake[0])
        )

        step = 1.0 / max(self.velocity, 0.0001)
        frac = 1.0 - (self.move_acc / step) if self.state == GameState.PLAYING else 1.0
        frac = max(0.0, min(1.0, frac))

        hx_px = int(prev_pos[0] + (head_now[0] - prev_pos[0]) * frac)
        hy_px = int(prev_pos[1] + (head_now[1] - prev_pos[1]) * frac)

        dx, dy = self._seg_dir(
            self.snake[1] if len(self.snake) > 1 else self.snake[0], self.snake[0]
        )
        hx_px, hy_px = self._apply_slither(
            hx_px, hy_px, dx, dy, k=-0.5, base_ampl=Config.HEAD_SWAY
        )

        # Desenhar cabeça
        self._draw_snake_segment(
            hx_px,
            hy_px,
            theme["HEAD"],
            self.labels[0] if self.labels else None,
            is_head=True,
        )

        # Desenhar língua ocasionalmente
        self._maybe_draw_tongue(hx_px, hy_px, (dx, dy))

        # Desenhar escudo se ativo
        if self.power_up_effects["shield"]["active"]:
            pygame.draw.circle(
                self.screen, (255, 215, 0, 100), (hx_px, hy_px), Config.CELL, width=2
            )

    def _head_pixel_pos(self, hx, hy):
        """Posição em pixels da cabeça da cobra."""
        return (
            hx * Config.CELL + Config.CELL // 2,
            Config.FIELD_Y + hy * Config.CELL + Config.CELL // 2,
        )

    def _seg_dir(self, seg_prev, seg_next):
        """Calcula direção do segmento."""
        x0, y0 = seg_prev
        x1, y1 = seg_next
        vx, vy = (x1 - x0, y1 - y0)
        vx = 1 if vx > 0 else (-1 if vx < 0 else 0)
        vy = 1 if vy > 0 else (-1 if vy < 0 else 0)
        if vx == 0 and vy == 0:
            vx, vy = 1, 0
        return vx, vy

    def _apply_slither(self, px, py, vx, vy, k, base_ampl):
        """Aplica efeito de ondulação."""
        phase = self.tick * Config.SLITHER_SPEED - k * 0.6
        sway = base_ampl * math.sin(phase)
        perp = (-vy, vx)
        return int(px + perp[0] * sway), int(py + perp[1] * sway)

    def _draw_snake_segment(self, px, py, color, label=None, is_head=False):
        """Desenha um segmento da cobra."""
        R = Config.CELL // 2 - 2
        ring = (max(color[0] - 25, 0), max(color[1] - 25, 0), max(color[2] - 25, 0))
        inner = (
            min(color[0] + 18, 255),
            min(color[1] + 18, 255),
            min(color[2] + 18, 255),
        )

        # Desenhar segmento
        pygame.draw.circle(self.screen, inner, (px, py), R - 1)
        pygame.draw.circle(self.screen, ring, (px, py), R, 2)

        # Padrões especiais baseados no tipo de cobra
        theme = self.theme_manager.current_theme
        snake_type = theme.get("SNAKE_TYPE", "água")

        if not is_head:
            if snake_type == "cascavel":
                pygame.draw.circle(self.screen, ring, (px, py), R - 4, 2)
            elif snake_type == "coral":
                pygame.draw.circle(self.screen, (255, 255, 255), (px, py), R - 4, 1)

        # Desenhar label se houver
        if label:
            fill, outline = Utils.auto_text_colors(inner)
            Utils.draw_text_outline_center(
                self.screen,
                str(label),
                px,
                py,
                fill,
                outline,
                self.fonts["segment"],
                outer_px=1,
            )

    def _maybe_draw_tongue(self, px, py, direction):
        """Desenha língua ocasionalmente."""
        t = self.tick % 1.4
        if t < 0.18:  # Mostra língua 20% do tempo a cada 1.4 segundos
            dx, dy = direction
            base_len = 10
            tip_spread = 4

            bx = px + dx * (Config.CELL // 2 - 1)
            by = py + dy * (Config.CELL // 2 - 1)
            tx = bx + dx * base_len
            ty = by + dy * base_len

            # Pontas da língua
            px1 = tx + (-dy) * tip_spread
            py1 = ty + (dx) * tip_spread
            px2 = tx - (-dy) * tip_spread
            py2 = ty - (dx) * tip_spread

            col = (255, 90, 90)
            pygame.draw.line(self.screen, col, (bx, by), (tx, ty), 2)
            pygame.draw.line(self.screen, col, (tx, ty), (px1, py1), 2)
            pygame.draw.line(self.screen, col, (tx, ty), (px2, py2), 2)

    def _draw_ui_overlay(self):
        """Desenha overlays de UI."""
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.ENTER_NAME:
            self._draw_name_entry()
        elif self.state == GameState.LEADERBOARD:
            self._draw_leaderboard()
        elif self.state == GameState.OPTIONS:
            self._draw_options()
        elif self.state == GameState.THEME:
            self._draw_theme_menu()
        elif self.state == GameState.BG:
            self._draw_bg_menu()
        elif self.state == GameState.MUSIC:
            self._draw_music_menu()
        elif self.state == GameState.SCREEN:
            self._draw_screen_menu()
        elif self.state == GameState.LEVEL:
            self._draw_level()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        elif self.state == GameState.VICTORY:
            self._draw_victory()
        elif self.state == GameState.PAUSED:
            self._draw_pause()

    def _dim_field(self, alpha=160):
        """Escurece o campo de jogo."""
        overlay = pygame.Surface((Config.FIELD_W, Config.FIELD_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, Config.FIELD_Y))

    def _draw_menu(self):
        """Desenha menu principal."""
        self._dim_field(150)

        title = "SNAKE - MECATRONICA"
        Utils.draw_text_outline_center(
            self.screen,
            title,
            Config.WIN_W // 2,
            Config.FIELD_Y + 70,
            (255, 255, 255),
            (0, 0, 0),
            self.fonts["huge"],
        )

        opts = [
            "1 - JOGAR",
            "2 - RANKING",
            "3 - OPÇÕES",
            "4 - TELA (Resolução)",
            "5 - SAIR",
        ]

        y = Config.FIELD_Y + 150
        for i, opt in enumerate(opts):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                opt,
                Config.WIN_W // 2 - 160,
                y + i * 44,
                (255, 255, 255),
            )

        sub = "Durante o jogo: 0 - Pausar | ESPAÇO - Atirar"
        Utils.draw_text(
            self.screen,
            self.fonts["small"],
            sub,
            Config.WIN_W // 2 - self.fonts["small"].size(sub)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H - 36,
            (200, 200, 200),
        )

    def _draw_name_entry(self):
        """Desenha tela de entrada de nome."""
        self._dim_field(160)

        title = "DIGITE SEU NOME"
        Utils.draw_text_outline_center(
            self.screen,
            title,
            Config.WIN_W // 2,
            Config.FIELD_Y + 70,
            (255, 255, 255),
            (0, 0, 0),
            self.fonts["big"],
        )

        # Caixa de texto
        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            (Config.WIN_W // 2 - 200, Config.FIELD_Y + 140, 400, 50),
            border_radius=5,
        )
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (Config.WIN_W // 2 - 200, Config.FIELD_Y + 140, 400, 50),
            2,
            border_radius=5,
        )

        # Texto digitado
        if self.player_name:
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                self.player_name,
                Config.WIN_W // 2 - self.fonts["normal"].size(self.player_name)[0] // 2,
                Config.FIELD_Y + 150,
                (255, 255, 255),
            )
        else:
            placeholder = "Clique aqui e digite..."
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                placeholder,
                Config.WIN_W // 2 - self.fonts["normal"].size(placeholder)[0] // 2,
                Config.FIELD_Y + 150,
                (150, 150, 150),
            )

        # Cursor piscante
        if int(self.tick * 2) % 2 == 0:
            cursor_x = (
                Config.WIN_W // 2
                + self.fonts["normal"].size(self.player_name)[0] // 2
                + 2
            )
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (cursor_x, Config.FIELD_Y + 150),
                (cursor_x, Config.FIELD_Y + 180),
                2,
            )

        # Instruções
        hint = "ENTER para confirmar | ESC para voltar"
        Utils.draw_text(
            self.screen,
            self.fonts["small"],
            hint,
            Config.WIN_W // 2 - self.fonts["small"].size(hint)[0] // 2,
            Config.FIELD_Y + 220,
            (200, 200, 200),
        )

    def _draw_leaderboard(self):
        """Desenha ranking."""
        self._dim_field(160)

        title = "RANKING - MELHORES TEMPOS"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            title,
            Config.WIN_W // 2 - self.fonts["big"].size(title)[0] // 2,
            Config.FIELD_Y + 28,
            (255, 255, 255),
        )

        lb = self.score_manager.load_leaderboard()
        top = lb[:10]
        y = Config.FIELD_Y + 100

        if not top:
            msg = "Ainda não há tempos salvos."
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                msg,
                Config.WIN_W // 2 - self.fonts["normal"].size(msg)[0] // 2,
                y,
                (255, 255, 255),
            )
        else:
            cx = Config.WIN_W // 2 - 260
            tx = Config.WIN_W // 2 + 140
            Utils.draw_text(
                self.screen, self.fonts["normal"], "Jogador", cx, y, (255, 255, 255)
            )
            Utils.draw_text(
                self.screen, self.fonts["normal"], "Tempo", tx, y, (255, 255, 255)
            )
            y += 32

            for i, rec in enumerate(top, 1):
                Utils.draw_text(
                    self.screen,
                    self.fonts["small"],
                    f"{i:2d}. {rec.get('name', 'Jogador')}",
                    cx,
                    y,
                    (255, 255, 255),
                )
                Utils.draw_text(
                    self.screen,
                    self.fonts["small"],
                    Utils.fmt_secs(rec.get("seconds", 0.0)),
                    tx,
                    y,
                    (255, 255, 255),
                )
                y += 24

        tip = "ESC para voltar"
        Utils.draw_text(
            self.screen,
            self.fonts["small"],
            tip,
            Config.WIN_W // 2 - self.fonts["small"].size(tip)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H - 36,
            (255, 255, 255),
        )

    def _draw_options(self):
        """Desenha menu de opções."""
        self._dim_field(170)

        title = "OPÇÕES"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            title,
            Config.WIN_W // 2 - self.fonts["big"].size(title)[0] // 2,
            Config.FIELD_Y + 40,
            (255, 255, 255),
        )

        opts = ["1 - Tema", "2 - Fundo (Imagem)", "3 - Música", "ESC - Voltar"]

        y = Config.FIELD_Y + 120
        for i, opt in enumerate(opts):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                opt,
                Config.WIN_W // 2 - 160,
                y + i * 40,
                (255, 255, 255),
            )

    def _draw_theme_menu(self):
        """Desenha menu de temas."""
        self._dim_field(170)

        title = "TEMA"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            title,
            Config.WIN_W // 2 - self.fonts["big"].size(title)[0] // 2,
            Config.FIELD_Y + 40,
            (255, 255, 255),
        )

        opts = [
            "1 - CLEAN (Cobra d'água)",
            "2 - NEON (Cobra coral)",
            "3 - RETRO70 (Cascavel)",
            "ESC - Voltar",
        ]

        y = Config.FIELD_Y + 120
        for i, opt in enumerate(opts):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                opt,
                Config.WIN_W // 2 - 160,
                y + i * 40,
                (255, 255, 255),
            )

    def _draw_bg_menu(self):
        """Desenha menu de fundo."""
        self._dim_field(170)

        title = "FUNDO (IMAGEM)"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            title,
            Config.WIN_W // 2 - self.fonts["big"].size(title)[0] // 2,
            Config.FIELD_Y + 40,
            (255, 255, 255),
        )

        opts = ["1 - Carregar imagem", "2 - Remover imagem (padrão)", "ESC - Voltar"]

        y = Config.FIELD_Y + 120
        for i, opt in enumerate(opts):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                opt,
                Config.WIN_W // 2 - 220,
                y + i * 40,
                (255, 255, 255),
            )

    def _draw_music_menu(self):
        """Desenha menu de música."""
        self._dim_field(170)

        title = "MÚSICA"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            title,
            Config.WIN_W // 2 - self.fonts["big"].size(title)[0] // 2,
            Config.FIELD_Y + 40,
            (255, 255, 255),
        )

        st = "Ligada" if self.audio_manager.enabled else "Desligada"
        Utils.draw_text(
            self.screen,
            self.fonts["normal"],
            f"Estado atual: {st}",
            Config.WIN_W // 2 - 160,
            Config.FIELD_Y + 90,
            (255, 255, 255),
        )

        opts = ["1 - Ligar", "2 - Desligar", "ESC - Voltar"]

        y = Config.FIELD_Y + 140
        for i, opt in enumerate(opts):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                opt,
                Config.WIN_W // 2 - 140,
                y + i * 40,
                (255, 255, 255),
            )

    def _draw_screen_menu(self):
        """Desenha menu de resolução."""
        self._dim_field(170)

        title = "TELA - RESOLUÇÃO"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            title,
            Config.WIN_W // 2 - 180,
            Config.FIELD_Y + 40,
            (255, 255, 255),
        )

        opts = ["1 - 800x600", "2 - 1280x720", "3 - 1600x900", "ESC - Voltar"]

        y = Config.FIELD_Y + 120
        for i, opt in enumerate(opts):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                opt,
                Config.WIN_W // 2 - 140,
                y + i * 40,
                (255, 255, 255),
            )

    def _draw_level(self):
        """Desenha transição de fase."""
        txt = f"Fase {self.phase}!"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            txt,
            Config.WIN_W // 2 - self.fonts["big"].size(txt)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 - 22,
            (0, 255, 180),
        )

        sub = "ENTER para continuar"
        Utils.draw_text(
            self.screen,
            self.fonts["normal"],
            sub,
            Config.WIN_W // 2 - self.fonts["normal"].size(sub)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 + 24,
            (238, 240, 243),
        )

    def _draw_game_over(self):
        """Desenha tela de game over."""
        self._dim_field(100)

        msg = "VOCÊ MORREU! 😵💀"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            msg,
            Config.WIN_W // 2 - self.fonts["big"].size(msg)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 - 64,
            (235, 70, 70),
        )

        cause_str = f"Causa: {self.death_reason}"
        Utils.draw_text(
            self.screen,
            self.fonts["normal"],
            cause_str,
            Config.WIN_W // 2 - self.fonts["normal"].size(cause_str)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 - 20,
            (238, 240, 243),
        )

        hint = "1 Repetir | 2 Novo jogo | ESC Menu"
        Utils.draw_text(
            self.screen,
            self.fonts["small"],
            hint,
            Config.WIN_W // 2 - self.fonts["small"].size(hint)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 + 30,
            (238, 240, 243),
        )

    def _draw_victory(self):
        """Desenha tela de vitória."""
        self._dim_field(100)

        total = self.timer.elapsed()
        win = f"CAMPEÃO! Tempo: {Utils.fmt_secs(total)}"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            win,
            Config.WIN_W // 2 - self.fonts["big"].size(win)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 - 24,
            (0, 255, 180),
        )

        hint = "1 Jogar de novo | ESC Menu"
        Utils.draw_text(
            self.screen,
            self.fonts["small"],
            hint,
            Config.WIN_W // 2 - self.fonts["small"].size(hint)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 + 24,
            (238, 240, 243),
        )

    def _draw_pause(self):
        """Desenha menu de pausa."""
        self._dim_field(140)

        txt = "PAUSADO"
        Utils.draw_text(
            self.screen,
            self.fonts["big"],
            txt,
            Config.WIN_W // 2 - self.fonts["big"].size(txt)[0] // 2,
            Config.FIELD_Y + Config.FIELD_H // 2 - 48,
            (255, 255, 255),
        )

        opts = [
            "1 - Continuar",
            "2 - Reiniciar fase",
            "3 - Opções",
            "4 - Menu principal",
        ]
        y = Config.FIELD_Y + Config.FIELD_H // 2 + 4
        for i, opt in enumerate(opts):
            Utils.draw_text(
                self.screen,
                self.fonts["normal"],
                opt,
                Config.WIN_W // 2 - 120,
                y + i * 36,
                (238, 240, 243),
            )

    # ...existing code...


def main():
    """Função principal."""
    try:
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")
        print("Certifique-se de que todos os módulos necessários estão disponíveis.")
        sys.exit(1)


if __name__ == "__main__":
    main()
