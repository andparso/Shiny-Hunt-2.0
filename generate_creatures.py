#!/usr/bin/env python3
"""
Utility script to procedurally generate pixel art creature sprites for the shiny hunting game.

This script uses the Pillow library to programmatically draw simple dinosaur‑like
creatures with a variety of features such as horns, spines, fins, collars and
spots. Each creature is represented by a dictionary of attributes that
determine its body colour, any decorative elements and special features. The
generated sprites are saved as PNG files into the ``assets/creatures``
directories:

``assets/creatures/base``     – base form for each creature (standard and radiant variants share this art)
``assets/creatures/unique``   – unique form for each creature (used for the unique variant)

Radiant variants are produced at runtime by applying a simple hue shift in
JavaScript, so only the base and unique images need to be pre‑generated here.

Running this script will overwrite any existing images in those folders.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFilter

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "creatures")
BASE_OUTPUT = os.path.join(ASSETS_DIR, "base")
UNIQUE_OUTPUT = os.path.join(ASSETS_DIR, "unique")
os.makedirs(BASE_OUTPUT, exist_ok=True)
os.makedirs(UNIQUE_OUTPUT, exist_ok=True)


def draw_creature(params, unique=False):
    """Draw a single creature sprite based on parameter dictionary.

    When ``unique`` is True the creature is drawn with modified features and
    colours to serve as the "unique" variant. Otherwise the base variant is
    rendered.
    """
    # Base image size
    size = 100
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Extract parameters
    colour = params.get('color', (120, 200, 120))
    tail_shape = params.get('tail', 'normal')
    horns = params.get('horns', False)
    horns_colour = params.get('horns_color', None)
    spines = params.get('spines', 0)
    crest = params.get('crest', False)
    spots = params.get('spots', False)
    fins = params.get('fins', False)

    # For unique variants, adjust features to make them feel special
    if unique:
        # swap horns/spines/crest flags and adjust colours
        colour = tuple(min(255, int(c * 0.7 + 80)) for c in colour)  # shift hue slightly
        horns = not horns
        spines = (spines + 2) % 5
        crest = not crest if params.get('allow_crest_unique', True) else crest
        spots = not spots
        fins = not fins

    # Body coordinates
    body_rect = (20, 40, 80, 90)
    # Draw body
    draw.ellipse(body_rect, fill=colour)

    # Head
    head_rect = (40, 20, 80, 60)
    draw.ellipse(head_rect, fill=colour)

    # Legs
    draw.rectangle((30, 80, 40, 95), fill=colour)
    draw.rectangle((55, 80, 65, 95), fill=colour)

    # Tail
    if tail_shape == 'leaf':
        leaf_points = [(20, 70), (10, 50), (20, 55), (15, 65)]
        draw.polygon(leaf_points, fill=colour)
        # central vein on leaf
        draw.line([(15, 55), (15, 65)], fill=(0, 100, 0), width=1)
    elif tail_shape == 'long':
        tail_points = [(20, 75), (5, 65), (20, 55)]
        draw.polygon(tail_points, fill=colour)
    elif tail_shape == 'fin':
        tail_points = [(20, 70), (5, 60), (20, 50)]
        draw.polygon(tail_points, fill=colour)
        draw.line([(12, 58), (12, 65)], fill=(0, 150, 200), width=1)
    else:  # normal
        tail_points = [(20, 70), (10, 65), (20, 60)]
        draw.polygon(tail_points, fill=colour)

    # Horns
    if horns:
        hc = horns_colour or tuple(min(255, c + 40) for c in colour)
        draw.polygon([(50, 12), (54, 25), (46, 25)], fill=hc)
        draw.polygon([(60, 12), (64, 25), (56, 25)], fill=hc)

    # Spines along back
    for i in range(spines):
        x = 30 + i * 10
        draw.polygon([(x, 38 - i * 2), (x + 5, 28 - i * 2), (x + 10, 38 - i * 2)],
                     fill=tuple(max(0, c - 30) for c in colour))

    # Collar/crest of petals around neck
    if crest:
        for i in range(6):
            angle = math.radians(i * 60)
            cx, cy = 60, 40
            dx = int(12 * math.cos(angle))
            dy = int(12 * math.sin(angle))
            petal_col = (255, 200, 0) if not unique else (255, 0, 200)
            draw.ellipse((cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4), fill=petal_col)

    # Spots
    if spots:
        import random
        for _ in range(6):
            sx = random.randint(30, 70)
            sy = random.randint(50, 85)
            spot_col = tuple(max(0, c - 40) for c in colour)
            draw.ellipse((sx - 2, sy - 2, sx + 2, sy + 2), fill=spot_col)

    # Fins along back (used for aquatic creatures)
    if fins:
        # draw three fins along spine
        fin_col = tuple(min(255, c + 60) for c in colour)
        for i in range(3):
            fx = 35 + i * 15
            draw.polygon([(fx, 35 - i * 3), (fx + 7, 25 - i * 3), (fx + 14, 35 - i * 3)], fill=fin_col)

    # Eyes
    eye_x, eye_y = 63, 33
    # left eye
    draw.ellipse((eye_x - 10, eye_y - 5, eye_x - 4, eye_y + 1), fill=(255, 255, 255))
    draw.ellipse((eye_x - 8, eye_y - 3, eye_x - 6, eye_y - 1), fill=(0, 0, 0))
    # right eye (smaller/side)
    draw.ellipse((eye_x - 24, eye_y - 5, eye_x - 18, eye_y + 1), fill=(255, 255, 255))
    draw.ellipse((eye_x - 22, eye_y - 3, eye_x - 20, eye_y - 1), fill=(0, 0, 0))

    return img


# Define creature attributes per biome and time of day. Each entry defines the name
# and drawing parameters for the base creature. Unique variants will be
# automatically derived by the script.
CREATURES = [
    # Verdant Glade – Day
    ('verdant_leaflon',    {'color': (76, 174, 79), 'tail': 'leaf', 'horns': False, 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
    ('verdant_barkhorn',   {'color': (143, 92, 49), 'tail': 'normal', 'horns': True, 'horns_color': (189, 135, 70), 'spines': 0, 'crest': False, 'spots': False, 'fins': False}),
    ('verdant_dewhopper', {'color': (119, 178, 187), 'tail': 'long', 'horns': False, 'spines': 0, 'crest': False, 'spots': True, 'fins': True}),
    ('verdant_suncollar', {'color': (208, 131, 45), 'tail': 'normal', 'horns': False, 'spines': 0, 'crest': True, 'spots': False, 'fins': False, 'allow_crest_unique': False}),
    ('verdant_sproutling',{'color': (102, 185, 90), 'tail': 'leaf', 'horns': False, 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    # Verdant Glade – Night
    ('verdant_gloomdrake',{'color': (91, 64, 115), 'tail': 'long', 'horns': True, 'horns_color': (111, 84, 135), 'spines': 3, 'crest': False, 'spots': False, 'fins': False}),
    ('verdant_shadowpouncer',{'color': (60, 60, 70), 'tail': 'long', 'horns': False, 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('verdant_moonfen',   {'color': (75, 123, 199), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': True, 'fins': True}),
    ('verdant_shadehopper',{'color': (63, 97, 56), 'tail': 'long', 'horns': False, 'spines': 0, 'crest': False, 'spots': True, 'fins': False}),
    ('verdant_starbit',   {'color': (223, 210, 60), 'tail': 'fin', 'horns': False, 'spines': 1, 'crest': False, 'spots': False, 'fins': True}),
    # Scorching Dunes – Day
    ('desert_sunscale',   {'color': (230, 170, 69), 'tail': 'normal', 'horns': True, 'horns_color': (255, 213, 96), 'spines': 3, 'crest': False, 'spots': False, 'fins': False}),
    ('desert_sandrunner', {'color': (199, 148, 80), 'tail': 'long', 'horns': False, 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
    ('desert_cactusaur',  {'color': (187, 167, 57), 'tail': 'leaf', 'horns': True, 'horns_color': (204, 190, 92), 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('desert_mirageback',{'color': (207, 152, 97), 'tail': 'long', 'horns': False, 'spines': 0, 'crest': True, 'spots': False, 'fins': False}),
    ('desert_dustwing',  {'color': (215, 180, 100), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': False, 'fins': True}),
    # Scorching Dunes – Night
    ('desert_dunehowl',  {'color': (120, 85, 60), 'tail': 'long', 'horns': True, 'horns_color': (145, 105, 75), 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
    ('desert_nightcrawler',{'color': (85, 74, 65), 'tail': 'long', 'horns': False, 'spines': 3, 'crest': False, 'spots': False, 'fins': False}),
    ('desert_mirageglider',{'color': (139, 116, 102), 'tail': 'fin', 'horns': True, 'horns_color': (169, 146, 132), 'spines': 0, 'crest': False, 'spots': False, 'fins': True}),
    ('desert_sandshiver',{'color': (155, 121, 93), 'tail': 'long', 'horns': False, 'spines': 4, 'crest': False, 'spots': False, 'fins': False}),
    ('desert_aridclaw', {'color': (133, 109, 90), 'tail': 'normal', 'horns': True, 'horns_color': (163, 139, 120), 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
    # Tidal Reef – Day
    ('ocean_seapup',     {'color': (79, 169, 222), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': False, 'fins': True}),
    ('ocean_coralhorn', {'color': (85, 131, 191), 'tail': 'normal', 'horns': True, 'horns_color': (170, 198, 240), 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('ocean_tideback',  {'color': (92, 183, 201), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': False, 'fins': True}),
    ('ocean_splashfin', {'color': (104, 167, 216), 'tail': 'fin', 'horns': False, 'spines': 1, 'crest': False, 'spots': False, 'fins': True}),
    ('ocean_wavefoot',  {'color': (66, 138, 190), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': True, 'fins': True}),
    # Tidal Reef – Night
    ('ocean_deepglow',  {'color': (40, 85, 138), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': True, 'fins': True}),
    ('ocean_moonray',   {'color': (58, 104, 161), 'tail': 'fin', 'horns': False, 'spines': 1, 'crest': False, 'spots': True, 'fins': True}),
    ('ocean_abyssclaw', {'color': (50, 84, 123), 'tail': 'normal', 'horns': True, 'horns_color': (80, 114, 153), 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('ocean_mistwing',  {'color': (76, 121, 182), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': False, 'fins': True}),
    ('ocean_whirlpooler',{'color': (60, 94, 140), 'tail': 'fin', 'horns': False, 'spines': 3, 'crest': False, 'spots': False, 'fins': True}),
    # Frost Peaks – Day
    ('mountain_iceback',{'color': (146, 202, 221), 'tail': 'normal', 'horns': True, 'horns_color': (176, 232, 251), 'spines': 3, 'crest': False, 'spots': False, 'fins': False}),
    ('mountain_snowtail',{'color': (192, 223, 233), 'tail': 'long', 'horns': False, 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
    ('mountain_frosthorn',{'color': (163, 198, 222), 'tail': 'normal', 'horns': True, 'horns_color': (213, 243, 255), 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
    ('mountain_glacierpaw',{'color': (179, 210, 220), 'tail': 'normal', 'horns': False, 'spines': 0, 'crest': True, 'spots': False, 'fins': False}),
    ('mountain_chilldrake',{'color': (134, 187, 210), 'tail': 'long', 'horns': True, 'horns_color': (164, 217, 240), 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    # Frost Peaks – Night
    ('mountain_iciclex',{'color': (103, 143, 170), 'tail': 'long', 'horns': False, 'spines': 3, 'crest': False, 'spots': False, 'fins': False}),
    ('mountain_nightfrost',{'color': (90, 122, 149), 'tail': 'long', 'horns': True, 'horns_color': (120, 152, 179), 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('mountain_winterstalk',{'color': (113, 153, 180), 'tail': 'normal', 'horns': False, 'spines': 4, 'crest': False, 'spots': False, 'fins': False}),
    ('mountain_snowmantle',{'color': (167, 214, 236), 'tail': 'normal', 'horns': False, 'spines': 1, 'crest': True, 'spots': False, 'fins': False}),
    ('mountain_iceblink',{'color': (120, 164, 198), 'tail': 'fin', 'horns': True, 'horns_color': (150, 194, 228), 'spines': 2, 'crest': False, 'spots': False, 'fins': True}),
    # Murk Swamp – Day
    ('swamp_mudfin',    {'color': (102, 125, 77), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': True, 'fins': True}),
    ('swamp_bogmaw',    {'color': (89, 113, 65), 'tail': 'long', 'horns': True, 'horns_color': (119, 143, 95), 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('swamp_marshclaw',{'color': (79, 103, 61), 'tail': 'long', 'horns': False, 'spines': 3, 'crest': False, 'spots': False, 'fins': False}),
    ('swamp_fenrunner',{'color': (96, 129, 82), 'tail': 'long', 'horns': False, 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
    ('swamp_vinecrest',{'color': (83, 116, 70), 'tail': 'leaf', 'horns': False, 'spines': 0, 'crest': True, 'spots': False, 'fins': False}),
    # Murk Swamp – Night
    ('swamp_mireglow', {'color': (70, 96, 58), 'tail': 'fin', 'horns': False, 'spines': 0, 'crest': False, 'spots': True, 'fins': True}),
    ('swamp_sludgeback',{'color': (60, 80, 50), 'tail': 'long', 'horns': True, 'horns_color': (90, 110, 70), 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('swamp_fogwhisp',  {'color': (72, 98, 64), 'tail': 'fin', 'horns': False, 'spines': 1, 'crest': False, 'spots': True, 'fins': True}),
    ('swamp_croakshade',{'color': (68, 92, 58), 'tail': 'long', 'horns': False, 'spines': 2, 'crest': False, 'spots': False, 'fins': False}),
    ('swamp_nightvine',{'color': (65, 90, 55), 'tail': 'leaf', 'horns': True, 'horns_color': (95, 120, 85), 'spines': 1, 'crest': False, 'spots': False, 'fins': False}),
]


def generate_all():
    """Generate base and unique sprites for all defined creatures."""
    for name, params in CREATURES:
        base_img = draw_creature(params, unique=False)
        unique_img = draw_creature(params, unique=True)
        base_path = os.path.join(BASE_OUTPUT, f"{name}_base.png")
        unique_path = os.path.join(UNIQUE_OUTPUT, f"{name}_unique.png")
        base_img.save(base_path)
        unique_img.save(unique_path)
        print(f"Generated {base_path} and unique variant")


if __name__ == '__main__':
    generate_all()