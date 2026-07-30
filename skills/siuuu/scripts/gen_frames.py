#!/usr/bin/env python3
"""Rasterize the Claude Code SVG logo into shaded half-block terminal frames for siuuu.sh.

Dev-time tool only — its output is pasted into siuuu.sh as static bash arrays, so end
users never need Python. SVG viewBox 0 0 24 24, pixel unit = 0.75 SVG units -> logo is
32x20 px. Frames live in a fixed 36x24 px box (36 terminal cols x 12 char rows),
bottom-aligned. Each char row = 2 px rows. Pixel values: 0 empty, 1 solid (█),
2 dark shade (▓), 3 medium shade (▒), 4 light shade (░). Shade rects are kept aligned
to even-y char cells where it matters.
"""

BOX_W, BOX_H = 36, 24

EMPTY, SOLID, DARK, MED, LIGHT = 0, 1, 2, 3, 4
CHAR = {EMPTY: ' ', SOLID: '█', DARK: '▓', MED: '▒', LIGHT: '░'}

# Standing logo in box coords (logo 32x20 centered: x offset 2, bottom-aligned: y offset 4)
BODY = (6, 4, 30, 20)
RIM = (6, 18, 30, 20)          # bottom rim of body -> ▓ (ambient occlusion)
ARM_L = (2, 12, 6, 16)
ARM_R = (30, 12, 34, 16)
EYE_L = (10, 8, 12, 12)
EYE_R = (24, 8, 26, 12)
LEGS = [(8, 20, 10, 24), (12, 20, 14, 24), (22, 20, 24, 24), (26, 20, 28, 24)]

# Mouths (box coords, below the eyes at y 8..12, above the rim at y 18)
MOUTH_SMALL = [(16, 14, 20, 16, EMPTY)]   # contented little smile-slit
MOUTH_O = [(16, 14, 20, 18, EMPTY)]       # small "o" of effort


# ---- grid helpers -------------------------------------------------------------------

def blank():
  return [[EMPTY] * BOX_W for _ in range(BOX_H)]


def rects(g, items, dx=0, dy=0):
  for (x0, y0, x1, y1, v) in items:
    for y in range(y0 + dy, y1 + dy):
      for x in range(x0 + dx, x1 + dx):
        if 0 <= y < BOX_H and 0 <= x < BOX_W:
          g[y][x] = v


def leg_items(legs, shade=True):
  out = []
  for (x0, y0, x1, y1) in legs:
    out.append((x0, y0, x1, y1, SOLID))
    if shade:
      out.append((x0 - 1, y0, x0, y1, MED))   # ▒ column on the left edge of each leg
  return out


def squash(g, keep_every):
  """Horizontal squash for the vertical-axis spin: keep every Nth column, re-centered."""
  out = blank()
  kept = [x for x in range(BOX_W) if x % keep_every == 0]
  off = (BOX_W - len(kept)) // 2
  for y in range(BOX_H):
    for i, x in enumerate(kept):
      out[y][off + i] = g[y][x]
  return out


def shadow(width):
  """Ground-shadow string (BOX_W cols), narrower the higher the jump."""
  pad = (BOX_W - width) // 2
  return ' ' * pad + '░' * width + ' ' * (BOX_W - width - pad)


# ---- pose builders ------------------------------------------------------------------

def standing(dy=0, legs=None, eyes=True, rim=True, leg_shade=True, mouth=None):
  g = blank()
  items = [BODY + (SOLID,), ARM_L + (SOLID,), ARM_R + (SOLID,)]
  if rim:
    items.append(RIM + (DARK,))
  if eyes:
    items += [EYE_L + (EMPTY,), EYE_R + (EMPTY,)]
  if mouth:
    items += mouth
  items += leg_items(legs if legs is not None else LEGS, shade=leg_shade)
  rects(g, items, dy=dy)
  return g


def crouch_grid(mouth):
  """Anticipation before takeoff / landing impact: squashed body, squinted eyes."""
  g = blank()
  rects(g, [
    (6, 10, 30, 22, SOLID),                    # body squashed to 12px
    (6, 20, 30, 22, DARK),                     # rim
    (2, 16, 6, 20, SOLID), (30, 16, 34, 20, SOLID),   # arms a bit lower
    (10, 14, 12, 16, EMPTY), (24, 14, 26, 16, EMPTY), # squinted eyes
  ] + mouth)
  rects(g, leg_items([(7, 22, 9, 24), (12, 22, 14, 24),
                      (22, 22, 24, 24), (27, 22, 29, 24)]))
  return g


