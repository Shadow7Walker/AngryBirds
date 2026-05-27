import pygame
import sys
import time
import random
import const
import utils
import state
from entities import Ball, StaticObstacle

def draw_button(surface, rect, text, font, is_hovered, base_color=(240, 240, 240), hover_color=(200, 220, 255), border_color=(100, 100, 250), text_color=(0, 0, 0)):
    shadow_rect = rect.copy()
    shadow_rect.x += 4
    shadow_rect.y += 4
    pygame.draw.rect(surface, (40, 40, 40), shadow_rect, border_radius=12)
    
    color = hover_color if is_hovered else base_color
    pygame.draw.rect(surface, color, rect, border_radius=12)
    pygame.draw.rect(surface, border_color if is_hovered else (150, 150, 150), rect, width=3, border_radius=12)
    
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)


def step(gameState):
    print("step", state.stepCount)
    state.stepCount += 1
    state.windr = random.randrange(1, 5)
    if gameState != 3:
        r = random.randrange(0, 4)
        k = [const.red, const.chuck, const.bomb, const.blue]
        if state.stepCount > 1:
            gS = gameState
            if gS == 1:
                Ball((350, 570), all_sprites, collision_sprites, k[r], 1)
            if gS == 2:
                Ball((920, 570), all_sprites2, collision_sprites2, k[r], 2)


def spriteSetup(level):
    for i in level:
        StaticObstacle(i[0], i[1], [all_sprites, collision_sprites] if i[2] == 1 else [all_sprites2, collision_sprites2])
    
    Ball((350, 570), all_sprites, collision_sprites, state.bird1, 1)
    Ball((920, 570), all_sprites2, collision_sprites2, state.bird2, 2)


def windSetup():
    arrow_surface = pygame.transform.rotate(arrow, 0)
    if state.wind == 1:
        if state.windr == 1:
            arrow_surface = pygame.transform.rotate(arrow, 315)
        elif state.windr == 2:
            arrow_surface = pygame.transform.rotate(arrow, 225)
        elif state.windr == 3:
            arrow_surface = pygame.transform.rotate(arrow, 45)
        elif state.windr == 4:
            arrow_surface = pygame.transform.rotate(arrow, 135)
        screen.blit(arrow_surface, (640, 100))


def timeCounter():
    if state.tim == 0:
        state.stk1 = time.time()
        state.tim = 1
    state.stk2 = time.time()
    
    rem_time = max(0, round(300 - (state.stk2 - state.stk1)))
    utils.render_text_with_shadow(screen, str(rem_time), FONTS["sys_70"], (255, 255, 255), (0, 0, 0), (640, 50), center=True)
    
    if state.stk2 - state.stk1 > 300:
        if state.score1 > state.score2:
            state.winner = 1
        else:
            state.winner = 2
        state.gameState = 3


# general setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Angry Birds")
clock = pygame.time.Clock()  # Game timing clock

# Share screen and step callback to state
state.screen = screen
state.step_callback = step

# Pre-load and cache fonts to avoid TTF parsing overhead in the rendering loop
FONTS = {
    "comic_64": pygame.font.Font(const.font, 64),
    "comic_56": pygame.font.Font(const.font, 56),
    "comic_54": pygame.font.Font(const.font, 54),
    "comic_48": pygame.font.Font(const.font, 48),
    "comic_44": pygame.font.Font(const.font, 44),
    "comic_40": pygame.font.Font(const.font, 40),
    "comic_38": pygame.font.Font(const.font, 38),
    "comic_36": pygame.font.Font(const.font, 36),
    "comic_32": pygame.font.Font(const.font, 32),
    "comic_28": pygame.font.Font(const.font, 28),
    "sys_70": pygame.font.Font(None, 70),
    "sys_54": pygame.font.Font(None, 54),
    "sys_24": pygame.font.Font(None, 24)
}

# group setup
all_sprites = pygame.sprite.Group()
collision_sprites = pygame.sprite.Group()
all_sprites2 = pygame.sprite.Group()
collision_sprites2 = pygame.sprite.Group()

