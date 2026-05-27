import pygame, sys, time, math, random, os
import const

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

class StaticObstacle(pygame.sprite.Sprite):
	def __init__(self,pos,type,groups):
		super().__init__(groups)
		self.type = type
		self.h = 100
		# Fix bug: Use self.h // 21 (which is 4 at full health) to match bounds of self.type lists (len 5)
		self.image = load_cached_image(self.type[self.h // 21])
		self.rect = self.image.get_rect(center = pos)

	# update sprite image based on health
	def update(self,dt):
		# move obstacle down if it is not obstructed by other obstacles
		collision_sprites = pygame.sprite.spritecollide(self, self.groups()[0], False)
		can_move_down = True
		for sprite in collision_sprites:
			if sprite != self and self.rect.bottom >= sprite.rect.top + 1:
				can_move_down = False
				break

		# Make falling frame-rate independent
		if can_move_down and self.rect.bottom < 700:
			self.rect.y += round(60 * dt)

		if self.h > 0:
			self.image = load_cached_image(self.type[self.h // 21])
		else:
			self.kill()


class Ball(pygame.sprite.Sprite):
	def __init__(self,position,groups,obstacles,type,gameState):
		super().__init__(groups)
		self.type = type
		self.position = position
		if gameState == 1:
			self.image = load_cached_image(self.type, False)
		else: # flip the image for player 2
			self.image = load_cached_image(self.type, True)
			
		self.rect = self.image.get_rect(center = self.position)
		self.pos = pygame.math.Vector2(self.rect.center)
		self.gmState = gameState

		self.velX = 0
		self.velY = 0
		
		self.old_rect = self.rect.copy()
		self.obstacles = obstacles
		self.state = 0 # 0: idle/aiming, 1: flying
		self.flight_time = 0.0
		self.low_speed_timer = 0.0
		self.grabbed = False  # Track if the bird is currently grabbed and being pulled
		
		if self.type == const.red:
			self.colour = (255,0,0)
		elif self.type == const.chuck:
			self.colour = (255,255,0)
		elif self.type == const.bomb:
			self.colour = (0,0,0)
		elif self.type == const.blue:
			self.colour = (0,0,255)

	def collision(self,direction):
		collision_sprites = pygame.sprite.spritecollide(self,self.obstacles,False)
		
		if collision_sprites:
			if direction == 'horizontal':
				for sprite in collision_sprites:
					# collision on the right
					if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left:
						self.rect.right = sprite.rect.left
						self.pos.x = self.rect.centerx
						self.velX *= -0.7

					# collision on the left
					if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right:
						self.rect.left = sprite.rect.right
						self.pos.x = self.rect.centerx
						self.velX *= -0.7

			if direction == 'vertical':
				for sprite in collision_sprites:
					# collision on the bottom
					if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top:
						self.rect.bottom = sprite.rect.top
						self.pos.y = self.rect.centery
						self.velY *= -0.7

					# collision on the top
					if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
						self.rect.top = sprite.rect.bottom
						self.pos.y = self.rect.centery
						self.velY *= -0.7

		# reduce health of static obstacles
		global score1,score2
		scr = 0
		for sprite in collision_sprites:
			if isinstance(sprite,StaticObstacle):
				if self.type == const.red:
					sprite.h -= 50
					scr += 50
				elif self.type == const.chuck:
					if sprite.type == const.wood:
						sprite.h -= 70
						scr += 70
					else:
						sprite.h -= 34
						scr += 34
				elif self.type == const.bomb:
					if sprite.type == const.stone:
						sprite.h -= 70
						scr += 70
					else:
						sprite.h -= 34
						scr += 34
				elif self.type == const.blue:
					if sprite.type == const.ice:
						sprite.h -= 70
						scr += 70
					else:
						sprite.h -= 34
						scr += 34

				if self.gmState == 1:
					score1 += scr
				elif self.gmState == 2:
					score2 += scr

				if sprite.h <= 0:
					sprite.kill()

	def window_collision(self,direction):
		if direction == 'horizontal':
			if self.rect.left < 0:
				self.rect.left = 0
				self.pos.x = self.rect.centerx
				self.velX *= -1
			if self.rect.right > 1280:
				self.rect.right = 1280
				self.pos.x = self.rect.centerx
				self.velX *= -1

		if direction == 'vertical':
			if self.rect.top < 0:
				self.rect.top = 0
				self.pos.y = self.rect.centery
				self.velY *= -1
			if self.rect.bottom > 720:
				self.rect.bottom = 720
				self.pos.y = self.rect.centery
				self.velY *= -0.7

	def update(self,dt):
		global gameState
		self.old_rect = self.rect.copy()

		if self.state == 1:
			self.pos.x += self.velX * dt
			self.rect.centerx = round(self.pos.x)
			self.collision('horizontal')
			
			self.pos.y += self.velY * dt
			self.rect.centery = round(self.pos.y)
			self.collision('vertical')
			self.window_collision('vertical')

			self.velY += 1000 * dt

			if wind == 1:
				global windr
				if windr == 1:
					self.velX += 150 * dt
					self.velY += 150 * dt
				elif windr == 2:
					self.velX -= 150 * dt
					self.velY += 150 * dt
				elif windr == 3:
					self.velX += 150 * dt
					self.velY -= 150 * dt
				elif windr == 4:
					self.velX -= 150 * dt
					self.velY -= 150 * dt

			# Ground / Obstacle rolling friction
			on_ground = self.rect.bottom >= 720
			if not on_ground:
				collision_sprites = pygame.sprite.spritecollide(self, self.obstacles, False)
				for sprite in collision_sprites:
					if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top:
						on_ground = True
						break
			
			if on_ground:
				self.velX *= (1 - 2.0 * dt)  # Friction to slow down rolling balls

			# Speed & flight time checks to prevent softlocks
			speed = math.hypot(self.velX, self.velY)
			if speed < 15:
				self.low_speed_timer += dt
			else:
				self.low_speed_timer = 0.0

			self.flight_time += dt

			should_kill = False
			if self.low_speed_timer > 1.2:
				should_kill = True
				print("Ball killed due to low speed")
			elif self.flight_time > 8.0:
				should_kill = True
				print("Ball killed due to flight timeout")

			if should_kill:
				self.kill_and_next_turn()

		# if ball is out of the screen bounds, kill the ball and trigger next turn
		if self.rect.left > 1280 or self.rect.right < 0:
			print("Ball killed due to out of screen bounds")
			self.kill_and_next_turn()
			
		# Handle aiming mechanics (Grabbing and Pulling with distance clamping)
		if self.state == 0 and self.gmState == gameState and not wait_for_mouse_release:
			mouse_pressed = pygame.mouse.get_pressed()[0]
			mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
			slingshot_center = pygame.math.Vector2(self.position)
			
			if mouse_pressed:
				if not self.grabbed:
					# Check if mouse clicked near the bird to grab it (100px radius)
					if mouse_pos.distance_to(slingshot_center) <= 100:
						self.grabbed = True
						
				if self.grabbed:
					# Pull vector relative to slingshot center
					pull = mouse_pos - slingshot_center
					# Clamp the pull vector to a maximum distance (200px pull radius)
					if pull.length() > 200:
						pull = pull.normalize() * 200
						
					# Prevent clipping into the ground while aiming
					max_pull_y = 720 - (self.rect.height / 2) - slingshot_center.y
					if pull.y > max_pull_y:
						pull *= (max_pull_y / pull.y)
						
					self.rect.center = (round(slingshot_center.x + pull.x), round(slingshot_center.y + pull.y))
					self.pos = pygame.math.Vector2(self.rect.center)
					self.velX = pull.x * -8
					self.velY = pull.y * -8
					
					self.draw_trajectory_preview()
			else:
				# Mouse released
				if self.grabbed:
					pull = pygame.math.Vector2(self.rect.center) - slingshot_center
					# Minimum pull of 15px to trigger a launch, otherwise cancel pull
					if pull.length() > 15:
						self.state = 1
						self.flight_time = 0.0
						self.low_speed_timer = 0.0
						# Play sound
						if self.type == const.red:
							red_sfx.play()
						elif self.type == const.chuck:
							chuck_sfx.play()
						elif self.type == const.bomb:
							bomb_sfx.play()
						elif self.type == const.blue:
							blues_sfx.play()
					else:
						# Reset to slingshot center if pull was too small
						self.rect.center = self.position
						self.pos = pygame.math.Vector2(self.rect.center)
						self.velX = 0
						self.velY = 0
					self.grabbed = False

	def kill_and_next_turn(self):
		global gameState
		self.kill()
		if self.gmState == 1:
			gameState = 2
			step(gameState)
		elif self.gmState == 2:
			gameState = 1
			step(gameState)
		print("Killed ball and transitioned turns")

	def draw_trajectory_preview(self):
		temp_pos = pygame.math.Vector2(self.rect.center)
		temp_vel = pygame.math.Vector2(self.velX, self.velY)
		points = []
		sim_dt = 1 / 60.0  # Exact fixed physics time step (1/60s)
		
		# Physics simulation loop matching the game loop exactly
		for step in range(120):
			if step % 3 == 0:
				points.append((round(temp_pos.x), round(temp_pos.y)))
				
			# 1. Update position
			temp_pos.x += temp_vel.x * sim_dt
			temp_pos.y += temp_vel.y * sim_dt
			
			# Ceiling bounce simulation matching window_collision
			if temp_pos.y < (self.rect.height / 2):
				temp_pos.y = (self.rect.height / 2)
				temp_vel.y *= -1
				
			# 2. Update velocity
			temp_vel.y += 1000 * sim_dt
			if wind == 1:
				global windr
				if windr == 1:
					temp_vel.x += 150 * sim_dt
					temp_vel.y += 150 * sim_dt
				elif windr == 2:
					temp_vel.x -= 150 * sim_dt
					temp_vel.y += 150 * sim_dt
				elif windr == 3:
					temp_vel.x += 150 * sim_dt
					temp_vel.y -= 150 * sim_dt
				elif windr == 4:
					temp_vel.x -= 150 * sim_dt
					temp_vel.y -= 150 * sim_dt
					
			# Ground collision matching actual physical bottom > 720
			ground_y = 720 - (self.rect.height / 2)
			if temp_pos.y > ground_y:
				if step % 3 == 0:
					points.append((round(temp_pos.x), round(ground_y)))
				break
				
		for pt in points:
			if 0 <= pt[0] <= 1280 and 0 <= pt[1] <= 720:
				pygame.draw.circle(screen, self.colour, pt, 4)


# UI Helper functions
def render_text_with_shadow(surface, text, font, color, shadow_color, pos, center=False, shadow_offset=(3, 3)):
    shadow_surf = font.render(text, True, shadow_color)
    main_surf = font.render(text, True, color)
    if center:
        rect = main_surf.get_rect(center=pos)
        shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]))
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(main_surf, rect)
    else:
        surface.blit(shadow_surf, (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]))
        surface.blit(main_surf, pos)

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