def stretch_grid():
  """Takeoff: body elongated, arms thrown up, eyes wide open."""
  g = blank()
  rects(g, [
    (6, 2, 30, 20, SOLID),                       # body stretched to 18px
    (6, 18, 30, 20, DARK),                       # rim
    (2, 0, 6, 6, SOLID), (30, 0, 34, 6, SOLID),  # arms thrown up past the shoulders
    (10, 6, 12, 12, EMPTY), (24, 6, 26, 12, EMPTY),   # wide eyes
  ] + MOUTH_O)
  rects(g, leg_items(LEGS))
  return g


def pose_grid(eyes, mouth):
  """Landing pose: arms swept down-out, wide stance, shouting face."""
  g = blank()
  rects(g, [
    BODY + (SOLID,), RIM + (DARK,),
    (2, 16, 6, 20, SOLID), (2, 20, 4, 22, SOLID),      # left arm angled down + hand
    (30, 16, 34, 20, SOLID), (32, 20, 34, 22, SOLID),  # right arm angled down + hand
  ] + eyes + mouth)
  rects(g, leg_items([(6, 20, 8, 24), (11, 20, 13, 24),
                      (23, 20, 25, 24), (28, 20, 30, 24)]))
  return g


# ---- half-block rendering -----------------------------------------------------------

def cell(t, b):
  if t == b:
    return CHAR[t]
  if {t, b} == {SOLID, EMPTY}:
    return '▀' if t == SOLID else '▄'
  if SOLID in (t, b):
    return '▓'          # solid + shade mix
  if EMPTY in (t, b):
    return '▒' if max(t, b) <= MED else '░'   # shade + empty mix
  return '▓'


def render(g):
  return [''.join(cell(g[r][x], g[r + 1][x]) for x in range(BOX_W))
          for r in range(0, BOX_H, 2)]


# ---- frames -------------------------------------------------------------------------

frames = {}

# run cycle: legs alternate + 1px bob, little smile
legs_b = [(x0 + 2, y0, x1 + 2, y1) for (x0, y0, x1, y1) in LEGS]
frames['RUN_A'] = standing(mouth=MOUTH_SMALL)
frames['RUN_B'] = standing(dy=-1, legs=legs_b, mouth=MOUTH_SMALL)

# crouch / impact / stretch
frames['CROUCH'] = crouch_grid([(15, 18, 21, 20, EMPTY)])         # gritted line
frames['IMPACT'] = crouch_grid([(15, 16, 21, 20, EMPTY)])         # mouth popping open
frames['STRETCH'] = stretch_grid()

# spin (vertical-axis 360°): legs tucked; back view has no eyes
tucked = [(8, 20, 10, 22), (12, 20, 14, 22), (22, 20, 24, 22), (26, 20, 28, 22)]
front_air = standing(legs=tucked, leg_shade=False, mouth=MOUTH_SMALL)
back_air = standing(legs=tucked, eyes=False, leg_shade=False)
frames['SPIN_HALF'] = squash(front_air, 2)
frames['SPIN_SLIT'] = squash(standing(legs=[], eyes=False), 4)
frames['SPIN_BACK'] = back_air
frames['SPIN_BACK_HALF'] = squash(back_air, 2)

# landing pose, two shout sizes (mouth chomps with the flashing banner)
eyes_intense = [(9, 8, 12, 12, EMPTY), (24, 8, 27, 12, EMPTY)]    # wider, intense
frames['POSE'] = pose_grid(
  eyes_intense,
  [(13, 14, 23, 18, EMPTY), (14, 16, 22, 18, MED)],   # open mouth + ▒ tongue
)
frames['POSE_SHOUT'] = pose_grid(
  eyes_intense,
  [(12, 12, 24, 18, EMPTY), (13, 16, 23, 18, MED)],   # jaw dropped: SIUUU!
)

# static logo (preview only — not emitted to bash, siuuu.sh doesn't use it)
frames['LOGO'] = standing()

shadows = {'SH0': shadow(32), 'SH1': shadow(24), 'SH2': shadow(16), 'SH3': shadow(8)}


# ---- output: previews, then the bash arrays to paste into siuuu.sh -------------------

for name, grid in frames.items():
  print(f'== {name} ==')
  for line in render(grid):
    print(f'|{line}|')
  print()

print('#---- bash ----')
for name, grid in frames.items():
  if name == 'LOGO':
    continue
  print(f'{name}=(')
  for line in render(grid):
    print(f"'{line}'")
  print(')')
for name, s in shadows.items():
  print(f"{name}='{s}'")
