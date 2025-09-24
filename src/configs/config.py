"""Configurações centralizadas do jogo Snake."""


class Config:
    # Dimensões
    CELL = 24
    GRID_W, GRID_H = 40, 26
    FIELD_W, FIELD_H = GRID_W * CELL, GRID_H * CELL
    TOP_PANEL_H = 100
    WIN_W, WIN_H = FIELD_W, TOP_PANEL_H + FIELD_H
    FIELD_Y = TOP_PANEL_H

    # Gameplay
    TARGET_PHRASE = "MECATRONICA"
    SEQUENCE = [c for c in TARGET_PHRASE if not c.isspace()]
    NCHARS = len(SEQUENCE)
    BASE_SPEED = {1: 3.2, 2: 4.8, 3: 6.2}
    PHASE_CAP = {1: 4.6, 2: 6.4, 3: 8.0}
    INC_PER_CHAR = 0.36
    GLOBAL_CAP = 9.8

    # Inimigos
    SPIDERS_BY_PHASE = {1: 2, 2: 2, 3: 2}
    SPIDER_STEP_BY_PHASE = {1: 0.50, 2: 0.40, 3: 0.33}
    DROP_RATE_BY_PHASE = {1: 0.20, 2: 0.28, 3: 0.36}

    # Power-ups
    POWER_UP_SPAWN_TIME = 15.0

    # Animação da cobra
    SLITHER_SPEED = 7.6
    SLITHER_AMPL = 4.8
    HEAD_SWAY = 2.6

    # Arquivos
    LB_PATH = "leaderboard.json"
    BG_CFG_PATH = "theme_bg.json"

    # Cores padrão
    DARK_PANEL = (12, 14, 18)