# load sounds
pygame.mixer.init()
play_sfx = pygame.mixer.Sound("./resources/sound/play.mp3")
play_sfx.set_volume(0.3)
victory_sfx = pygame.mixer.Sound("./resources/sound/victory.mp3")
victory_sfx.set_volume(0.3)
red_sfx = pygame.mixer.Sound("./resources/sound/red.mp3")
chuck_sfx = pygame.mixer.Sound("./resources/sound/chuck.mp3")
bomb_sfx = pygame.mixer.Sound("./resources/sound/bomb.mp3")
blues_sfx = pygame.mixer.Sound("./resources/sound/blues.mp3")

# Share sounds to state for use by entities
state.sounds = {
    const.red: red_sfx,
    const.chuck: chuck_sfx,
    const.bomb: bomb_sfx,
    const.blue: blues_sfx
}

# Load static images
background_surface = pygame.image.load("./resources/images/background2.jpg").convert()
background_surface2 = pygame.image.load("./resources/images/background1.jpg").convert()
sling_shot_surface = pygame.image.load("./resources/images/sling.png").convert_alpha()
stars_surface = pygame.image.load("./resources/images/stars.png").convert_alpha()
RED = pygame.image.load(const.red).convert_alpha()
CHUCK = pygame.image.load(const.chuck).convert_alpha()
BOMB = pygame.image.load(const.bomb).convert_alpha()
BLUE = pygame.image.load(const.blue).convert_alpha()
arrow = pygame.image.load("./resources/img/arrow.png").convert_alpha()

# Pre-render scaled states of the restart button to avoid runtime scaling overhead
restart_img_hovered = pygame.transform.scale(pygame.image.load("./resources/img/restart.png").convert_alpha(), (210, 210))
restart_img_normal = pygame.transform.scale(pygame.image.load("./resources/img/restart.png").convert_alpha(), (190, 190))

# Pre-define static bird selections to avoid allocating memory inside the rendering loop
BIRD_OPTIONS = [
    {"type": const.red, "img": RED, "name": "Red", "pos": (220, 200), "desc": "Standard Bird\nBalanced stats", "color": (255, 0, 0)},
    {"type": const.chuck, "img": CHUCK, "name": "Chuck", "pos": (460, 200), "desc": "Wood Piercer\nExtra pierce vs Wood", "color": (255, 255, 0)},
    {"type": const.bomb, "img": BOMB, "name": "Bomb", "pos": (700, 200), "desc": "Stone Piercer\nExtra pierce vs Stone", "color": (50, 50, 50)},
    {"type": const.blue, "img": BLUE, "name": "Blue", "pos": (940, 200), "desc": "Ice Piercer\nExtra pierce vs Ice", "color": (0, 191, 255)},
]

state.highScore = utils.load_high_score()

