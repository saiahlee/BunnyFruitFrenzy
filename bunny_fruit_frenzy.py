#!/usr/bin/env python3
"""
Bunny Fruit Frenzy
A galaxy-style fruit collecting game featuring a pink rabbit!

Controls:
  Arrow keys - Move bunny
  P / ESC    - Pause / Resume (in-game)
  SPACE/ENTER - Start / Restart

Objective: Eat fruits, avoid the cockroach, collect powerups!
Requirements: pip install pygame numpy
"""

import json
import math
import os
import random
import sys

import numpy as np
import pygame

# ─────────────────────────────────────────────
# PATHS (works for both source and PyInstaller bundles)
# ─────────────────────────────────────────────
def app_data_dir():
    """A writable directory for storing high score, etc."""
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support/BunnyFruitFrenzy")
    elif sys.platform.startswith("win"):
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                            "BunnyFruitFrenzy")
    else:
        base = os.path.expanduser("~/.local/share/BunnyFruitFrenzy")
    os.makedirs(base, exist_ok=True)
    return base


HIGHSCORE_PATH = os.path.join(app_data_dir(), "highscore.json")


def load_highscore():
    try:
        with open(HIGHSCORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("best_score", 0))
    except Exception:
        return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_PATH, "w", encoding="utf-8") as f:
            json.dump({"best_score": int(score)}, f)
    except Exception:
        pass


# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(8)

# Dedicated channels to prevent music overlap
BGM_CHANNEL = pygame.mixer.Channel(0)
SFX_CHANNEL1 = pygame.mixer.Channel(1)
SFX_CHANNEL2 = pygame.mixer.Channel(2)
SFX_CHANNEL3 = pygame.mixer.Channel(3)

WIDTH, HEIGHT = 900, 650
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bunny Fruit Frenzy")
clock = pygame.time.Clock()

# ─────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────
OCHRE_BG       = (204, 163, 93)
OCHRE_DARK     = (180, 140, 70)
GROUND_COLOR   = (139, 110, 60)
GROUND_GRASS   = (120, 160, 60)
PINK           = (255, 140, 170)
PINK_LIGHT     = (255, 180, 200)
PINK_DARK      = (220, 100, 130)
PINK_EAR_IN    = (255, 160, 180)
WHITE          = (255, 255, 255)
BLACK          = (0, 0, 0)
RED            = (220, 50, 50)
DARK_BROWN     = (80, 45, 20)
BROWN_BODY     = (100, 60, 30)
BROWN_LEG      = (70, 40, 15)
APPLE_RED      = (220, 40, 40)
APPLE_GREEN    = (80, 180, 60)
BANANA_YELLOW  = (255, 220, 60)
BANANA_BROWN   = (140, 100, 40)
GRAPE_PURPLE   = (140, 50, 160)
GRAPE_LIGHT    = (180, 80, 200)
ORANGE_COLOR   = (255, 160, 30)
ORANGE_DARK    = (220, 130, 20)
STRAWBERRY_RED = (230, 50, 60)
STRAWBERRY_SEED= (255, 230, 100)
CHERRY_RED     = (200, 30, 50)
CHERRY_DARK    = (160, 20, 40)
WATERMELON_GRN = (60, 150, 50)
WATERMELON_RED = (240, 70, 80)
STAR_YELLOW    = (255, 255, 100)
GOLD           = (255, 215, 0)
HEART_RED      = (240, 50, 70)
SPEED_BLUE     = (60, 160, 255)
UI_PANEL       = (40, 25, 10)

# ─────────────────────────────────────────────
# SOUND GENERATION
# ─────────────────────────────────────────────
def generate_tone(freq, duration, volume=0.3, wave='square'):
    sr = 44100
    n = int(sr * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    if wave == 'square':
        sig = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == 'triangle':
        sig = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    elif wave == 'sine':
        sig = np.sin(2 * np.pi * freq * t)
    else:
        sig = np.sin(2 * np.pi * freq * t)
    att = int(n * 0.05)
    rel = int(n * 0.15)
    env = np.ones(n)
    if att > 0: env[:att] = np.linspace(0, 1, att)
    if rel > 0: env[-rel:] = np.linspace(1, 0, rel)
    sig = sig * env * volume
    stereo = np.column_stack((sig, sig))
    return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))


def _build_bgm(bpm):
    sr = 44100
    beat = 60.0 / bpm
    total_beats = 32
    n_samples = int(sr * beat * total_beats)
    out = np.zeros(n_samples, dtype=np.float64)

    melody = [
        ('E5', 0.5), ('G5', 0.5), ('A5', 0.5), ('B5', 0.5),
        ('A5', 0.5), ('G5', 0.5), ('E5', 1.0),
        ('D5', 0.5), ('E5', 0.5), ('G5', 0.5), ('A5', 0.5),
        ('G5', 0.5), ('E5', 0.5), ('D5', 1.0),
        ('E5', 0.5), ('G5', 0.5), ('A5', 0.5), ('B5', 0.5),
        ('D6', 0.5), ('B5', 0.5), ('A5', 1.0),
        ('G5', 0.5), ('A5', 0.5), ('G5', 0.5), ('E5', 0.5),
        ('D5', 0.5), ('E5', 0.5), ('E5', 1.0),
    ]
    nf = {'C4':261.6,'D4':293.7,'E4':329.6,'F4':349.2,'G4':392.0,
          'A4':440.0,'B4':493.9,'C5':523.3,'D5':587.3,'E5':659.3,
          'F5':698.5,'G5':784.0,'A5':880.0,'B5':987.8,
          'C6':1046.5,'D6':1174.7,'E6':1318.5}

    pos = 0.0
    for note, db in melody:
        freq = nf.get(note, 440)
        dur = db * beat
        n = int(sr * dur)
        s = int(sr * pos)
        if s + n > n_samples: n = n_samples - s
        t = np.linspace(0, dur, n, endpoint=False)
        sig = np.sign(np.sin(2*np.pi*freq*t))*0.15
        sig += np.sign(np.sin(2*np.pi*freq*2*t))*0.05
        env = np.ones(n)
        a = min(int(n*0.05), n)
        r = min(int(n*0.3), n)
        if a>0: env[:a] = np.linspace(0,1,a)
        if r>0: env[-r:] = np.linspace(1,0.1,r)
        out[s:s+n] += sig*env
        pos += dur

    bass = [('E4',1),('E4',1),('G4',1),('A4',1),
            ('D4',1),('D4',1),('G4',1),('G4',1),
            ('E4',1),('E4',1),('G4',1),('A4',1),
            ('D4',1),('D4',1),('E4',1),('E4',1)]*2
    pos = 0.0
    for note, db in bass:
        freq = nf.get(note,220)/2
        dur = db*beat; n = int(sr*dur); s = int(sr*pos)
        if s+n > n_samples: n = n_samples-s
        t = np.linspace(0,dur,n,endpoint=False)
        sig = (2*np.abs(2*(t*freq-np.floor(t*freq+0.5)))-1)*0.12
        env = np.ones(n)
        a = min(int(n*0.02),n); r = min(int(n*0.2),n)
        if a>0: env[:a] = np.linspace(0,1,a)
        if r>0: env[-r:] = np.linspace(1,0,r)
        out[s:s+n] += sig*env
        pos += dur

    for i in range(total_beats):
        if i%2==0:
            s = int(sr*i*beat); dur=0.08; n=min(int(sr*dur),n_samples-s)
            if n>0:
                t=np.linspace(0,dur,n,endpoint=False)
                out[s:s+n] += np.sin(2*np.pi*150*np.exp(-t*30)*t)*0.2*np.exp(-t*25)
        if i%2==1:
            s = int(sr*i*beat); dur=0.04; n=min(int(sr*dur),n_samples-s)
            if n>0:
                out[s:s+n] += np.random.randn(n)*0.06*np.exp(-np.linspace(0,1,n)*15)

    pk = np.max(np.abs(out))
    if pk > 0: out = out/pk*0.5
    stereo = np.column_stack((out,out))
    return pygame.sndarray.make_sound((stereo*32767).astype(np.int16))


