import pygame, sys, time , math
import const
import random


class StaticObstacle(pygame.sprite.Sprite):
	def __init__(self,pos,type,groups):
		super().__init__(groups)
		self.type = type
		self.h=100
		self.image = pygame.image.load(type[self.h//34]).convert_alpha()
		self.rect = self.image.get_rect(center = pos)

	# update sprite image based on health
	def update(self,dt):

		# self.rect.bottom += .5
		# move obstacle down if it is not obstructed by other obstacles
		collision_sprites = pygame.sprite.spritecollide(self, self.groups()[0], False)
		can_move_down = True
		for sprite in collision_sprites:
			if sprite != self and self.rect.bottom >= sprite.rect.top +1:
				can_move_down = False
				# self.rect.bottom = sprite.rect.top -1
				break

		if can_move_down and self.rect.bottom < 700:
			self.rect.y += 1


		if self.h > 0:
			self.image = pygame.image.load(self.type[self.h//21]).convert_alpha()
		else:
			self.kill()


class Ball(pygame.sprite.Sprite):
	def __init__(self,position,groups,obstacles,type,gameState):
		super().__init__(groups)
		self.type = type
		self.position = position
		if gameState == 1:
			self.image = pygame.image.load(self.type).convert_alpha()
		else: # flip the image for player 2
			self.image = pygame.transform.flip(pygame.image.load(self.type).convert_alpha(),True,False)
			
		self.rect = self.image.get_rect(center = self.position)
		self.pos = pygame.math.Vector2(self.rect.center)
		self.gmState = gameState

		self.velX = 0
		self.velY = 0
		# self.c=0
		
		self.old_rect = self.rect.copy()
		self.obstacles = obstacles
		self.state = 0 # 0: idle, 1: moving
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
		
		# if self.rect.colliderect(self.player.rect):
		# 	collision_sprites.append(self.player)

		if collision_sprites:
			if direction == 'horizontal':
				for sprite in collision_sprites:
					# collision on the right
					if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left:
						self.rect.right = sprite.rect.left
						self.pos.x = self.rect.x
						self.velX *= -1
						self.velX *= 0.7


					# collision on the left
					if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right:
						self.rect.left = sprite.rect.right
						self.pos.x = self.rect.x
						self.velX *= -1
						self.velX *= 0.7

		
			if direction == 'vertical':
				for sprite in collision_sprites:
					# collision on the bottom
					if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top:
						self.rect.bottom = sprite.rect.top
						self.pos.y = self.rect.y
						self.velY *= -1
						self.velY *= 0.7

					# collision on the top
					if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
						self.rect.top = sprite.rect.bottom
						self.pos.y = self.rect.y
						self.velY *= -1
						self.velY *= 0.7

		# reduce health of static obstacles
		global score1,score2
		scr=0
		for sprite in collision_sprites:
			if isinstance(sprite,StaticObstacle):
				if self.type == const.red:
					sprite.h -= 50
					scr+= 50
				elif self.type == const.chuck:
					if sprite.type == const.wood:
						sprite.h -= 70
						scr+= 70
					else:
						sprite.h -= 34
						scr+= 34
				elif self.type == const.bomb:
					if sprite.type == const.stone:
						sprite.h -= 70
						scr+= 70
					else:
						sprite.h -= 34
						scr+= 34
				elif self.type == const.blue:
					if sprite.type == const.ice:
						sprite.h -= 70
						scr+= 70
					else:
						sprite.h -= 34
						scr+= 34

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
				self.pos.x = self.rect.x
				self.velX *= -1
			if self.rect.right > 1280:
				self.rect.right = 1280
				self.pos.x = self.rect.x
				self.velX *= -1

		if direction == 'vertical':
			if self.rect.top < 0:
				self.rect.top = 0
				self.pos.y = self.rect.y
				self.velY *= -1
			if self.rect.bottom > 720:
				self.rect.bottom = 720
				self.pos.y = self.rect.y
				self.velY *= -1
			# self.c+=1
			# if self.c > 10:
			# 	self.kill()
			# 	if self.gmState == 1:
			# 		gameState = 2
			# 		step(gameState)
			# 	elif self.gmState == 2:
			# 		gameState = 1
			# 		step(gameState)
			# 	print("killed")

	def update(self,dt):

		global gameState
		# print(self.velX,self.velY)
		# print(self.launch)

		self.old_rect = self.rect.copy()

		if self.state == 1:

			self.pos.x += self.velX * dt
			self.rect.x = round(self.pos.x)
			self.collision('horizontal')
			#self.window_collision('horizontal')
			self.pos.y += self.velY * dt
			self.rect.y = round(self.pos.y)
			self.collision('vertical')
			self.window_collision('vertical')

			self.velY += 1000 * dt

			if wind == 1:
				# wind impulse
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

		# if ball is out of the screen, kill the ball
		if self.rect.left > 1280 or self.rect.right < 0:
			self.kill()
			if self.gmState == 1:
				gameState = 2
				step(gameState)
			elif self.gmState == 2:
				gameState = 1
				step(gameState)
			print("killed")
		# if ball is not moving, kill the ball
		if self.velX == 0 and self.velY == 0 and self.state == 2:
			self.kill()
			if self.gmState == 1:
				gameState = 2
				step(gameState)
			elif self.gmState == 2:
				gameState = 1
				step(gameState)
			print("killed")

			


		# launch the ball when the ball is pulled back by the mouse and released
		
		if pygame.mouse.get_pressed()[0] and self.gmState == gameState and self.state == 0:
			self.pos.x = pygame.mouse.get_pos()[0] - self.rect.width/2
			self.pos.y = pygame.mouse.get_pos()[1] - self.rect.height/2
			self.rect.x = round(self.pos.x)
			self.rect.y = round(self.pos.y)
			self.velX = (self.rect.x - self.position[0] +45) * -8
			self.velY = (self.rect.y - self.position[1] +45) * -8
			# draw projectile path
			if gameState == 1:
				pygame.draw.arc(screen, self.colour, (self.rect.centerx, self.rect.centery - (self.velY**2)/(2000), -2*self.velX*self.velY/(1000), (self.velY**2)/(1000)), 0, math.pi, 5, )
			elif gameState == 2:
				pygame.draw.arc(screen, self.colour, (self.rect.centerx - 2*self.velX*self.velY/(1000), self.rect.centery - (self.velY**2)/(2000), 2*self.velX*self.velY/(1000), (self.velY**2)/(1000)), 0, math.pi, 5)
		
		# mouse release
		if pygame.mouse.get_just_released()[0] and self.gmState == gameState and self.state == 0:
			if self.type == const.red:
				red_sfx.play()
			elif self.type == const.chuck:
				chuck_sfx.play()
			elif self.type == const.bomb:
				bomb_sfx.play()
			elif self.type == const.blue:
				blues_sfx.play()

		if not pygame.mouse.get_pressed()[0] and (self.velX != 0 or self.velY != 0):
			self.state = 1

stepCount = 0
def step(gameState):
	global stepCount
	print("step",stepCount)
	stepCount +=1
	global windr
	windr= random.randrange(1,5)
	if gameState != 3:
		r= random.randrange(0,4)
		k=[const.red,const.chuck,const.bomb,const.blue]
		if stepCount > 1:
			gS =gameState
			if gS == 1:
				Ball((350,570),all_sprites,collision_sprites,k[r],1)
			if gS == 2:
				Ball((920,570),all_sprites2,collision_sprites2,k[r],2)


def spriteSetup(level):
	# sprite setup
	for i in level:
		StaticObstacle(i[0],i[1], [all_sprites,collision_sprites] if i[2] == 1 else [all_sprites2,collision_sprites2])
	
	Ball((350,570),all_sprites,collision_sprites,bird1,1)
	Ball((920,570),all_sprites2,collision_sprites2,bird2,2)
	r= random.randrange(1,5)

def windSetup():
	# wind setup
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
		screen.blit(arrow_surface, (640, 100))  # Draw the arrow image

def timeCounter():
	global tim,stk1,stk2,winner,gameState
	if tim==0:
		stk1 = time.time()
		tim=1
	stk2 = time.time()
	time_surface = pygame.font.Font(None, 70).render(str(round(300-(stk2-stk1))), True, (0, 0, 0))
	screen.blit(time_surface, (640, 50))  # Draw the time
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


background_surface = pygame.image.load("./resources/images/background2.jpg").convert()  # Load the background image
background_surface2 = pygame.image.load("./resources/images/background1.jpg").convert()  # Load the background image
sling_shot_surface = pygame.image.load("./resources/images/sling.png").convert_alpha()
stars_surface = pygame.image.load("./resources/images/stars.png").convert_alpha()
RED = pygame.image.load(const.red).convert_alpha()
CHUCK = pygame.image.load(const.chuck).convert_alpha()
BOMB = pygame.image.load(const.bomb).convert_alpha()
BLUE = pygame.image.load(const.blue).convert_alpha()
arrow = pygame.image.load("./resources/img/arrow.png").convert_alpha()


gameState = 0  # 0: input, 1: player1 turn, 2: player2 turn, 3: game over, -1: player1 chose bird, -2: player2 chose bird, -3: chose level
tim=0
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
highScore = 0
scoreV = False


# game loop
last_time = time.time()
while True:
	# print(gameState)
	# print(winner)
	# print(player1,player2)
	# delta time
	dt = time.time() - last_time
	last_time = time.time()
	
	# event loop
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if gameState == 0 and event.type == pygame.KEYDOWN:
			if event.key == pygame.K_BACKSPACE:
				input = input[:-1]
			elif p==0 and event.key == pygame.K_RETURN:
				player1 = input
				input = ""
				text = "Enter Player_2 Name "
				p = 1
			elif p==1 and event.key == pygame.K_RETURN:
				player2 = input
				input = ""
				gameState = -1
			else:
				input += event.unicode
	if gameState == 1:
		play_sfx.stop()
		player1_surface = pygame.font.Font(const.font, 64).render(player1, True, (0, 0, 0))
		# drawing and updating the screen
		screen.blit(background_surface, (0, 0))  # Draw the background image
		screen.blit(sling_shot_surface, (300, 550))  # Draw the slingshot image
		screen.blit(sling_shot_surface, (900, 550))  # Draw the slingshot image
		screen.blit(player1_surface, (50, 0))  # Draw the player1 name
		# display time
		timeCounter()
		windSetup()

		# draw linesfrom slingshot to ball
		if pygame.mouse.get_pressed()[0]:
			for sprite in all_sprites:
				if isinstance(sprite,Ball) and sprite.state == 0:
					pygame.draw.line(screen, (47, 22, 10), (310, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
					pygame.draw.line(screen, (47, 22, 10), (360, 590), (sprite.rect.centerx, sprite.rect.centery), 19)			
	elif gameState == 2:
		player2_surface = pygame.font.Font(const.font, 64).render(player2, True, (0, 0, 0))
		# drawing and updating the screen
		screen.blit(background_surface, (0, 0))
		screen.blit(sling_shot_surface, (300, 550))
		screen.blit(sling_shot_surface, (900, 550))
		screen.blit(player2_surface, (1200-len(player2)*30, 0))
		# display time
		timeCounter()
		windSetup()

		if pygame.mouse.get_pressed()[0]:
			for sprite in all_sprites2:
				if isinstance(sprite,Ball) and sprite.state == 0:
					pygame.draw.line(screen, (47, 22, 10), (910, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
					pygame.draw.line(screen, (47, 22, 10), (960, 590), (sprite.rect.centerx, sprite.rect.centery), 19)
	elif gameState == 0:
		screen.blit(background_surface2, (0, 0))

		base_font = pygame.font.Font(None, 74)
		
		text_surface = base_font.render(text, True, (0, 0, 0))
		text_surface2 = base_font.render(input, True, (0, 0, 0))
		screen.blit(text_surface, (100, 100))
		screen.blit(text_surface2, (100, 200))
		victory_sfx.stop()
		play_sfx.play()
	elif gameState == 3:
		# kill all sprites
		all_sprites.empty()
		all_sprites2.empty()		
		collision_sprites.empty()
		collision_sprites2.empty()
		# display winner
		screen.blit(background_surface2, (0, 0))
		if winner == 1:
			text = player1 + " Wins!"
		else:
			text = player2 + " Wins!"
		text_surface = pygame.font.Font(const.font, 74).render(text, True, (0, 0, 0))
		screen.blit(text_surface, (100, 50))
		screen.blit(stars_surface, (560, 200))
		# print score
		score_surface = pygame.font.Font(const.font, 54).render("Score Board", True, (0, 0, 0))
		score1_surface = pygame.font.Font(const.font, 54).render(player1 + " : " + str(score1), True, (0, 0, 0))
		score2_surface = pygame.font.Font(const.font, 54).render(player2 + " : " + str(score2), True, (0, 0, 0))
		screen.blit(score_surface, (100, 200))
		screen.blit(score1_surface, (100, 300))
		screen.blit(score2_surface, (100, 400))
		# print high score
		if score1 > score2:
			if score1 > highScore:
				highScore = score1
				scoreV = True
		else:
			if score2 > highScore:
				highScore = score2
				scoreV = True

		high_score_surface = pygame.font.Font(None, 80).render("Highest Score : " + str(highScore), True, (0, 0, 0))
		screen.blit(high_score_surface, (100, 510))
		if scoreV == True:
			victory_surface = pygame.font.Font(None, 80).render("New High Score!", True, (0, 0, 0))
			screen.blit(victory_surface, (100, 610))

		#restart game
		restart_button = pygame.image.load("./resources/img/restart.png").convert_alpha()
		restart_button = pygame.transform.scale(restart_button, (200, 200))
		screen.blit(restart_button, (900, 500))
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if restart_button.get_rect(topleft=(900, 500)).collidepoint(event.pos):
					gameState = 0
					player1 = ""
					player2 = ""
					score1 = 0
					score2 = 0
					stepCount = 0
					wind = 0
					windr = random.randrange(1,5)
					p=0
					bird1 = 0
					bird2 = 0
					winner = 0
					input = ""
					text = "Enter Player_1 Name "
					tim=0
					stepCount = 0
					scoreV = False

					# clean up the screen
					all_sprites.empty()
					all_sprites2.empty()		
					collision_sprites.empty()
					collision_sprites2.empty()
		victory_sfx.play()
		# pygame.display.update()
		# time.sleep(2)
	elif gameState == -1 or gameState == -2:

		# chose birds
		screen.blit(background_surface, (0, 0))
		if gameState == -1:
			tx = player1 + "  Choose your Bird"
		else:
			tx = player2 + "  Choose your Bird"
		text_surface = pygame.font.Font(None, 74).render(tx, True, (0, 0, 0))
		screen.blit(text_surface, (100, 100))
		screen.blit(RED, (300, 300))
		screen.blit(CHUCK, (500, 300))
		screen.blit(BOMB, (700, 300))
		screen.blit(BLUE, (900, 300))

		#hover effect
		if event.type == pygame.MOUSEMOTION:
			if RED.get_rect(topleft=(300, 300)).collidepoint(event.pos):
				pygame.draw.circle(screen, (255, 0, 0), (300+RED.width//2, 300+RED.width//2), 60, 5)
			if CHUCK.get_rect(topleft=(500, 300)).collidepoint(event.pos):
				pygame.draw.circle(screen, (255, 255, 0), (500+CHUCK.width//2, 300+CHUCK.width//2), 60, 5)
			if BOMB.get_rect(topleft=(700, 300)).collidepoint(event.pos):
				pygame.draw.circle(screen, (0, 0, 0), (700+BOMB.width//2, 330+BOMB.width//2), 60, 5)
			if BLUE.get_rect(topleft=(900, 300)).collidepoint(event.pos):
				pygame.draw.circle(screen, (0, 0, 255), (900+BLUE.width//2, 300+BLUE.width//2), 60, 5)

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if RED.get_rect(topleft=(300, 300)).collidepoint(event.pos):
					if gameState == -1:
						bird1 = const.red
						# wait 1 sec
						time.sleep(0.2)
						gameState = -2
					else:
						bird2 = const.red
						time.sleep(0.2)
						gameState = -3
				elif CHUCK.get_rect(topleft=(500, 300)).collidepoint(event.pos):
					if gameState == -1:
						bird1 = const.chuck
						time.sleep(0.2)
						gameState = -2
					else:
						bird2 = const.chuck
						time.sleep(0.2)
						gameState = -3
				elif BOMB.get_rect(topleft=(700, 300)).collidepoint(event.pos):
					if gameState == -1:
						bird1 = const.bomb
						time.sleep(0.2)
						gameState = -2
					else:
						bird2 = const.bomb
						time.sleep(0.2)
						gameState = -3
				elif BLUE.get_rect(topleft=(900, 300)).collidepoint(event.pos):
					if gameState == -1:
						bird1 = const.blue
						time.sleep(0.2)
						gameState = -2
					else:
						bird2 = const.blue
						time.sleep(0.2)
						gameState = -3
	elif gameState == -3:
		tk = "Chose Level"
		l1 = "Level 1"
		l2 = "Level 2"
		l3 = "Level 3"
		base_font = pygame.font.Font(const.font, 54)
		text_surface = pygame.font.Font(None,94).render(tk, True, (0, 0, 0))
		l1_surface = base_font.render(l1, True, (0, 0, 0))
		l2_surface = base_font.render(l2, True, (0, 0, 0))
		l3_surface = base_font.render(l3, True, (0, 0, 0))
		screen.blit(background_surface, (0, 0))
		screen.blit(text_surface, (100, 100))
		screen.blit(l1_surface, (100, 200))
		screen.blit(l2_surface, (100, 300))
		screen.blit(l3_surface, (100, 400))

		if event.type == pygame.MOUSEMOTION:
			if l1_surface.get_rect(topleft=(100, 200)).collidepoint(event.pos):
				pygame.draw.rect(screen, (0, 0, 255), (90, 200, l1_surface.get_width()+20, l1_surface.get_height()), 5)
			if l2_surface.get_rect(topleft=(100, 300)).collidepoint(event.pos):
				pygame.draw.rect(screen, (0, 0, 255), (90, 300, l2_surface.get_width()+20, l2_surface.get_height()), 5)
			if l3_surface.get_rect(topleft=(100, 400)).collidepoint(event.pos):
				pygame.draw.rect(screen, (0, 0, 255), (90, 400, l3_surface.get_width()+20, l3_surface.get_height()), 5)


		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if l1_surface.get_rect(topleft=(100, 200)).collidepoint(event.pos):
					lev = const.level1
					time.sleep(0.2)
					gameState =-4
				elif l2_surface.get_rect(topleft=(100, 300)).collidepoint(event.pos):
					lev = const.level2
					time.sleep(0.2)
					gameState = -4
				elif l3_surface.get_rect(topleft=(100, 400)).collidepoint(event.pos):
					lev = const.level3
					time.sleep(0.2)
					gameState = -4
	elif gameState == -4:
		# Wind State
		wtx = "Wind State"
		w1 = "Wind Impulse On"
		w2 = "Wind Impulse Off"
		base_font = pygame.font.Font(const.font, 54)
		text_surface = pygame.font.Font(None,94).render(wtx, True, (0, 0, 0))
		w1_surface = base_font.render(w1, True, (0, 0, 0))
		w2_surface = base_font.render(w2, True, (0, 0, 0))
		screen.blit(background_surface, (0, 0))
		screen.blit(text_surface, (100, 100))
		screen.blit(w1_surface, (100, 200))
		screen.blit(w2_surface, (100, 300))
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if w1_surface.get_rect(topleft=(100, 200)).collidepoint(event.pos):
					wind = 1
					time.sleep(0.2)
					gameState = -5
				elif w2_surface.get_rect(topleft=(100, 300)).collidepoint(event.pos):
					wind
					time.sleep(0.2)
					gameState = -5		
		if event.type == pygame.MOUSEMOTION:
			if w1_surface.get_rect(topleft=(100, 200)).collidepoint(event.pos):
				pygame.draw.rect(screen, (0, 0, 255), (90, 200, w1_surface.get_width()+20, w1_surface.get_height()), 5)
			if w2_surface.get_rect(topleft=(100, 300)).collidepoint(event.pos):
				pygame.draw.rect(screen, (0, 0, 255), (90, 300, w2_surface.get_width()+20, w2_surface.get_height()), 5)
			
	elif gameState == -5:
		# clean up the screen
		all_sprites.empty()
		all_sprites2.empty()
		collision_sprites.empty()
		collision_sprites2.empty()
		time.sleep(0.1)
		spriteSetup(lev)
		gameState = 1

	all_sprites.update(dt)
	all_sprites.draw(screen)
	all_sprites2.update(dt)
	all_sprites2.draw(screen)

	for sprite in collision_sprites:
		if isinstance(sprite,StaticObstacle):
			health_surface = pygame.font.Font(None, 30).render(str(sprite.h), True, (255, 0, 0))
			screen.blit(health_surface, (sprite.rect.x + 10, sprite.rect.y + 10))
	for sprite in collision_sprites2:
		if isinstance(sprite,StaticObstacle):
			health_surface = pygame.font.Font(None, 30).render(str(sprite.h), True, (255, 0, 0))
			screen.blit(health_surface, (sprite.rect.x + 10, sprite.rect.y + 10))

	# find winner
	if gameState == 1 or gameState == 2:
		winC=False
		for sprite in collision_sprites:
			if isinstance(sprite,StaticObstacle):
				if sprite.h > 0:
					winC = True

		if winC == False:
			winner = 1
			gameState = 3

		winC=False
		for sprite in collision_sprites2:
			if isinstance(sprite,StaticObstacle):
				if sprite.h > 0:
					winC = True

		if winC == False:
			winner = 2
			gameState = 3


	# display output
	pygame.display.update()