# main game loop
while True:
    # Frame rate cap using clock.tick, but fixed dt for physics
    clock.tick(60)
    dt = 1 / 60.0
    
    # Consolidated event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if state.gameState == 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    state.input = state.input[:-1]
                elif state.p == 0 and event.key == pygame.K_RETURN:
                    state.player1 = state.input.strip() if state.input.strip() else "Player 1"
                    state.input = ""
                    state.text = "Enter Player_2 Name "
                    state.p = 1
                elif state.p == 1 and event.key == pygame.K_RETURN:
                    state.player2 = state.input.strip() if state.input.strip() else "Player 2"
                    state.input = ""
                    state.gameState = -1
                else:
                    if event.unicode.isprintable() and len(state.input) < 15:
                        state.input += event.unicode
                        
        elif state.gameState == -1 or state.gameState == -2:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if pygame.Rect(220, 200, 200, 350).collidepoint(pos):
                    if state.gameState == -1:
                        state.bird1 = const.red
                        state.gameState = -2
                    else:
                        state.bird2 = const.red
                        state.gameState = -3
                elif pygame.Rect(460, 200, 200, 350).collidepoint(pos):
                    if state.gameState == -1:
                        state.bird1 = const.chuck
                        state.gameState = -2
                    else:
                        state.bird2 = const.chuck
                        state.gameState = -3
                elif pygame.Rect(700, 200, 200, 350).collidepoint(pos):
                    if state.gameState == -1:
                        state.bird1 = const.bomb
                        state.gameState = -2
                    else:
                        state.bird2 = const.bomb
                        state.gameState = -3
                elif pygame.Rect(940, 200, 200, 350).collidepoint(pos):
                    if state.gameState == -1:
                        state.bird1 = const.blue
                        state.gameState = -2
                    else:
                        state.bird2 = const.blue
                        state.gameState = -3
                        
        elif state.gameState == -3:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if pygame.Rect(490, 240, 300, 80).collidepoint(pos):
                    lev = const.level1
                    state.gameState = -4
                elif pygame.Rect(490, 350, 300, 80).collidepoint(pos):
                    lev = const.level2
                    state.gameState = -4
                elif pygame.Rect(490, 460, 300, 80).collidepoint(pos):
                    lev = const.level3
                    state.gameState = -4
                    
        elif state.gameState == -4:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if pygame.Rect(490, 260, 300, 80).collidepoint(pos):
                    state.wind = 1
                    state.gameState = -5
                elif pygame.Rect(490, 380, 300, 80).collidepoint(pos):
                    state.wind = 0
                    state.gameState = -5
                    
        elif state.gameState == 3:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if pygame.Rect(800, 300, 200, 200).collidepoint(pos):
                    # Reset all game variables on restart
                    state.gameState = 0
                    state.player1 = ""
                    state.player2 = ""
                    state.score1 = 0
                    state.score2 = 0
                    state.stepCount = 0
                    state.wind = 0
                    state.windr = random.randrange(1, 5)
                    state.p = 0
                    state.bird1 = 0
                    state.bird2 = 0
                    state.winner = 0
                    state.input = ""
                    state.text = "Enter Player_1 Name "
                    state.tim = 0
                    state.scoreV = False
                    all_sprites.empty()
                    all_sprites2.empty()        
                    collision_sprites.empty()
                    collision_sprites2.empty()

    if state.gameState == 1:
        play_sfx.stop()
        screen.blit(background_surface, (0, 0))
        screen.blit(sling_shot_surface, (300, 550))
        screen.blit(sling_shot_surface, (900, 550))
        
        # Draw HUD info
        utils.render_text_with_shadow(screen, state.player1, FONTS["comic_54"], (255, 255, 255), (0, 0, 0), (50, 20))
        utils.render_text_with_shadow(screen, f"Score: {state.score1}", FONTS["comic_36"], (255, 220, 100), (0, 0, 0), (50, 85))
        utils.render_text_with_shadow(screen, f"Opponent: {state.score2}", FONTS["comic_28"], (220, 220, 220), (0, 0, 0), (50, 130))
        
        timeCounter()
        windSetup()

        if pygame.mouse.get_pressed()[0]:
            for sprite in all_sprites:
                if isinstance(sprite, Ball) and sprite.state == 0:
                    pygame.draw.line(screen, (47, 22, 10), (310, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
                    pygame.draw.line(screen, (47, 22, 10), (360, 590), (sprite.rect.centerx, sprite.rect.centery), 19)            
                    
    elif state.gameState == 2:
        screen.blit(background_surface, (0, 0))
        screen.blit(sling_shot_surface, (300, 550))
        screen.blit(sling_shot_surface, (900, 550))
        
        # Draw HUD info on top right
        w_name = FONTS["comic_54"].size(state.player2)[0]
        w_score = FONTS["comic_36"].size(f"Score: {state.score2}")[0]
        w_opp = FONTS["comic_28"].size(f"Opponent: {state.score1}")[0]
        max_w = max(w_name, w_score, w_opp)
        x_pos = 1230 - max_w
        
        utils.render_text_with_shadow(screen, state.player2, FONTS["comic_54"], (255, 255, 255), (0, 0, 0), (x_pos, 20))
        utils.render_text_with_shadow(screen, f"Score: {state.score2}", FONTS["comic_36"], (255, 220, 100), (0, 0, 0), (x_pos, 85))
        utils.render_text_with_shadow(screen, f"Opponent: {state.score1}", FONTS["comic_28"], (220, 220, 220), (0, 0, 0), (x_pos, 130))
        
        timeCounter()
        windSetup()

        if pygame.mouse.get_pressed()[0]:
            for sprite in all_sprites2:
                if isinstance(sprite, Ball) and sprite.state == 0:
                    pygame.draw.line(screen, (47, 22, 10), (910, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
                    pygame.draw.line(screen, (47, 22, 10), (960, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
                    
    elif state.gameState == 0:
        screen.blit(background_surface2, (0, 0))
        
        # Glassmorphism container
        panel_width, panel_height = 800, 360
        panel_rect = pygame.Rect((1280 - panel_width)//2, (720 - panel_height)//2, panel_width, panel_height)
        
        # Card Shadow
        shadow_panel = panel_rect.copy()
        shadow_panel.x += 8
        shadow_panel.y += 8
        pygame.draw.rect(screen, (30, 30, 30), shadow_panel, border_radius=20)
        
        # Glass pane background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 220), (0, 0, panel_width, panel_height), border_radius=20)
        screen.blit(panel_surface, panel_rect.topleft)
        
        pygame.draw.rect(screen, (70, 130, 180), panel_rect, width=4, border_radius=20)
        
        # Text Prompt
        prompt_surf = FONTS["comic_44"].render(state.text, True, (40, 40, 40))
        prompt_rect = prompt_surf.get_rect(center=(640, 240))
        screen.blit(prompt_surf, prompt_rect)
        
        # Input field box
        input_box = pygame.Rect(340, 320, 600, 70)
        pygame.draw.rect(screen, (240, 248, 255), input_box, border_radius=10)
        pygame.draw.rect(screen, (70, 130, 180), input_box, width=2, border_radius=10)
        
        player_lbl = "P1:" if state.p == 0 else "P2:"
        lbl_surf = FONTS["comic_44"].render(player_lbl, True, (70, 130, 180))
        screen.blit(lbl_surf, (270, 330))
        
        # Typing text with blinking cursor
        cursor = "|" if (time.time() % 1.0) < 0.5 else ""
        input_surf = FONTS["sys_54"].render(state.input + cursor, True, (0, 0, 0))
        input_rect = input_surf.get_rect(midleft=(360, 355))
        screen.blit(input_surf, input_rect)
        
        # Info line
        info_surf = FONTS["sys_24"].render("Type name and press ENTER", True, (100, 100, 100))
        info_rect = info_surf.get_rect(center=(640, 415))
        screen.blit(info_surf, info_rect)
        
        victory_sfx.stop()
        play_sfx.play()
        
    elif state.gameState == 3:
        all_sprites.empty()
        all_sprites2.empty()        
        collision_sprites.empty()
        collision_sprites2.empty()
        
        screen.blit(background_surface2, (0, 0))
        
        panel_width, panel_height = 1000, 600
        panel_rect = pygame.Rect((1280 - panel_width)//2, (720 - panel_height)//2, panel_width, panel_height)
        
        shadow_panel = panel_rect.copy()
        shadow_panel.x += 8
        shadow_panel.y += 8
        pygame.draw.rect(screen, (30, 30, 30), shadow_panel, border_radius=25)
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (255, 255, 255, 220), (0, 0, panel_width, panel_height), border_radius=25)
        screen.blit(panel_surf, panel_rect.topleft)
        
        pygame.draw.rect(screen, (220, 100, 100), panel_rect, width=4, border_radius=25)
        
        w_text = state.player1 + " Wins!" if state.winner == 1 else state.player2 + " Wins!"
        utils.render_text_with_shadow(screen, w_text, FONTS["comic_64"], (180, 50, 50), (100, 100, 100), (640, 120), center=True)
        
        screen.blit(stars_surface, (560, 180))
        
        # Scoreboard
        utils.render_text_with_shadow(screen, "Score Board", FONTS["comic_48"], (30, 30, 30), (200, 200, 200), (340, 280), center=True)
        
        p1_score_txt = f"{state.player1} : {state.score1}"
        p2_score_txt = f"{state.player2} : {state.score2}"
        utils.render_text_with_shadow(screen, p1_score_txt, FONTS["comic_36"], (50, 50, 50), (220, 220, 220), (340, 355), center=True)
        utils.render_text_with_shadow(screen, p2_score_txt, FONTS["comic_36"], (50, 50, 50), (220, 220, 220), (340, 420), center=True)
        
        # High score logic & save
        utils.render_text_with_shadow(screen, f"Highest Score: {state.highScore}", FONTS["comic_40"], (70, 130, 180), (220, 220, 220), (340, 520), center=True)
        
        current_max = max(state.score1, state.score2)
        if current_max > state.highScore:
            state.highScore = current_max
            state.scoreV = True
            utils.save_high_score(state.highScore)

        if state.scoreV:
            utils.render_text_with_shadow(screen, "NEW HIGH SCORE!", FONTS["comic_44"], (220, 50, 50), (255, 200, 200), (340, 580), center=True)
            
        # Scaling / hover restart button
        restart_rect = pygame.Rect(800, 300, 200, 200)
        mouse_pos = pygame.mouse.get_pos()
        is_restart_hovered = restart_rect.collidepoint(mouse_pos)
        
        # Use pre-rendered restart buttons to avoid scale/load operations every frame
        restart_img = restart_img_hovered if is_restart_hovered else restart_img_normal
        r_rect = restart_img.get_rect(center=restart_rect.center)
        
        pygame.draw.circle(screen, (230, 240, 255) if is_restart_hovered else (255, 255, 255), restart_rect.center, 100)
        pygame.draw.circle(screen, (70, 130, 180) if is_restart_hovered else (150, 150, 150), restart_rect.center, 100, width=4)
        screen.blit(restart_img, r_rect)
        
        victory_sfx.play()

    elif state.gameState == -1 or state.gameState == -2:
        # Choose birds menu
        screen.blit(background_surface, (0, 0))
        
        tx = state.player1 if state.gameState == -1 else state.player2
        title_text = f"{tx} - Choose your Bird"
        utils.render_text_with_shadow(screen, title_text, FONTS["comic_56"], (255, 255, 255), (0, 0, 0), (640, 100), center=True)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for opt in BIRD_OPTIONS:
            bx, by = opt["pos"]
            card_rect = pygame.Rect(bx, by, 200, 350)
            is_hovered = card_rect.collidepoint(mouse_pos)
            
            # Card shadow
            shadow_card = card_rect.copy()
            shadow_card.x += 4
            shadow_card.y += 4
            pygame.draw.rect(screen, (20, 20, 20), shadow_card, border_radius=15)
            
            # Card background
            bg_alpha = 220 if is_hovered else 170
            bg_surf = pygame.Surface((200, 350), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (255, 255, 255, bg_alpha), (0, 0, 200, 350), border_radius=15)
            screen.blit(bg_surf, card_rect.topleft)
            
            # Highlights
            b_color = opt["color"] if is_hovered else (150, 150, 150)
            b_width = 4 if is_hovered else 2
            pygame.draw.rect(screen, b_color, card_rect, width=b_width, border_radius=15)
            
            # Render Image
            img_rect = opt["img"].get_rect(center=(bx + 100, by + 100))
            screen.blit(opt["img"], img_rect)
            
            name_surf = FONTS["comic_32"].render(opt["name"], True, (30, 30, 30))
            name_rect = name_surf.get_rect(center=(bx + 100, by + 190))
            screen.blit(name_surf, name_rect)
            
            # Render descriptions
            desc_lines = opt["desc"].split('\n')
            for idx, line in enumerate(desc_lines):
                d_surf = FONTS["sys_24"].render(line, True, (80, 80, 80))
                d_rect = d_surf.get_rect(center=(bx + 100, by + 240 + idx*25))
                screen.blit(d_surf, d_rect)
                
    elif state.gameState == -3:
        # Level Selection menu
        screen.blit(background_surface, (0, 0))
        
        utils.render_text_with_shadow(screen, "Choose Level", FONTS["comic_64"], (255, 255, 255), (0, 0, 0), (640, 120), center=True)
        
        l1_rect = pygame.Rect(490, 240, 300, 80)
        l2_rect = pygame.Rect(490, 350, 300, 80)
        l3_rect = pygame.Rect(490, 460, 300, 80)
        
        mouse_pos = pygame.mouse.get_pos()
        
        draw_button(screen, l1_rect, "Level 1", FONTS["comic_38"], l1_rect.collidepoint(mouse_pos))
        draw_button(screen, l2_rect, "Level 2", FONTS["comic_38"], l2_rect.collidepoint(mouse_pos))
        draw_button(screen, l3_rect, "Level 3", FONTS["comic_38"], l3_rect.collidepoint(mouse_pos))
        
    elif state.gameState == -4:
        # Wind toggle menu
        screen.blit(background_surface, (0, 0))
        
        utils.render_text_with_shadow(screen, "Wind Impulse State", FONTS["comic_64"], (255, 255, 255), (0, 0, 0), (640, 120), center=True)
        
        w1_rect = pygame.Rect(490, 260, 300, 80)
        w2_rect = pygame.Rect(490, 380, 300, 80)
        
        mouse_pos = pygame.mouse.get_pos()
        
        draw_button(screen, w1_rect, "Wind Impulse On", FONTS["comic_32"], w1_rect.collidepoint(mouse_pos), hover_color=(200, 255, 200), border_color=(50, 200, 50))
        draw_button(screen, w2_rect, "Wind Impulse Off", FONTS["comic_32"], w2_rect.collidepoint(mouse_pos), hover_color=(255, 200, 200), border_color=(200, 50, 50))
            
    elif state.gameState == -5:
        # Pre-game setup
        all_sprites.empty()
        all_sprites2.empty()
        collision_sprites.empty()
        collision_sprites2.empty()
        time.sleep(0.1)
        spriteSetup(lev)
        state.gameState = 1
        state.wait_for_mouse_release = True  # Block initial mouse drag until released

    # Reset wait_for_mouse_release when mouse is fully released
    if state.wait_for_mouse_release and not pygame.mouse.get_pressed()[0]:
        state.wait_for_mouse_release = False

    # Update physics & logic for both sprite groups
    all_sprites.update(dt)
    all_sprites.draw(screen)
    all_sprites2.update(dt)
    all_sprites2.draw(screen)

    # Overlay health values on static obstacles
    for sprite in collision_sprites:
        if isinstance(sprite, StaticObstacle) and sprite.h > 0:
            h_surf = FONTS["sys_24"].render(str(sprite.h), True, (255, 50, 50))
            h_rect = h_surf.get_rect(center=(sprite.rect.centerx, sprite.rect.centery))
            screen.blit(h_surf, h_rect)
            
    for sprite in collision_sprites2:
        if isinstance(sprite, StaticObstacle) and sprite.h > 0:
            h_surf = FONTS["sys_24"].render(str(sprite.h), True, (255, 50, 50))
            h_rect = h_surf.get_rect(center=(sprite.rect.centerx, sprite.rect.centery))
            screen.blit(h_surf, h_rect)

    # Turn progression and game over check
    if state.gameState == 1 or state.gameState == 2:
        winC = False
        for sprite in collision_sprites:
            if isinstance(sprite, StaticObstacle):
                if sprite.h > 0:
                    winC = True
        if winC == False:
            state.winner = 1
            state.gameState = 3

        winC = False
        for sprite in collision_sprites2:
            if isinstance(sprite, StaticObstacle):
                if sprite.h > 0:
                    winC = True
        if winC == False:
            state.winner = 2
            state.gameState = 3

    pygame.display.update()
