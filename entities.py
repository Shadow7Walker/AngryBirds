import pygame
import math
import const
import utils
import state

class StaticObstacle(pygame.sprite.Sprite):
    def __init__(self, pos, obstacle_type, groups):
        super().__init__(groups)
        self.type = obstacle_type
        self.h = 100
        # Fix bug: Use self.h // 21 (which is 4 at full health) to match bounds of self.type lists (len 5)
        self.image = utils.load_cached_image(self.type[self.h // 21])
        self.rect = self.image.get_rect(center=pos)

    # update sprite image based on health
    def update(self, dt):
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
            self.image = utils.load_cached_image(self.type[self.h // 21])
        else:
            self.kill()


class Ball(pygame.sprite.Sprite):
    def __init__(self, position, groups, obstacles, bird_type, gameState):
        super().__init__(groups)
        self.type = bird_type
        self.position = position
        if gameState == 1:
            self.image = utils.load_cached_image(self.type, False)
        else: # flip the image for player 2
            self.image = utils.load_cached_image(self.type, True)
            
        self.rect = self.image.get_rect(center=self.position)
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
            self.colour = (255, 0, 0)
        elif self.type == const.chuck:
            self.colour = (255, 255, 0)
        elif self.type == const.bomb:
            self.colour = (0, 0, 0)
        elif self.type == const.blue:
            self.colour = (0, 0, 255)

    def collision(self, direction):
        collision_sprites = pygame.sprite.spritecollide(self, self.obstacles, False)
        
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
        scr = 0
        for sprite in collision_sprites:
            if isinstance(sprite, StaticObstacle):
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
                    state.score1 += scr
                elif self.gmState == 2:
                    state.score2 += scr

                if sprite.h <= 0:
                    sprite.kill()

    def window_collision(self, direction):
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

    def update(self, dt):
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

            if state.wind == 1:
                if state.windr == 1:
                    self.velX += 150 * dt
                    self.velY += 150 * dt
                elif state.windr == 2:
                    self.velX -= 150 * dt
                    self.velY += 150 * dt
                elif state.windr == 3:
                    self.velX += 150 * dt
                    self.velY -= 150 * dt
                elif state.windr == 4:
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
            
            # If ball is rolling very slowly on ground, start the low speed timer
            if on_ground and speed < 15:
                self.low_speed_timer += dt
            else:
                self.low_speed_timer = 0.0
                
            self.flight_time += dt
            
            # Kill ball if it gets stuck, rolls too long, or stays at very low speed
            if self.flight_time > 8.0 or self.low_speed_timer > 1.5:
                print("Ball killed due to flight timeout")
                self.kill_and_next_turn()
                
        # Handle aiming mechanics (Grabbing and Pulling with distance clamping)
        if self.state == 0 and self.gmState == state.gameState and not state.wait_for_mouse_release:
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
						# Keep the same angle, just scale down the magnitude
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
                        if self.type in state.sounds:
                            state.sounds[self.type].play()
                    else:
                        # Reset to slingshot center if pull was too small
                        self.rect.center = self.position
                        self.pos = pygame.math.Vector2(self.rect.center)
                        self.velX = 0
                        self.velY = 0
                    self.grabbed = False

        # if ball is out of the screen bounds, kill the ball and trigger next turn
        if self.rect.left > 1280 or self.rect.right < 0:
            print("Ball killed due to out of screen bounds")
            self.kill_and_next_turn()

    def kill_and_next_turn(self):
        self.kill()
        if self.gmState == 1:
            state.gameState = 2
            if state.step_callback:
                state.step_callback(state.gameState)
        elif self.gmState == 2:
            state.gameState = 1
            if state.step_callback:
                state.step_callback(state.gameState)
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
            if state.wind == 1:
                if state.windr == 1:
                    temp_vel.x += 150 * sim_dt
                    temp_vel.y += 150 * sim_dt
                elif state.windr == 2:
                    temp_vel.x -= 150 * sim_dt
                    temp_vel.y += 150 * sim_dt
                elif state.windr == 3:
                    temp_vel.x += 150 * sim_dt
                    temp_vel.y -= 150 * sim_dt
                elif state.windr == 4:
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
                pygame.draw.circle(state.screen, self.colour, pt, 4)
