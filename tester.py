import pygame
import webcolors
from matplotlib import colors
import json
colors_ = {}
for key in colors.XKCD_COLORS:
    old = key
    if ":" in key:
        key = key.split(":")[1]
    key = key.replace(" ", "_")
    colors_[key] = tuple(x * 255 for x in colors.to_rgb(colors.XKCD_COLORS[old]))


for key in pygame.colordict.THECOLORS:
    old = key
    if ":" in key:
        key = key.split(":")[1]
    key = key.replace(" ", "_")
    colors_[key] = tuple(pygame.colordict.THECOLORS[old][i] for i in range(3))



with open("colors.py", "w") as file:
    json.dump(colors_, file, indent=4)