def generate_gameover_bgm():
    """Sad, slow game-over melody."""
    sr = 44100
    bpm = 70
    beat = 60.0/bpm
    melody = [
        ('E5',1),('D5',1),('C5',1.5),('B4',0.5),
        ('A4',1),('G4',1),('A4',2),
        ('E4',1),('D4',1),('C4',2),
    ]
    nf = {'C4':261.6,'D4':293.7,'E4':329.6,'F4':349.2,'G4':392.0,
          'A4':440.0,'B4':493.9,'C5':523.3,'D5':587.3,'E5':659.3}
    total_beats = sum(d for _,d in melody)
    n_samples = int(sr * beat * total_beats)
    out = np.zeros(n_samples, dtype=np.float64)
    pos = 0.0
    for note, db in melody:
        freq = nf.get(note,440)
        dur = db*beat; n = int(sr*dur); s = int(sr*pos)
        if s+n > n_samples: n = n_samples-s
        t = np.linspace(0,dur,n,endpoint=False)
        sig = (2*np.abs(2*(t*freq-np.floor(t*freq+0.5)))-1)*0.18
        env = np.ones(n)
        a = min(int(n*0.08),n); r = min(int(n*0.4),n)
        if a>0: env[:a] = np.linspace(0,1,a)
        if r>0: env[-r:] = np.linspace(1,0,r)
        out[s:s+n] += sig*env
        pos += dur
    t_all = np.linspace(0, beat*total_beats, n_samples, endpoint=False)
    out += np.sin(2*np.pi*65*t_all)*0.06*np.linspace(1,0,n_samples)

    pk = np.max(np.abs(out))
    if pk>0: out = out/pk*0.35
    stereo = np.column_stack((out,out))
    return pygame.sndarray.make_sound((stereo*32767).astype(np.int16))


def generate_life_sfx():
    """Bright ascending arpeggio for gaining a life."""
    sr = 44100
    notes = [523.3, 659.3, 784.0, 1046.5]  # C5 E5 G5 C6
    total = int(sr * 0.5)
    out = np.zeros(total, dtype=np.float64)
    for i, freq in enumerate(notes):
        start = int(sr * i * 0.1)
        dur = 0.2
        n = min(int(sr * dur), total - start)
        if n <= 0: continue
        t = np.linspace(0, dur, n, endpoint=False)
        sig = np.sin(2*np.pi*freq*t)*0.25
        sig += np.sign(np.sin(2*np.pi*freq*t))*0.08
        env = np.ones(n)
        a = min(int(n*0.05), n)
        r = min(int(n*0.4), n)
        if a>0: env[:a] = np.linspace(0,1,a)
        if r>0: env[-r:] = np.linspace(1,0,r)
        out[start:start+n] += sig*env
    pk = np.max(np.abs(out))
    if pk>0: out = out/pk*0.4
    stereo = np.column_stack((out,out))
    return pygame.sndarray.make_sound((stereo*32767).astype(np.int16))


def generate_speed_sfx():
    """Whooshing speed-up sound with rising pitch."""
    sr = 44100
    dur = 0.4
    n = int(sr*dur)
    t = np.linspace(0, dur, n, endpoint=False)
    freq = 400 + 1200*t/dur
    sig = np.sign(np.sin(2*np.pi*np.cumsum(freq)/sr))*0.2
    sig += np.random.randn(n)*0.04
    env = np.ones(n)
    env[:int(n*0.05)] = np.linspace(0,1,int(n*0.05))
    env[-int(n*0.3):] = np.linspace(1,0,int(n*0.3))
    out = sig*env*0.35
    stereo = np.column_stack((out,out))
    return pygame.sndarray.make_sound((stereo*32767).astype(np.int16))


def generate_levelup_sfx():
    """Triumphant chime when difficulty level increases."""
    sr = 44100
    notes = [(659.3, 0.0), (784.0, 0.08), (1046.5, 0.16), (1318.5, 0.24)]
    total = int(sr * 0.7)
    out = np.zeros(total, dtype=np.float64)
    for freq, st in notes:
        s = int(sr * st)
        dur = 0.45
        n = min(int(sr * dur), total - s)
        if n <= 0: continue
        t = np.linspace(0, dur, n, endpoint=False)
        sig = np.sin(2*np.pi*freq*t)*0.3
        sig += np.sin(2*np.pi*freq*2*t)*0.1
        env = np.exp(-t*3)
        out[s:s+n] += sig*env
    pk = np.max(np.abs(out))
    if pk>0: out = out/pk*0.4
    stereo = np.column_stack((out,out))
    return pygame.sndarray.make_sound((stereo*32767).astype(np.int16))


try:
    eat_sound = generate_tone(880, 0.08, 0.25, 'square')
    eat_sound2 = generate_tone(1100, 0.06, 0.2, 'sine')
    hit_sound = generate_tone(150, 0.3, 0.3, 'square')
    countdown_sound = generate_tone(660, 0.15, 0.2, 'triangle')
    gameover_sound = generate_tone(220, 0.5, 0.3, 'triangle')
    start_sound = generate_tone(523, 0.2, 0.25, 'square')
    life_sfx = generate_life_sfx()
    speed_sfx = generate_speed_sfx()
    levelup_sfx = generate_levelup_sfx()
    bgm_normal = _build_bgm(150)
    bgm_fast = _build_bgm(300)
    bgm_gameover = generate_gameover_bgm()