stepCount = 0
def step(gameState):
	global stepCount
	print("step",stepCount)
	stepCount +=1
	global windr
	windr = random.randrange(1,5)
	if gameState != 3:
		r = random.randrange(0,4)
		k = [const.red,const.chuck,const.bomb,const.blue]
		if stepCount > 1:
			gS = gameState
			if gS == 1:
				Ball((350,570),all_sprites,collision_sprites,k[r],1)
			if gS == 2:
				Ball((920,570),all_sprites2,collision_sprites2,k[r],2)


def spriteSetup(level):
	for i in level:
		StaticObstacle(i[0],i[1], [all_sprites,collision_sprites] if i[2] == 1 else [all_sprites2,collision_sprites2])
	
	Ball((350,570),all_sprites,collision_sprites,bird1,1)
	Ball((920,570),all_sprites2,collision_sprites2,bird2,2)

def windSetup():
	global wind,windr
	arrow_surface = pygame.transform.rotate(arrow, 0)
	if wind == 1:
		if windr == 1:
			arrow_surface = pygame.transform.rotate(arrow, 315)
		elif windr == 2:
			arrow_surface = pygame.transform.rotate(arrow, 225)
		elif windr == 3:
			arrow_surface = pygame.transform.rotate(arrow, 45)
		elif windr == 4:
			arrow_surface = pygame.transform.rotate(arrow, 135)
		screen.blit(arrow_surface, (640, 100))

