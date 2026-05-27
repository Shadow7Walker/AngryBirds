import pygame
import os

# Image loading and caching system to optimize performance
_image_cache = {}
def load_cached_image(path, flip_h=False):
    key = (path, flip_h)
    if key not in _image_cache:
        img = pygame.image.load(path).convert_alpha()
        if flip_h:
            img = pygame.transform.flip(img, True, False)
        _image_cache[key] = img
    return _image_cache[key]

# Persistent High Score system
HIGHSCORE_FILE = ".highscore"

def load_high_score():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0
    return 0

def save_high_score(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception as e:
        print(f"Error saving high score: {e}")

# UI Helper function
def render_text_with_shadow(surface, text, font, color, shadow_color, pos, center=False, shadow_offset=(3, 3)):
    # Render shadow
    shadow_surf = font.render(text, True, shadow_color)
    # Render main text
    text_surf = font.render(text, True, color)
    
    if center:
        rect = text_surf.get_rect(center=pos)
        shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]))
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, rect)
    else:
        surface.blit(shadow_surf, (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]))
        surface.blit(text_surf, pos)