except Exception:
    eat_sound = eat_sound2 = hit_sound = countdown_sound = None
    gameover_sound = start_sound = life_sfx = speed_sfx = None
    levelup_sfx = None
    bgm_normal = bgm_fast = bgm_gameover = None


def play_bgm(sound, loops=-1):
    BGM_CHANNEL.stop()
    if sound:
        BGM_CHANNEL.play(sound, loops=loops)


def play_sfx(sound):
    if sound:
        for ch in (SFX_CHANNEL1, SFX_CHANNEL2, SFX_CHANNEL3):
            if not ch.get_busy():
                ch.play(sound)
                return
        SFX_CHANNEL1.play(sound)


# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
def find_korean_font():
    for p in [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleSDGothicNeo.ttc",
        "/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/System/Library/Fonts/NanumGothic.ttc",
        "/Library/Fonts/NanumGothic.ttc",
        "C:\\Windows\\Fonts\\malgun.ttf",
        "C:\\Windows\\Fonts\\malgunbd.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]:
        if os.path.exists(p): return p
    return None

_kr = find_korean_font()
def _font(sz):
    if _kr:
        try: return pygame.font.Font(_kr, sz)
        except: pass
    return pygame.font.SysFont(None, sz, bold=True)

font_large  = _font(52)
font_medium = _font(32)
font_small  = _font(24)
font_score  = _font(28)
font_timer  = _font(40)
font_title  = _font(48)
font_tiny   = _font(20)

# ─────────────────────────────────────────────
# DRAWING HELPERS
# ─────────────────────────────────────────────
def draw_small_apple_icon(surf, x, y, size=12):
    cx, cy = int(x), int(y)
    pygame.draw.circle(surf, APPLE_RED, (cx, cy), size)
    pygame.draw.circle(surf, (240, 80, 80), (cx-2, cy-2), size//3)
    pygame.draw.line(surf, BANANA_BROWN, (cx, cy-size), (cx+1, cy-size-5), 2)
    pygame.draw.ellipse(surf, APPLE_GREEN, (cx, cy-size-5, 6, 4))
    pygame.draw.circle(surf, (255,200,200), (cx-size//3, cy-size//3), max(1,size//5))


def draw_small_grape_icon(surf, x, y, size=12):
    cx, cy = int(x), int(y)
    r = max(3, size//3)
    offsets = [(0,0),(-r,-r),(r,-r),(-r-1,r//2),(r+1,r//2),(0,r),(0,-r*2+2)]
    for dx, dy in offsets:
        pygame.draw.circle(surf, GRAPE_PURPLE, (cx+dx, cy+dy), r)
        pygame.draw.circle(surf, GRAPE_LIGHT, (cx+dx-1, cy+dy-1), max(1,r//2))
    pygame.draw.line(surf, APPLE_GREEN, (cx, cy-r*2), (cx, cy-r*3), 2)
    pygame.draw.ellipse(surf, APPLE_GREEN, (cx-1, cy-r*3-2, 5, 3))


def draw_heart(surf, x, y, size=12, color=HEART_RED):
    cx, cy = int(x), int(y)
    s = size
    r = max(2, s*2//5)
    pygame.draw.circle(surf, color, (cx - r, cy - r//2), r)
    pygame.draw.circle(surf, color, (cx + r, cy - r//2), r)
    pts = [(cx - r - r, cy), (cx, cy + s), (cx + r + r, cy)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.circle(surf, (255,200,210), (cx - r - 1, cy - r//2 - 1), max(1, r//3))


def draw_speed_icon(surf, x, y, size=12):
    cx, cy = int(x), int(y)
    s = size
    pts = [
        (cx - s//4, cy - s//2),
        (cx + s//3, cy - s//8),
        (cx + s//8, cy + s//8),
        (cx + s//2, cy - s//8),
        (cx, cy + s//2),
        (cx + s//6, cy + s//8),
        (cx - s//6, cy + s//8),
    ]
    pygame.draw.polygon(surf, (255, 230, 80), pts)
    pygame.draw.polygon(surf, SPEED_BLUE, pts, 2)
    inner = [(cx-s//8, cy-s//4), (cx+s//6, cy-s//10), (cx, cy+s//4)]
    pygame.draw.polygon(surf, (255,255,200), inner)


def draw_trophy_icon(surf, x, y, size=14):
    cx, cy = int(x), int(y)
    pygame.draw.rect(surf, GOLD, (cx-size//2, cy-size//2, size, int(size*0.7)), border_radius=3)
    pygame.draw.rect(surf, (255,235,100), (cx-size//4, cy-size//3, size//2, size//3))
    pygame.draw.rect(surf, GOLD, (cx-size//3, cy+int(size*0.2), size*2//3, 4))


def draw_rabbit(surf, x, y, size=40, facing_left=False, frame=0):
    s = size; cx, cy = int(x), int(y)
    hop = int(math.sin(frame*0.3)*3)

    body = pygame.Rect(cx-s//2, cy-s//3+hop, s, int(s*0.7))
    pygame.draw.ellipse(surf, PINK, body)
    pygame.draw.ellipse(surf, PINK_DARK, body, 2)
    belly = pygame.Rect(cx-s//4, cy-s//6+hop, s//2, int(s*0.4))
    pygame.draw.ellipse(surf, PINK_LIGHT, belly)

    hx, hy = cx, cy-s//2+hop
    pygame.draw.circle(surf, PINK, (hx, hy), s//3)
    pygame.draw.circle(surf, PINK_DARK, (hx, hy), s//3, 2)

    for side in (-1, 1):
        ex = hx+side*s//5; ey = hy-s//2
        ep = [(ex, ey-s//2),(ex-s//6, ey+s//6),(ex+s//6, ey+s//6)]
        pygame.draw.polygon(surf, PINK, ep)
        pygame.draw.polygon(surf, PINK_DARK, ep, 2)
        ip = [(ex, ey-s//3),(ex-s//10, ey+s//10),(ex+s//10, ey+s//10)]
        pygame.draw.polygon(surf, PINK_EAR_IN, ip)

    ed = -1 if facing_left else 1
    for ex_pos in (hx-s//7, hx+s//7):
        eey = hy-2
        pygame.draw.circle(surf, BLACK, (ex_pos+ed, eey), 3)
        pygame.draw.circle(surf, WHITE, (ex_pos+ed+1, eey-1), 1)

    bl = pygame.Surface((10,6), pygame.SRCALPHA)
    pygame.draw.ellipse(bl, (255,130,150,120), (0,0,10,6))
    surf.blit(bl, (hx-s//7-8, hy+2))
    surf.blit(bl, (hx+s//7+1, hy+2))

    pygame.draw.circle(surf, PINK_DARK, (hx, hy+3), 2)
    pygame.draw.arc(surf, PINK_DARK, (hx-4, hy+2, 8, 6), 3.14, 6.28, 1)

    tx = cx+(s//2 if not facing_left else -s//2)
    pygame.draw.circle(surf, WHITE, (tx, cy+hop), s//7)

    fy = cy+int(s*0.35)+hop
    pygame.draw.ellipse(surf, PINK_DARK, (cx-s//3, fy-3, s//4, 8))
    pygame.draw.ellipse(surf, PINK_DARK, (cx+s//8, fy-3, s//4, 8))


def draw_cockroach(surf, x, y, size=35, frame=0):
    s = size; cx, cy = int(x), int(y)
    w = int(math.sin(frame*0.2)*2)

    bd = pygame.Rect(cx-s//2, cy-s//4+w, s, s//2)
    pygame.draw.ellipse(surf, DARK_BROWN, bd)
    sh = pygame.Rect(cx-s//2+3, cy-s//4+3+w, s-6, s//2-6)
    pygame.draw.ellipse(surf, BROWN_BODY, sh)
    pygame.draw.line(surf, DARK_BROWN, (cx, cy-s//4+4+w), (cx, cy+s//4-4+w), 1)

    hx, hy = cx, cy-s//3+w
    pygame.draw.circle(surf, DARK_BROWN, (hx, hy), s//5)

    aw = int(math.sin(frame*0.4)*4)
    pygame.draw.line(surf, BROWN_LEG, (hx-3, hy-s//6), (hx-s//3+aw, hy-s//2), 2)
    pygame.draw.line(surf, BROWN_LEG, (hx+3, hy-s//6), (hx+s//3-aw, hy-s//2), 2)

    for i in range(3):
        ly = cy-s//8+i*(s//5)+w
        la = int(math.sin(frame*0.3+i*2)*3)
        pygame.draw.line(surf, BROWN_LEG, (cx-s//3, ly), (cx-s//2-6-la, ly+8), 2)
        pygame.draw.line(surf, BROWN_LEG, (cx+s//3, ly), (cx+s//2+6+la, ly+8), 2)

    pygame.draw.circle(surf, RED, (hx-3, hy-1), 2)
    pygame.draw.circle(surf, RED, (hx+3, hy-1), 2)
    pygame.draw.circle(surf, (255,200,200), (hx-2, hy-2), 1)
    pygame.draw.circle(surf, (255,200,200), (hx+4, hy-2), 1)


def draw_fruit(surf, x, y, fruit_type, size=20, frame=0):
    cx, cy = int(x), int(y)
    s = size
    bob = int(math.sin(frame*0.1+x*0.05)*2)
    cy += bob

    if fruit_type == 'apple':
        pygame.draw.circle(surf, APPLE_RED, (cx,cy), s)
        pygame.draw.circle(surf, (240,80,80), (cx-3,cy-3), s//3)
        pygame.draw.line(surf, BANANA_BROWN, (cx,cy-s), (cx+2,cy-s-6), 2)
        pygame.draw.ellipse(surf, APPLE_GREEN, (cx+1,cy-s-6, 8, 5))
        pygame.draw.circle(surf, (255,200,200), (cx-s//3,cy-s//3), 3)

    elif fruit_type == 'banana':
        bs = s * 2
        pts = []
        for i in range(20):
            angle = math.pi*0.3+i*0.07
            bx = cx+int(math.cos(angle)*bs*0.6)-bs//4
            by = cy+int(math.sin(angle)*bs*0.4)-bs//6
            pts.append((bx, by))
        if len(pts) > 2:
            pygame.draw.lines(surf, BANANA_YELLOW, False, pts, max(4,bs//4))
            pygame.draw.lines(surf, (255,240,100), False, pts, max(2,bs//6))
        pygame.draw.circle(surf, BANANA_BROWN, pts[0], 4)
        pygame.draw.circle(surf, BANANA_BROWN, pts[-1], 4)

    elif fruit_type == 'grape':
        gs = s * 2
        r = max(4, gs//4)
        offsets = [(0,0),(-r,-r),(r,-r),(-r-2,r//2),(r+2,r//2),(0,r),(0,-r*2+3)]
        for dx, dy in offsets:
            pygame.draw.circle(surf, GRAPE_PURPLE, (cx+dx,cy+dy), r)
            pygame.draw.circle(surf, GRAPE_LIGHT, (cx+dx-1,cy+dy-1), max(1,r//2))
        pygame.draw.line(surf, APPLE_GREEN, (cx,cy-r*2), (cx,cy-r*3), 2)
        pygame.draw.ellipse(surf, APPLE_GREEN, (cx-2,cy-r*3-3, 7, 4))

    elif fruit_type == 'orange':
        pygame.draw.circle(surf, ORANGE_COLOR, (cx,cy), s)
        pygame.draw.circle(surf, ORANGE_DARK, (cx,cy), s, 2)
        pygame.draw.circle(surf, (255,180,60), (cx+2,cy+3), s//4)
        pygame.draw.line(surf, APPLE_GREEN, (cx,cy-s), (cx,cy-s-4), 2)
        pygame.draw.ellipse(surf, APPLE_GREEN, (cx-4,cy-s-6, 8, 5))
        pygame.draw.circle(surf, (255,220,130), (cx-s//3,cy-s//3), 3)

    elif fruit_type == 'strawberry':
        p = [(cx,cy-s),(cx-s,cy+s//2),(cx,cy+s),(cx+s,cy+s//2)]
        pygame.draw.polygon(surf, STRAWBERRY_RED, p)
        pygame.draw.polygon(surf, (200,40,50), p, 2)
        for i in range(5):
            sx = cx+random.Random(int(x)+i).randint(-s//2,s//2)
            sy = cy+random.Random(int(y)+i).randint(-s//3,s//2)
            pygame.draw.circle(surf, STRAWBERRY_SEED, (sx,sy), 1)
        pygame.draw.ellipse(surf, APPLE_GREEN, (cx-s//2,cy-s-2, s, 6))

    elif fruit_type == 'cherry':
        pygame.draw.circle(surf, CHERRY_RED, (cx-s//2,cy), s//2+2)
        pygame.draw.circle(surf, CHERRY_DARK, (cx-s//2,cy), s//2+2, 2)
        pygame.draw.circle(surf, CHERRY_RED, (cx+s//2,cy+2), s//2+2)
        pygame.draw.circle(surf, CHERRY_DARK, (cx+s//2,cy+2), s//2+2, 2)
        pygame.draw.line(surf, APPLE_GREEN, (cx-s//2,cy-s//2), (cx,cy-s), 2)
        pygame.draw.line(surf, APPLE_GREEN, (cx+s//2,cy-s//2+2), (cx,cy-s), 2)
        pygame.draw.circle(surf, (255,150,160), (cx-s//2-2,cy-3), 2)

    elif fruit_type == 'watermelon':
        pygame.draw.circle(surf, WATERMELON_GRN, (cx,cy), s, draw_top_left=True, draw_top_right=True)
        pygame.draw.circle(surf, WATERMELON_RED, (cx,cy), s-3, draw_top_left=True, draw_top_right=True)
        pygame.draw.rect(surf, OCHRE_BG, (cx-s,cy, s*2, s))
        pygame.draw.line(surf, WATERMELON_GRN, (cx-s,cy), (cx+s,cy), 3)
        for i in range(3):
            pygame.draw.ellipse(surf, BLACK, (cx-s//2+i*(s//2),cy-s//3, 3, 5))


def draw_star_particle(surf, x, y, size, alpha, color=STAR_YELLOW):
    s = max(1, int(size))
    ps = pygame.Surface((s*2+2, s*2+2), pygame.SRCALPHA)
    c = (*color, min(255, int(alpha)))
    cx2, cy2 = s+1, s+1
    pts = []
    for i in range(8):
        a = i*math.pi/4
        r = s if i%2==0 else s//3
        pts.append((cx2+int(math.cos(a)*r), cy2+int(math.sin(a)*r)))
    if len(pts)>=3: pygame.draw.polygon(ps, c, pts)
    surf.blit(ps, (int(x)-s-1, int(y)-s-1))


def draw_background(surf, frame):
    surf.fill(OCHRE_BG)
    for y in range(0, HEIGHT-100, 4):
        alpha = int(30*(1-y/HEIGHT))
        gs = pygame.Surface((WIDTH,4), pygame.SRCALPHA)
        gs.fill((255,230,180,alpha))
        surf.blit(gs, (0,y))
    for i in range(30):
        dx = (i*137+frame*0.3)%WIDTH
        dy = (i*89+math.sin(frame*0.02+i)*20)%(HEIGHT-120)
        alpha = int(80+40*math.sin(frame*0.05+i))
        ds = pygame.Surface((4,4), pygame.SRCALPHA)
        pygame.draw.circle(ds, (255,255,200,alpha), (2,2), 2)
        surf.blit(ds, (int(dx), int(dy)))
    gy = HEIGHT-80
    pygame.draw.rect(surf, GROUND_COLOR, (0,gy,WIDTH,80))
    for i in range(0, WIDTH, 15):
        h = 5+int(math.sin(i*0.5)*3)
        pygame.draw.line(surf, GROUND_GRASS, (i,gy), (i-3,gy-h), 2)
        pygame.draw.line(surf, GROUND_GRASS, (i+5,gy), (i+7,gy-h-2), 2)
    for i in range(3):
        pygame.draw.line(surf, OCHRE_DARK, (0,gy+20+i*20), (WIDTH,gy+20+i*20), 1)


# ─────────────────────────────────────────────
# UI LAYOUT
# ─────────────────────────────────────────────
def draw_ui(surf, score, time_left, lives, frame, speed_remaining, level):
    bar = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
    bar.fill((*UI_PANEL, 190))
    surf.blit(bar, (0, 0))

    pygame.draw.circle(surf, WHITE, (30, 25), 13, 2)
    pygame.draw.line(surf, WHITE, (30,25), (30,16), 2)
    pygame.draw.line(surf, WHITE, (30,25), (36,25), 2)
    t_txt = font_timer.render(f"{int(time_left)}", True, WHITE)
    surf.blit(t_txt, (50, 5))

    bar_x, bar_w = 110, WIDTH - 360
    pct = max(0, time_left/60.0)
    tw = int(bar_w * pct)
    tc = (100,220,100) if time_left>15 else ((255,200,50) if time_left>5 else (255,60,60))
    pygame.draw.rect(surf, (80,60,40), (bar_x, 15, bar_w, 20), border_radius=10)
    if tw > 0:
        pygame.draw.rect(surf, tc, (bar_x, 15, tw, 20), border_radius=10)
    pygame.draw.rect(surf, (200,180,140), (bar_x, 15, bar_w, 20), 2, border_radius=10)

    # Level badge (right of timer)
    lvl_x = bar_x + bar_w + 12
    lvl_bg_color = (255, 140, 60) if level >= 3 else (200, 180, 140)
    pygame.draw.rect(surf, (60, 40, 20), (lvl_x, 12, 78, 26), border_radius=6)
    pygame.draw.rect(surf, lvl_bg_color, (lvl_x, 12, 78, 26), 2, border_radius=6)
    lvl_txt = font_tiny.render(f"LV {level}", True, lvl_bg_color)
    surf.blit(lvl_txt, (lvl_x + 39 - lvl_txt.get_width()//2, 17))

    # Score (right side of top bar)
    draw_small_apple_icon(surf, WIDTH-120, 20, 11)
    s_txt = font_score.render(f"x {score}", True, GOLD)
    surf.blit(s_txt, (WIDTH-103, 10))

    # Speed indicator
    if speed_remaining > 0:
        pulse = int(180+75*math.sin(frame*0.2))
        bt = font_tiny.render(f"SPEED x2  {int(math.ceil(speed_remaining))}s", True, (60,pulse,255))
        surf.blit(bt, (WIDTH//2 - bt.get_width()//2, 38))

    # Time warning
    if time_left<=10 and int(frame*0.12)%2==0 and time_left>0:
        wt = font_small.render("서둘러!", True, RED)
        surf.blit(wt, (WIDTH//2-wt.get_width()//2, 50))

    # Lives panel
    panel_w, panel_h = 130, 36
    panel_x, panel_y = 12, HEIGHT - 70
    lp = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    lp.fill((*UI_PANEL, 170))
    pygame.draw.rect(lp, (200,180,140,200), (0,0,panel_w,panel_h), 2, border_radius=8)
    surf.blit(lp, (panel_x, panel_y))

    life_label = font_tiny.render("LIFE", True, (200,180,140))
    surf.blit(life_label, (panel_x+8, panel_y+8))

    for i in range(3):
        hx = panel_x + 58 + i * 24
        hy = panel_y + panel_h // 2
        c = HEART_RED if i < lives else (80, 55, 35)
        draw_heart(surf, hx, hy, 10, c)


# ─────────────────────────────────────────────
# PARTICLES & POPUPS
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color=STAR_YELLOW):
        self.x, self.y = x, y
        self.vx = random.uniform(-3,3)
        self.vy = random.uniform(-4,-1)
        self.life = 1.0
        self.size = random.uniform(3,7)
        self.color = color
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.05
        self.life-=0.03; self.size*=0.97
    def draw(self, surf, frame):
        if self.life>0:
            draw_star_particle(surf, self.x, self.y, self.size, int(255*self.life), self.color)


class ScorePopup:
    def __init__(self, x, y, text, color=GOLD):
        self.x, self.y, self.text, self.color = x, y, text, color
        self.life, self.vy = 1.0, -2
    def update(self):
        self.y+=self.vy; self.vy*=0.95; self.life-=0.025
    def draw(self, surf):
        if self.life>0:
            t = font_score.render(self.text, True, self.color)
            t.set_alpha(int(255*self.life))
            surf.blit(t, (int(self.x)-t.get_width()//2, int(self.y)))


class CenterBanner:
    """Big banner shown briefly in the center (e.g. "LEVEL UP!")."""
    def __init__(self, text, color=GOLD, duration=1.4):
        self.text = text
        self.color = color
        self.life = 1.0
        self.decay = 1.0 / (duration * FPS)
    def update(self):
        self.life -= self.decay
    def draw(self, surf, frame):
        if self.life <= 0:
            return
        scale = 1.0 + 0.06 * math.sin(frame * 0.2)
        t = font_large.render(self.text, True, self.color)
        if scale != 1.0:
            t = pygame.transform.rotozoom(t, 0, scale)
        t.set_alpha(int(255 * min(1.0, self.life * 1.6)))
        surf.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - t.get_height()//2))


# ─────────────────────────────────────────────
# GAME OBJECTS
# ─────────────────────────────────────────────
class Rabbit:
    def __init__(self):
        self.x, self.y = WIDTH//2, HEIGHT-130
        self.speed, self.size = 5, 40
        self.facing_left = False
        self.frame, self.hit_timer = 0, 0
    def update(self, keys, sm=1.0):
        self.frame += 1
        spd = self.speed * sm
        if keys[pygame.K_LEFT]:  self.x -= spd; self.facing_left = True
        if keys[pygame.K_RIGHT]: self.x += spd; self.facing_left = False
        if keys[pygame.K_UP]:    self.y -= spd
        if keys[pygame.K_DOWN]:  self.y += spd
        self.x = max(self.size, min(WIDTH-self.size, self.x))
        self.y = max(55+self.size, min(HEIGHT-95, self.y))
        if self.hit_timer>0: self.hit_timer-=1
    def draw(self, surf):
        if self.hit_timer>0 and self.hit_timer%6<3: return
        draw_rabbit(surf, self.x, self.y, self.size, self.facing_left, self.frame)
    def get_rect(self):
        return pygame.Rect(self.x-self.size//2, self.y-self.size//2, self.size, self.size)


class Fruit:
    TYPES = ['apple','banana','grape','orange','strawberry','cherry','watermelon']
    def __init__(self):
        self.type = random.choice(self.TYPES)
        self.size = random.randint(14,20)
        self.x = random.randint(50, WIDTH-50)
        self.y = HEIGHT-80
        self.vy = random.uniform(-1.5,-0.5)
        self.vx = random.uniform(-0.5,0.5)
        self.alive = True
        self.frame = random.randint(0,100)
    def update(self, sm=1.0):
        self.frame+=1
        self.y+=self.vy*sm; self.x+=self.vx*sm
        if self.x<30 or self.x>WIDTH-30: self.vx*=-1
        self.x+=math.sin(self.frame*0.05)*0.3*sm
        if self.y<30: self.alive=False
    def draw(self, surf):
        draw_fruit(surf, self.x, self.y, self.type, self.size, self.frame)
    def get_rect(self):
        return pygame.Rect(self.x-self.size, self.y-self.size, self.size*2, self.size*2)


class PowerUp:
    def __init__(self, kind):
        self.kind = kind
        self.x = random.randint(60, WIDTH-60)
        self.y = HEIGHT-80
        self.vy = random.uniform(-0.8,-0.3)
        self.vx = random.uniform(-0.3,0.3)
        self.alive = True
        self.frame = random.randint(0,100)
        self.size = 28
    def update(self, sm=1.0):
        self.frame+=1
        self.y+=self.vy*sm; self.x+=self.vx*sm
        if self.x<30 or self.x>WIDTH-30: self.vx*=-1
        if self.y<30: self.alive=False
    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        bob = int(math.sin(self.frame*0.08)*4)
        cy += bob
        glow = pygame.Surface((70,70), pygame.SRCALPHA)
        alpha = int(70+35*math.sin(self.frame*0.12))
        gc = (255,100,120,alpha) if self.kind=='life' else (80,180,255,alpha)
        pygame.draw.circle(glow, gc, (35,35), 30)
        surf.blit(glow, (cx-35, cy-35))
        ring_a = int(120+60*math.sin(self.frame*0.15))
        ring_s = pygame.Surface((60,60), pygame.SRCALPHA)
        rc = (255,180,190,ring_a) if self.kind=='life' else (120,200,255,ring_a)
        pygame.draw.circle(ring_s, rc, (30,30), 24, 3)
        surf.blit(ring_s, (cx-30, cy-30))
        if self.kind=='life':
            draw_heart(surf, cx, cy, 20, HEART_RED)
        else:
            draw_speed_icon(surf, cx, cy, 22)
    def get_rect(self):
        return pygame.Rect(self.x-20, self.y-20, 40, 40)


class Cockroach:
    """Cockroach now actively chases the rabbit, with intensity rising by level."""
    def __init__(self):
        self.x = random.choice([100, WIDTH-100])
        self.y = HEIGHT-130
        self.base_speed = 1.5
        self.size, self.frame = 35, 0
        self.facing = 1  # for animation, +1 right / -1 left

    def update(self, frame, sm, level, target_x, target_y):
        self.frame = frame
        # Speed scales with difficulty level (1..N)
        speed = (self.base_speed + (level - 1) * 0.45) * sm
        # Chasing factor: at level 1 mostly horizontal patrol, higher levels = stronger pursuit
        chase = min(1.0, 0.25 + (level - 1) * 0.18)

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy) or 1.0

        # Blend pure horizontal patrol with seek-toward-rabbit
        patrol_vx = (1 if self.x < WIDTH/2 else -1) * 0.4
        seek_vx = (dx / dist)
        seek_vy = (dy / dist)

        vx = patrol_vx * (1 - chase) + seek_vx * chase
        vy = seek_vy * chase * 0.85  # vertical pursuit a bit weaker so it isn't unfair

        self.x += vx * speed
        self.y += vy * speed

        # Clamp inside playfield
        self.x = max(40, min(WIDTH - 40, self.x))
        self.y = max(HEIGHT - 280, min(HEIGHT - 110, self.y))

        if vx > 0.05: self.facing = 1
        elif vx < -0.05: self.facing = -1

    def draw(self, surf):
        draw_cockroach(surf, self.x, self.y, self.size, self.frame)
        aura = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        a = int(40+20*math.sin(self.frame*0.1))
        pygame.draw.circle(aura, (200,0,0,a), (self.size*3//2, self.size*3//2), self.size)
        surf.blit(aura, (int(self.x)-self.size*3//2, int(self.y)-self.size*3//2))
    def get_rect(self):
        return pygame.Rect(self.x-self.size//2, self.y-self.size//3, self.size, self.size*2//3)


# ─────────────────────────────────────────────
# DIFFICULTY
# ─────────────────────────────────────────────
def level_for_score(score):
    """Score thresholds for difficulty levels.
    LV1: 0-9, LV2: 10-19, LV3: 20-34, LV4: 35-54, LV5+: 55+
    """
    if score < 10:  return 1
    if score < 20:  return 2
    if score < 35:  return 3
    if score < 55:  return 4
    return 5 + (score - 55) // 25  # endless ramp


def fruit_spawn_interval(level):
    """Frames between fruit spawns. Lower at higher levels = more fruit."""
    base_min, base_max = 25, 55
    factor = max(0.45, 1.0 - (level - 1) * 0.12)
    return max(12, int(random.randint(base_min, base_max) * factor))


# ─────────────────────────────────────────────
# GAME
# ─────────────────────────────────────────────
STATE_TITLE, STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER = 0, 1, 2, 3


def run_game():
    state = STATE_TITLE
    rabbit = Rabbit()
    cockroach = Cockroach()
    fruits, particles, popups, powerups = [], [], [], []
    banners = []
    score, lives = 0, 3
    game_time = 60.0
    frame = 0
    fruit_timer = 0
    pu_timer = random.randint(350,550)
    best_score = load_highscore()
    speed_timer = 0.0
    gameover_reason = ''
    level = 1

    play_bgm(bgm_normal)

    running = True
    while running:
        dt = clock.tick(FPS)/1000.0
        frame += 1
        sm = 2.0 if speed_timer>0 else 1.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN:
                if state==STATE_TITLE and ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                    state = STATE_PLAYING
                    rabbit = Rabbit(); cockroach = Cockroach()
                    fruits, particles, popups, powerups, banners = [], [], [], [], []
                    score, lives = 0, 3
                    game_time = 60.0; fruit_timer = 0
                    pu_timer = random.randint(350,550)
                    speed_timer = 0.0; gameover_reason = ''
                    level = 1
                    play_bgm(bgm_normal)
                    play_sfx(start_sound)
                elif state==STATE_GAMEOVER and ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                    state = STATE_TITLE
                    play_bgm(bgm_normal)
                elif state==STATE_PLAYING and ev.key in (pygame.K_p, pygame.K_ESCAPE):
                    state = STATE_PAUSED
                    BGM_CHANNEL.pause()
                elif state==STATE_PAUSED and ev.key in (pygame.K_p, pygame.K_ESCAPE,
                                                         pygame.K_SPACE, pygame.K_RETURN):
                    state = STATE_PLAYING
                    BGM_CHANNEL.unpause()
                elif state==STATE_TITLE and ev.key == pygame.K_ESCAPE:
                    running = False
                elif state==STATE_PAUSED and ev.key == pygame.K_q:
                    running = False

        keys = pygame.key.get_pressed()

        # ── TITLE ──
        if state == STATE_TITLE:
            draw_background(screen, frame)

            ty = HEIGHT//2-120+int(math.sin(frame*0.03)*8)
            tt = font_title.render("Bunny Fruit Frenzy", True, PINK_DARK)
            ts = font_title.render("Bunny Fruit Frenzy", True, (120,60,60))
            tx = WIDTH//2-tt.get_width()//2
            screen.blit(ts, (tx+3, ty+3))
            screen.blit(tt, (tx, ty))

            draw_small_grape_icon(screen, tx-38, ty+22, 28)
            draw_small_apple_icon(screen, tx+tt.get_width()+32, ty+20, 28)

            draw_rabbit(screen, WIDTH//2, HEIGHT//2+30, 55, False, frame)

            iy = HEIGHT//2+105
            for i, (txt, c) in enumerate([
                ("방향키로 토끼를 움직여요!", WHITE),
                ("과일을 먹고 바퀴벌레를 피하세요! 목숨 3개!", WHITE),
                ("점수가 오르면 난이도가 올라가요!", (255, 200, 100)),
                ("SPACE 또는 ENTER를 눌러 시작!  (P/ESC 일시정지)", GOLD),
            ]):
                if txt:
                    r = font_small.render(txt, True, c)
                    screen.blit(r, (WIDTH//2-r.get_width()//2, iy+i*30))

            if best_score > 0:
                bs = font_medium.render(f"최고 기록: {best_score}", True, GOLD)
                bx = WIDTH//2-bs.get_width()//2
                draw_trophy_icon(screen, bx-22, iy+162, 12)
                screen.blit(bs, (bx, iy+154))

        # ── PLAYING ──
        elif state == STATE_PLAYING:
            game_time -= dt

            # Difficulty level (changes with score)
            new_level = level_for_score(score)
            if new_level > level:
                level = new_level
                banners.append(CenterBanner(f"LEVEL {level}!", GOLD, 1.3))
                play_sfx(levelup_sfx)

            # Speed boost
            if speed_timer > 0:
                speed_timer -= dt
                if speed_timer <= 0:
                    speed_timer = 0.0
                    play_bgm(bgm_normal)

            if 0<game_time<=10 and int(game_time)!=int(game_time+dt):
                play_sfx(countdown_sound)

            # Time up
            if game_time <= 0:
                game_time = 0
                gameover_reason = 'time'
                state = STATE_GAMEOVER
                if score > best_score:
                    best_score = score
                    save_highscore(best_score)
                play_sfx(gameover_sound)
                BGM_CHANNEL.stop()

            rabbit.update(keys, sm)

            # Spawn fruits (level-aware)
            fruit_timer -= 1
            if fruit_timer <= 0:
                fruits.append(Fruit())
                fruit_timer = max(8, int(fruit_spawn_interval(level) / sm))

            # Spawn powerups
            pu_timer -= 1
            if pu_timer <= 0:
                powerups.append(PowerUp(random.choice(['life','speed'])))
                pu_timer = random.randint(400,700)

            for f in fruits: f.update(sm)
            fruits = [f for f in fruits if f.alive]
            for p in powerups: p.update(sm)
            powerups = [p for p in powerups if p.alive]
            cockroach.update(frame, sm, level, rabbit.x, rabbit.y)

            rr = rabbit.get_rect()

            # Fruit collection
            fc = {'apple':APPLE_RED,'banana':BANANA_YELLOW,'grape':GRAPE_PURPLE,
                  'orange':ORANGE_COLOR,'strawberry':STRAWBERRY_RED,
                  'cherry':CHERRY_RED,'watermelon':WATERMELON_RED}
            for f in fruits[:]:
                if f.alive and rr.colliderect(f.get_rect()):
                    f.alive = False; score += 1
                    play_sfx(eat_sound)
                    for _ in range(8):
                        particles.append(Particle(f.x, f.y, fc.get(f.type, STAR_YELLOW)))
                    popups.append(ScorePopup(f.x, f.y-20, "+1"))

            # Powerup collection
            for p in powerups[:]:
                if p.alive and rr.colliderect(p.get_rect()):
                    if p.kind == 'life':
                        if lives < 3:
                            p.alive = False; lives += 1
                            play_sfx(life_sfx)
                            for _ in range(12):
                                particles.append(Particle(p.x, p.y, HEART_RED))
                            popups.append(ScorePopup(p.x, p.y-20, "+1 UP", HEART_RED))
                    elif p.kind == 'speed':
                        p.alive = False
                        speed_timer = 10.0
                        play_sfx(speed_sfx)
                        play_bgm(bgm_fast)
                        for _ in range(12):
                            particles.append(Particle(p.x, p.y, SPEED_BLUE))
                        popups.append(ScorePopup(p.x, p.y-20, "SPEED x2!", SPEED_BLUE))

            # Cockroach hit -> lose life
            if rabbit.hit_timer == 0 and rr.colliderect(cockroach.get_rect()):
                rabbit.hit_timer = 90
                lives -= 1
                play_sfx(hit_sound)
                for _ in range(12):
                    particles.append(Particle(rabbit.x, rabbit.y, RED))
                popups.append(ScorePopup(rabbit.x, rabbit.y-30, "-1 Life", RED))
                if lives <= 0:
                    gameover_reason = 'dead'
                    state = STATE_GAMEOVER
                    if score > best_score:
                        best_score = score
                        save_highscore(best_score)
                    play_sfx(gameover_sound)
                    play_bgm(bgm_gameover)

            for p in particles: p.update()
            particles = [p for p in particles if p.life>0]
            for p in popups: p.update()
            popups = [p for p in popups if p.life>0]
            for b in banners: b.update()
            banners = [b for b in banners if b.life>0]

            # ── DRAW ──
            draw_background(screen, frame)

            if speed_timer > 0:
                tint = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
                pulse = int(12+8*math.sin(frame*0.15))
                tint.fill((80,180,255,pulse))
                screen.blit(tint, (0,0))

            for f in fruits: f.draw(screen)
            for p in powerups: p.draw(screen)
            for p in particles: p.draw(screen, frame)
            cockroach.draw(screen)
            rabbit.draw(screen)
            for p in popups: p.draw(screen)
            draw_ui(screen, score, game_time, lives, frame, speed_timer, level)
            for b in banners: b.draw(screen, frame)

        # ── PAUSED ──
        elif state == STATE_PAUSED:
            # draw last playing frame, then overlay
            draw_background(screen, frame)
            for f in fruits: f.draw(screen)
            for p in powerups: p.draw(screen)
            cockroach.draw(screen)
            rabbit.draw(screen)
            draw_ui(screen, score, game_time, lives, frame, speed_timer, level)

            ov = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,150))
            screen.blit(ov, (0,0))
            pt = font_large.render("일시정지", True, GOLD)
            screen.blit(pt, (WIDTH//2-pt.get_width()//2, HEIGHT//2-60))
            ht = font_small.render("P / ESC / SPACE: 계속하기   |   Q: 종료", True, WHITE)
            screen.blit(ht, (WIDTH//2-ht.get_width()//2, HEIGHT//2+10))

        # ── GAME OVER ──
        elif state == STATE_GAMEOVER:
            draw_background(screen, frame)

            ov = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,130))
            screen.blit(ov, (0,0))

            bw, bh = 460, 360
            bx, by = WIDTH//2-bw//2, HEIGHT//2-bh//2
            pygame.draw.rect(screen, (50,35,18), (bx,by,bw,bh), border_radius=16)
            pygame.draw.rect(screen, GOLD, (bx,by,bw,bh), 3, border_radius=16)

            if gameover_reason == 'dead':
                gt = font_large.render("Game Over!", True, RED)
                reason = font_small.render("바퀴벌레에게 모든 목숨을 잃었어요!", True, (200,180,140))
            else:
                gt = font_large.render("시간 종료!", True, GOLD)
                reason = None

            screen.blit(gt, (WIDTH//2-gt.get_width()//2, by+22))
            ry = by + 68
            if reason:
                screen.blit(reason, (WIDTH//2-reason.get_width()//2, ry))
                ry += 30

            sd = font_large.render(f" {score}개 수집!", True, WHITE)
            tw2 = 30+sd.get_width()
            sx = WIDTH//2-tw2//2
            draw_small_apple_icon(screen, sx+14, ry+24, 15)
            screen.blit(sd, (sx+30, ry+8))

            lvl_text = font_small.render(f"도달 레벨 LV {level}", True, (255, 200, 100))
            screen.blit(lvl_text, (WIDTH//2-lvl_text.get_width()//2, ry+58))

            if score>=40:   rat, rc = "* 과일 마스터! *", GOLD
            elif score>=25: rat, rc = "훌륭해요!", (100,255,100)
            elif score>=15: rat, rc = "잘했어요!", (100,200,255)
            else:           rat, rc = "다시 도전해봐요!", (255,180,100)
            rt = font_medium.render(rat, True, rc)
            screen.blit(rt, (WIDTH//2-rt.get_width()//2, ry+88))

            if score>=best_score and score>0:
                nt = font_medium.render("새로운 최고 기록!", True, GOLD)
                nx = WIDTH//2-nt.get_width()//2
                draw_trophy_icon(screen, nx-22, ry+138, 12)
                screen.blit(nt, (nx, ry+130))
            else:
                bst = font_small.render(f"최고 기록: {best_score}", True, (200,180,140))
                screen.blit(bst, (WIDTH//2-bst.get_width()//2, ry+135))

            rest = font_small.render("SPACE로 다시 시작", True, (180,160,120))
            screen.blit(rest, (WIDTH//2-rest.get_width()//2, by+bh-45))

            draw_rabbit(screen, WIDTH//2-110, by-25, 32, False, frame)
            draw_rabbit(screen, WIDTH//2+110, by-25, 32, True, frame)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()