def timeCounter():
	global tim,stk1,stk2,winner,gameState
	if tim==0:
		stk1 = time.time()
		tim=1
	stk2 = time.time()
	
	rem_time = max(0, round(300-(stk2-stk1)))
	time_font = pygame.font.Font(None, 70)
	render_text_with_shadow(screen, str(rem_time), time_font, (255, 255, 255), (0, 0, 0), (640, 50), center=True)
	
	if stk2-stk1 > 300:
		if score1 > score2:
			winner = 1
		else:
			winner = 2
		gameState = 3

# general setup
pygame.init()
screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption("Angry Birds")
clock = pygame.time.Clock()  # Game timing clock

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

# Game State and variables
gameState = 0  # 0: input, 1: player1 turn, 2: player2 turn, 3: game over, -1: P1 bird, -2: P2 bird, -3: level, -4: wind, -5: setup
tim = 0
input = ""
text = "Enter Player_1 Name "
player1 = ""
player2 = ""
score1 = 0
score2 = 0
p = 0
bird1 = 0
bird2 = 0
wind = 0
windr = random.randrange(1,5)
winner = 0
highScore = load_high_score()
scoreV = False
wait_for_mouse_release = False  # Track if we need to wait for mouse button release after state changes

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
			
		if gameState == 0:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_BACKSPACE:
					input = input[:-1]
				elif p == 0 and event.key == pygame.K_RETURN:
					player1 = input.strip() if input.strip() else "Player 1"
					input = ""
					text = "Enter Player_2 Name "
					p = 1
				elif p == 1 and event.key == pygame.K_RETURN:
					player2 = input.strip() if input.strip() else "Player 2"
					input = ""
					gameState = -1
				else:
					if event.unicode.isprintable() and len(input) < 15:
						input += event.unicode
						
		elif gameState == -1 or gameState == -2:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = event.pos
				if pygame.Rect(220, 200, 200, 350).collidepoint(pos):
					if gameState == -1:
						bird1 = const.red
						gameState = -2
					else:
						bird2 = const.red
						gameState = -3
				elif pygame.Rect(460, 200, 200, 350).collidepoint(pos):
					if gameState == -1:
						bird1 = const.chuck
						gameState = -2
					else:
						bird2 = const.chuck
						gameState = -3
				elif pygame.Rect(700, 200, 200, 350).collidepoint(pos):
					if gameState == -1:
						bird1 = const.bomb
						gameState = -2
					else:
						bird2 = const.bomb
						gameState = -3
				elif pygame.Rect(940, 200, 200, 350).collidepoint(pos):
					if gameState == -1:
						bird1 = const.blue
						gameState = -2
					else:
						bird2 = const.blue
						gameState = -3
						
		elif gameState == -3:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = event.pos
				if pygame.Rect(490, 240, 300, 80).collidepoint(pos):
					lev = const.level1
					gameState = -4
				elif pygame.Rect(490, 350, 300, 80).collidepoint(pos):
					lev = const.level2
					gameState = -4
				elif pygame.Rect(490, 460, 300, 80).collidepoint(pos):
					lev = const.level3
					gameState = -4
					
		elif gameState == -4:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = event.pos
				if pygame.Rect(490, 260, 300, 80).collidepoint(pos):
					wind = 1
					gameState = -5
				elif pygame.Rect(490, 380, 300, 80).collidepoint(pos):
					wind = 0
					gameState = -5
					
		elif gameState == 3:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				pos = event.pos
				if pygame.Rect(800, 300, 200, 200).collidepoint(pos):
					# Reset all game variables on restart
					gameState = 0
					player1 = ""
					player2 = ""
					score1 = 0
					score2 = 0
					stepCount = 0
					wind = 0
					windr = random.randrange(1,5)
					p = 0
					bird1 = 0
					bird2 = 0
					winner = 0
					input = ""
					text = "Enter Player_1 Name "
					tim = 0
					scoreV = False
					all_sprites.empty()
					all_sprites2.empty()		
					collision_sprites.empty()
					collision_sprites2.empty()

	if gameState == 1:
		play_sfx.stop()
		screen.blit(background_surface, (0, 0))
		screen.blit(sling_shot_surface, (300, 550))
		screen.blit(sling_shot_surface, (900, 550))
		
		# Draw HUD info
		render_text_with_shadow(screen, player1, pygame.font.Font(const.font, 54), (255, 255, 255), (0, 0, 0), (50, 20))
		render_text_with_shadow(screen, f"Score: {score1}", pygame.font.Font(const.font, 36), (255, 220, 100), (0, 0, 0), (50, 85))
		render_text_with_shadow(screen, f"Opponent: {score2}", pygame.font.Font(const.font, 28), (220, 220, 220), (0, 0, 0), (50, 130))
		
		timeCounter()
		windSetup()

		if pygame.mouse.get_pressed()[0]:
			for sprite in all_sprites:
				if isinstance(sprite,Ball) and sprite.state == 0:
					pygame.draw.line(screen, (47, 22, 10), (310, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
					pygame.draw.line(screen, (47, 22, 10), (360, 590), (sprite.rect.centerx, sprite.rect.centery), 19)			
					
	elif gameState == 2:
		screen.blit(background_surface, (0, 0))
		screen.blit(sling_shot_surface, (300, 550))
		screen.blit(sling_shot_surface, (900, 550))
		
		# Draw HUD info on top right
		p2_name_font = pygame.font.Font(const.font, 54)
		p2_score_font = pygame.font.Font(const.font, 36)
		p2_opp_font = pygame.font.Font(const.font, 28)
		
		w_name = p2_name_font.size(player2)[0]
		w_score = p2_score_font.size(f"Score: {score2}")[0]
		w_opp = p2_opp_font.size(f"Opponent: {score1}")[0]
		max_w = max(w_name, w_score, w_opp)
		x_pos = 1230 - max_w
		
		render_text_with_shadow(screen, player2, p2_name_font, (255, 255, 255), (0, 0, 0), (x_pos, 20))
		render_text_with_shadow(screen, f"Score: {score2}", p2_score_font, (255, 220, 100), (0, 0, 0), (x_pos, 85))
		render_text_with_shadow(screen, f"Opponent: {score1}", p2_opp_font, (220, 220, 220), (0, 0, 0), (x_pos, 130))
		
		timeCounter()
		windSetup()

		if pygame.mouse.get_pressed()[0]:
			for sprite in all_sprites2:
				if isinstance(sprite,Ball) and sprite.state == 0:
					pygame.draw.line(screen, (47, 22, 10), (910, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
					pygame.draw.line(screen, (47, 22, 10), (960, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
					
	elif gameState == 0:
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
		font_prompt = pygame.font.Font(const.font, 44)
		prompt_surf = font_prompt.render(text, True, (40, 40, 40))
		prompt_rect = prompt_surf.get_rect(center=(640, 240))
		screen.blit(prompt_surf, prompt_rect)
		
		# Input field box
		input_box = pygame.Rect(340, 320, 600, 70)
		pygame.draw.rect(screen, (240, 248, 255), input_box, border_radius=10)
		pygame.draw.rect(screen, (70, 130, 180), input_box, width=2, border_radius=10)
		
		player_lbl = "P1:" if p == 0 else "P2:"
		lbl_font = pygame.font.Font(const.font, 44)
		lbl_surf = lbl_font.render(player_lbl, True, (70, 130, 180))
		screen.blit(lbl_surf, (270, 330))
		
		# Typing text with blinking cursor
		input_font = pygame.font.Font(None, 54)
		cursor = "|" if (time.time() % 1.0) < 0.5 else ""
		input_surf = input_font.render(input + cursor, True, (0, 0, 0))
		input_rect = input_surf.get_rect(midleft=(360, 355))
		screen.blit(input_surf, input_rect)
		
		# Info line
		info_font = pygame.font.Font(None, 24)
		info_surf = info_font.render("Type name and press ENTER", True, (100, 100, 100))
		info_rect = info_surf.get_rect(center=(640, 415))
		screen.blit(info_surf, info_rect)
		
		victory_sfx.stop()
		play_sfx.play()
		
	elif gameState == 3:
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
		
		w_text = player1 + " Wins!" if winner == 1 else player2 + " Wins!"
		font_win = pygame.font.Font(const.font, 64)
		render_text_with_shadow(screen, w_text, font_win, (180, 50, 50), (100, 100, 100), (640, 120), center=True)
		
		screen.blit(stars_surface, (560, 180))
		
		# Scoreboard
		sb_font = pygame.font.Font(const.font, 48)
		render_text_with_shadow(screen, "Score Board", sb_font, (30, 30, 30), (200, 200, 200), (340, 280), center=True)
		
		score_detail_font = pygame.font.Font(const.font, 36)
		p1_score_txt = f"{player1} : {score1}"
		p2_score_txt = f"{player2} : {score2}"
		render_text_with_shadow(screen, p1_score_txt, score_detail_font, (50, 50, 50), (220, 220, 220), (340, 355), center=True)
		render_text_with_shadow(screen, p2_score_txt, score_detail_font, (50, 50, 50), (220, 220, 220), (340, 420), center=True)
		
		# High score logic & save
		hs_font = pygame.font.Font(const.font, 40)
		render_text_with_shadow(screen, f"Highest Score: {highScore}", hs_font, (70, 130, 180), (220, 220, 220), (340, 520), center=True)
		
		current_max = max(score1, score2)
		if current_max > highScore:
			highScore = current_max
			scoreV = True
			save_high_score(highScore)

		if scoreV:
			victory_font = pygame.font.Font(const.font, 44)
			render_text_with_shadow(screen, "NEW HIGH SCORE!", victory_font, (220, 50, 50), (255, 200, 200), (340, 580), center=True)
			
		# Scaling / hover restart button
		restart_rect = pygame.Rect(800, 300, 200, 200)
		mouse_pos = pygame.mouse.get_pos()
		is_restart_hovered = restart_rect.collidepoint(mouse_pos)
		
		btn_size = 210 if is_restart_hovered else 190
		restart_img = pygame.transform.scale(pygame.image.load("./resources/img/restart.png").convert_alpha(), (btn_size, btn_size))
		r_rect = restart_img.get_rect(center=restart_rect.center)
		
		pygame.draw.circle(screen, (230, 240, 255) if is_restart_hovered else (255, 255, 255), restart_rect.center, 100)
		pygame.draw.circle(screen, (70, 130, 180) if is_restart_hovered else (150, 150, 150), restart_rect.center, 100, width=4)
		screen.blit(restart_img, r_rect)
		
		victory_sfx.play()

	elif gameState == -1 or gameState == -2:
		# Choose birds menu
		screen.blit(background_surface, (0, 0))
		
		tx = player1 if gameState == -1 else player2
		title_text = f"{tx} - Choose your Bird"
		font_title = pygame.font.Font(const.font, 56)
		render_text_with_shadow(screen, title_text, font_title, (255, 255, 255), (0, 0, 0), (640, 100), center=True)
		
		bird_options = [
			{"type": const.red, "img": RED, "name": "Red", "pos": (220, 200), "desc": "Standard Bird\nBalanced stats", "color": (255, 0, 0)},
			{"type": const.chuck, "img": CHUCK, "name": "Chuck", "pos": (460, 200), "desc": "Wood Piercer\nExtra pierce vs Wood", "color": (255, 255, 0)},
			{"type": const.bomb, "img": BOMB, "name": "Bomb", "pos": (700, 200), "desc": "Stone Piercer\nExtra pierce vs Stone", "color": (50, 50, 50)},
			{"type": const.blue, "img": BLUE, "name": "Blue", "pos": (940, 200), "desc": "Ice Piercer\nExtra pierce vs Ice", "color": (0, 191, 255)},
		]
		
		mouse_pos = pygame.mouse.get_pos()
		
		for opt in bird_options:
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
			
			font_name = pygame.font.Font(const.font, 32)
			name_surf = font_name.render(opt["name"], True, (30, 30, 30))
			name_rect = name_surf.get_rect(center=(bx + 100, by + 190))
			screen.blit(name_surf, name_rect)
			
			# Render descriptions
			font_desc = pygame.font.Font(None, 24)
			desc_lines = opt["desc"].split('\n')
			for idx, line in enumerate(desc_lines):
				d_surf = font_desc.render(line, True, (80, 80, 80))
				d_rect = d_surf.get_rect(center=(bx + 100, by + 240 + idx*25))
				screen.blit(d_surf, d_rect)
				
	elif gameState == -3:
		# Level Selection menu
		screen.blit(background_surface, (0, 0))
		
		font_title = pygame.font.Font(const.font, 64)
		render_text_with_shadow(screen, "Choose Level", font_title, (255, 255, 255), (0, 0, 0), (640, 120), center=True)
		
		btn_font = pygame.font.Font(const.font, 38)
		l1_rect = pygame.Rect(490, 240, 300, 80)
		l2_rect = pygame.Rect(490, 350, 300, 80)
		l3_rect = pygame.Rect(490, 460, 300, 80)
		
		mouse_pos = pygame.mouse.get_pos()
		
		draw_button(screen, l1_rect, "Level 1", btn_font, l1_rect.collidepoint(mouse_pos))
		draw_button(screen, l2_rect, "Level 2", btn_font, l2_rect.collidepoint(mouse_pos))
		draw_button(screen, l3_rect, "Level 3", btn_font, l3_rect.collidepoint(mouse_pos))
		
	elif gameState == -4:
		# Wind toggle menu
		screen.blit(background_surface, (0, 0))
		
		font_title = pygame.font.Font(const.font, 64)
		render_text_with_shadow(screen, "Wind Impulse State", font_title, (255, 255, 255), (0, 0, 0), (640, 120), center=True)
		
		btn_font = pygame.font.Font(const.font, 32)
		w1_rect = pygame.Rect(490, 260, 300, 80)
		w2_rect = pygame.Rect(490, 380, 300, 80)
		
		mouse_pos = pygame.mouse.get_pos()
		
		draw_button(screen, w1_rect, "Wind Impulse On", btn_font, w1_rect.collidepoint(mouse_pos), hover_color=(200, 255, 200), border_color=(50, 200, 50))
		draw_button(screen, w2_rect, "Wind Impulse Off", btn_font, w2_rect.collidepoint(mouse_pos), hover_color=(255, 200, 200), border_color=(200, 50, 50))
			
	elif gameState == -5:
		# Pre-game setup
		all_sprites.empty()
		all_sprites2.empty()
		collision_sprites.empty()
		collision_sprites2.empty()
		time.sleep(0.1)
		spriteSetup(lev)
		gameState = 1
		wait_for_mouse_release = True  # Block initial mouse drag until released

	# Reset wait_for_mouse_release when mouse is fully released
	if wait_for_mouse_release and not pygame.mouse.get_pressed()[0]:
		wait_for_mouse_release = False

	# Update physics & logic for both sprite groups
	all_sprites.update(dt)
	all_sprites.draw(screen)
	all_sprites2.update(dt)
	all_sprites2.draw(screen)

	# Overlay health values on static obstacles
	for sprite in collision_sprites:
		if isinstance(sprite, StaticObstacle) and sprite.h > 0:
			health_font = pygame.font.Font(None, 24)
			h_surf = health_font.render(str(sprite.h), True, (255, 50, 50))
			h_rect = h_surf.get_rect(center=(sprite.rect.centerx, sprite.rect.centery))
			screen.blit(h_surf, h_rect)
			
	for sprite in collision_sprites2:
		if isinstance(sprite, StaticObstacle) and sprite.h > 0:
			health_font = pygame.font.Font(None, 24)
			h_surf = health_font.render(str(sprite.h), True, (255, 50, 50))
			h_rect = h_surf.get_rect(center=(sprite.rect.centerx, sprite.rect.centery))
			screen.blit(h_surf, h_rect)

	# Turn progression and game over check
	if gameState == 1 or gameState == 2:
		winC = False
		for sprite in collision_sprites:
			if isinstance(sprite, StaticObstacle):
				if sprite.h > 0:
					winC = True
		if winC == False:
			winner = 1
			gameState = 3

		winC = False
		for sprite in collision_sprites2:
			if isinstance(sprite, StaticObstacle):
				if sprite.h > 0:
					winC = True
		if winC == False:
			winner = 2
			gameState = 3

	pygame.display.update()
