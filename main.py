
import pygame
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Happy Birthday Johann!")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Load images
def load_image(path, scale=1.0):
    try:
        img = pygame.image.load(path).convert_alpha()
        width = int(img.get_width() * scale)
        height = int(img.get_height() * scale)
        return pygame.transform.scale(img, (width, height))
    except pygame.error:
        print(f"Error loading image: {path}")
        return pygame.Surface((50, 50), pygame.SRCALPHA)

# Assets - scaled down by factor of 1/4 (0.125 instead of 0.5)
player_img = load_image('attached_assets/hero-johann.png', 0.125)
enemy_images = {
    'ariel': load_image('attached_assets/mob-ariel.png', 0.125),
    'tim': load_image('attached_assets/mob-tim.png', 0.125),
    'margaret': load_image('attached_assets/mob-margaret.png', 0.125),
    'john': load_image('attached_assets/mob-john.png', 0.125),
    'kirtik': load_image('attached_assets/mob-kirtik.png', 0.125)
}

# Speech bubble messages
SPEECH_MESSAGES = [
    "New high-priority task assigned!",
    "Design has been updated... again",
    "Can we huddle right now?",
    "Urgent email that needs your attention!",
    "Let's schedule a meeting",
    "Did you see my Slack message?",
    "The client wants changes",
    "Let's talk about your estimates",
    "The deadline was moved up",
    "Just a quick question..."
]

# Effects
lightning_img = pygame.Surface((20, 200), pygame.SRCALPHA)
pygame.draw.line(lightning_img, (255, 255, 255), (10, 0), (10, 200), 4)
missile_img = pygame.Surface((10, 20), pygame.SRCALPHA)
pygame.draw.ellipse(missile_img, (0, 255, 255), (0, 0, 10, 20))
fire_cone_img = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.polygon(fire_cone_img, (255, 100, 0), [(50, 0), (0, 100), (100, 100)])

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.xp = 0
        self.level = 1
        self.xp_to_level = 10
        self.hurt_timer = 0
        
        # Abilities
        self.abilities = {
            'lightning': {'cooldown': 0, 'max_cooldown': 60},
            'missile': {'cooldown': 0, 'max_cooldown': 30},
            'fire_cone': {'cooldown': 0, 'max_cooldown': 90},
            'speed_burst': {'cooldown': 0, 'max_cooldown': 120, 'active': False, 'duration': 0}
        }
        
    def update(self):
        # Movement
        keys = pygame.key.get_pressed()
        speed_modifier = 2 if self.abilities['speed_burst']['active'] else 1
        
        if keys[K_w]:
            self.rect.y -= self.speed * speed_modifier
        if keys[K_s]:
            self.rect.y += self.speed * speed_modifier
        if keys[K_a]:
            self.rect.x -= self.speed * speed_modifier
        if keys[K_d]:
            self.rect.x += self.speed * speed_modifier
            
        # World boundaries (larger than screen)
        WORLD_WIDTH = SCREEN_WIDTH * 3
        WORLD_HEIGHT = SCREEN_HEIGHT * 3
        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, WORLD_HEIGHT - self.rect.height))
        
        # Cooldown timers
        for ability in self.abilities:
            if self.abilities[ability]['cooldown'] > 0:
                self.abilities[ability]['cooldown'] -= 1
                
        # Speed burst duration
        if self.abilities['speed_burst']['active']:
            self.abilities['speed_burst']['duration'] -= 1
            if self.abilities['speed_burst']['duration'] <= 0:
                self.abilities['speed_burst']['active'] = False
                
        # Hurt timer
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            
    def use_ability(self, ability_name, projectiles_group, all_sprites):
        if ability_name == 'lightning' and self.abilities['lightning']['cooldown'] == 0:
            # Lightning ability
            self.abilities['lightning']['cooldown'] = self.abilities['lightning']['max_cooldown']
            lightning = Projectile(self.rect.centerx, self.rect.centery, 'lightning', 0, -10)
            projectiles_group.add(lightning)
            all_sprites.add(lightning)
            
        elif ability_name == 'missile' and self.abilities['missile']['cooldown'] == 0:
            # Magic missile ability
            self.abilities['missile']['cooldown'] = self.abilities['missile']['max_cooldown']
            # Create 3 missiles in a spread pattern
            for angle in [-10, 0, 10]:
                dx = math.sin(math.radians(angle)) * 8
                dy = -math.cos(math.radians(angle)) * 8
                missile = Projectile(self.rect.centerx, self.rect.centery, 'missile', dx, dy)
                projectiles_group.add(missile)
                all_sprites.add(missile)
                
        elif ability_name == 'fire_cone' and self.abilities['fire_cone']['cooldown'] == 0:
            # Fire cone ability
            self.abilities['fire_cone']['cooldown'] = self.abilities['fire_cone']['max_cooldown']
            fire_cone = Projectile(self.rect.centerx, self.rect.centery, 'fire_cone', 0, 0, is_area_effect=True)
            projectiles_group.add(fire_cone)
            all_sprites.add(fire_cone)
            
        elif ability_name == 'speed_burst' and self.abilities['speed_burst']['cooldown'] == 0:
            # Speed burst ability
            self.abilities['speed_burst']['cooldown'] = self.abilities['speed_burst']['max_cooldown']
            self.abilities['speed_burst']['active'] = True
            self.abilities['speed_burst']['duration'] = 120  # 2 seconds at 60 FPS
            
    def take_damage(self, amount):
        if self.hurt_timer == 0:
            self.health -= amount
            self.hurt_timer = 30  # Invincibility frames
            
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.xp = 0
        self.xp_to_level = 10 * self.level
        self.health = self.max_health  # Refill health on level up
        
# Camera class
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
        
    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        
        # Limit scrolling to game area
        x = min(0, x)  # left
        y = min(0, y)  # top
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = enemy_images.get(enemy_type, pygame.Surface((50, 50)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = random.uniform(1.0, 2.5)
        self.health = 30
        self.hurt_timer = 0
        self.target = None
        
        # Speech bubble
        self.speech_message = random.choice(SPEECH_MESSAGES)
        self.show_speech = False
        self.speech_timer = 0
        self.speech_duration = 180  # 3 seconds at 60 FPS
        
    def update(self):
        if self.target:
            # Move towards player
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            dx, dy = dx / dist, dy / dist
            
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            
            # Show speech bubble when close to player
            if dist < 200 and not self.show_speech and random.random() < 0.02:
                self.show_speech = True
                self.speech_timer = self.speech_duration
                # Randomly select a new message
                self.speech_message = random.choice(SPEECH_MESSAGES)
            
        # Speech bubble timer
        if self.speech_timer > 0:
            self.speech_timer -= 1
            if self.speech_timer <= 0:
                self.show_speech = False
            
        # Hurt timer
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            
    def take_damage(self, amount):
        if self.hurt_timer == 0:
            self.health -= amount
            self.hurt_timer = 10
            
    def draw_speech_bubble(self, surface, camera):
        if self.show_speech:
            # Get position adjusted for camera
            pos = camera.apply(self)
            
            # Create font
            font = pygame.font.SysFont(None, 18)
            
            # Render text
            text_surface = font.render(self.speech_message, True, BLACK)
            text_rect = text_surface.get_rect()
            
            # Create bubble
            bubble_width = text_rect.width + 10
            bubble_height = text_rect.height + 10
            bubble_rect = pygame.Rect(
                pos.centerx - bubble_width // 2,
                pos.top - bubble_height - 5,
                bubble_width,
                bubble_height
            )
            
            # Draw bubble
            pygame.draw.rect(surface, WHITE, bubble_rect, border_radius=5)
            pygame.draw.rect(surface, BLACK, bubble_rect, 1, border_radius=5)
            
            # Draw triangle pointer
            pygame.draw.polygon(surface, WHITE, [
                (pos.centerx - 5, bubble_rect.bottom),
                (pos.centerx + 5, bubble_rect.bottom),
                (pos.centerx, bubble_rect.bottom + 5)
            ])
            
            # Position text inside bubble
            text_rect.center = bubble_rect.center
            
            # Draw text
            surface.blit(text_surface, text_rect)
        
# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, proj_type, dx=0, dy=0, is_area_effect=False):
        super().__init__()
        self.proj_type = proj_type
        self.dx = dx
        self.dy = dy
        self.is_area_effect = is_area_effect
        self.lifetime = 60 if is_area_effect else 120  # 1-2 seconds at 60 FPS
        
        if proj_type == 'lightning':
            self.image = lightning_img
            self.damage = 20
        elif proj_type == 'missile':
            self.image = missile_img
            self.damage = 10
        elif proj_type == 'fire_cone':
            self.image = fire_cone_img
            self.damage = 5
        else:
            self.image = pygame.Surface((10, 10))
            self.image.fill(RED)
            self.damage = 5
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def update(self):
        if not self.is_area_effect:
            self.rect.x += self.dx
            self.rect.y += self.dy
            
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            
# XP Orb class
class XPOrb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pulse_counter = 0
        
    def update(self):
        # Pulsing effect
        self.pulse_counter = (self.pulse_counter + 1) % 60
        scale = 1.0 + 0.2 * math.sin(self.pulse_counter * math.pi / 30)
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        radius = int(5 * scale)
        pygame.draw.circle(self.image, BLUE, (5, 5), radius)
            
# Game functions
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)
    
def draw_bar(surface, x, y, value, max_value, bar_width, bar_height, color, bg_color=BLACK):
    # Background
    pygame.draw.rect(surface, bg_color, (x, y, bar_width, bar_height))
    # Fill
    fill_width = int((value / max_value) * bar_width)
    fill_rect = pygame.Rect(x, y, fill_width, bar_height)
    pygame.draw.rect(surface, color, fill_rect)
    # Border
    pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)
    
def draw_ability_cooldowns(surface, player):
    # Draw ability cooldown indicators
    for i, ability in enumerate(player.abilities):
        max_cd = player.abilities[ability]['max_cooldown']
        current_cd = player.abilities[ability]['cooldown']
        
        # Set colors and position
        if ability == 'lightning':
            key = 'J'
            color = YELLOW
            x = 600
        elif ability == 'missile':
            key = 'K'
            color = BLUE
            x = 650
        elif ability == 'fire_cone':
            key = 'L'
            color = ORANGE
            x = 700
        elif ability == 'speed_burst':
            key = 'I'
            color = GREEN
            x = 550
            
        # Draw ability box
        pygame.draw.rect(surface, WHITE, (x, 20, 40, 40), 2)
        
        # Draw cooldown overlay
        if current_cd > 0:
            cd_height = int((current_cd / max_cd) * 40)
            pygame.draw.rect(surface, (100, 100, 100, 128), (x, 20, 40, cd_height))
            
        # Draw key label
        draw_text(surface, key, 20, x + 20, 25, color)
        
def spawn_enemy(player_pos, enemies_group, all_sprites, wave_num):
    # Define the size of the world
    WORLD_WIDTH = SCREEN_WIDTH * 3
    WORLD_HEIGHT = SCREEN_HEIGHT * 3
    
    # Calculate visible area based on player position
    min_x = max(0, player_pos.rect.centerx - SCREEN_WIDTH)
    max_x = min(WORLD_WIDTH, player_pos.rect.centerx + SCREEN_WIDTH)
    min_y = max(0, player_pos.rect.centery - SCREEN_HEIGHT)
    max_y = min(WORLD_HEIGHT, player_pos.rect.centery + SCREEN_HEIGHT)
    
    # Choose spawn position outside visible area but inside world boundaries
    side = random.randint(0, 3)
    if side == 0:  # Top
        x = random.randint(min_x, max_x)
        y = max(0, min_y - 100)
    elif side == 1:  # Right
        x = min(WORLD_WIDTH, max_x + 100)
        y = random.randint(min_y, max_y)
    elif side == 2:  # Bottom
        x = random.randint(min_x, max_x)
        y = min(WORLD_HEIGHT, max_y + 100)
    else:  # Left
        x = max(0, min_x - 100)
        y = random.randint(min_y, max_y)
        
    # Choose enemy type based on wave number
    enemy_types = ['ariel', 'tim', 'margaret', 'john', 'kirtik']
    
    if wave_num < 5:
        # Early waves have basic enemies
        enemy_type = random.choice(enemy_types[:2])
    else:
        # Later waves have all enemy types
        enemy_type = random.choice(enemy_types)
        
    enemy = Enemy(x, y, enemy_type)
    enemy.target = player_pos
    enemies_group.add(enemy)
    all_sprites.add(enemy)
    
def show_game_over(surface, player_level):
    surface.fill(BLACK)
    draw_text(surface, f"Happiest of birthdays, Johann!", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, WHITE)
    draw_text(surface, f"Thank you for being a great developer!", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
    draw_text(surface, f"You reached level {player_level}!", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, WHITE)
    draw_text(surface, "Press R to restart", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4, WHITE)
    
    # Confetti animation
    for _ in range(20):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT // 2)
        size = random.randint(5, 15)
        color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE])
        pygame.draw.rect(surface, color, (x, y, size, size))
        
# Main game function
def game():
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    xp_orbs = pygame.sprite.Group()
    
    # Create player
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    all_sprites.add(player)
    
    # Create camera
    camera = Camera(SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3)  # Create a larger world
    
    # Game variables
    running = True
    game_over = False
    score = 0
    wave_number = 1
    wave_size = 5
    spawn_timer = 0
    spawn_delay = 60  # 1 second at 60 FPS
    
    # Define the size of the world
    WORLD_WIDTH = SCREEN_WIDTH * 3
    WORLD_HEIGHT = SCREEN_HEIGHT * 3
    
    # Tile size (smaller tiles)
    TILE_SIZE = 20  # Reduced from 50
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            # Key presses
            if event.type == KEYDOWN:
                if game_over and event.key == K_r:
                    return  # Restart game
                    
                # Ability keys
                if not game_over:
                    if event.key == K_j:
                        player.use_ability('lightning', projectiles, all_sprites)
                    elif event.key == K_k:
                        player.use_ability('missile', projectiles, all_sprites)
                    elif event.key == K_l:
                        player.use_ability('fire_cone', projectiles, all_sprites)
                    elif event.key == K_i:
                        player.use_ability('speed_burst', projectiles, all_sprites)
                        
        if not game_over:
            # Update
            all_sprites.update()
            
            # Update camera to follow player
            camera.update(player)
            
            # Spawn enemies
            if len(enemies) < wave_size and spawn_timer <= 0:
                spawn_enemy(player, enemies, all_sprites, wave_number)
                spawn_timer = spawn_delay
            spawn_timer -= 1
            
            # Check if wave is complete
            if len(enemies) == 0 and spawn_timer <= 0:
                wave_number += 1
                wave_size = 5 + wave_number
                spawn_delay = max(30, 60 - wave_number * 2)  # Spawn faster as waves progress
                
            # Collisions - Projectiles hit enemies
            for proj in projectiles:
                # Area effect projectiles
                if proj.is_area_effect:
                    for enemy in enemies:
                        # Check if enemy is within area effect (fire cone)
                        distance = math.sqrt((enemy.rect.centerx - proj.rect.centerx)**2 + 
                                           (enemy.rect.centery - proj.rect.centery)**2)
                        if distance < 100:  # Fire cone radius
                            enemy.take_damage(proj.damage)
                            
                # Direct hit projectiles
                else:
                    hits = pygame.sprite.spritecollide(proj, enemies, False)
                    for enemy in hits:
                        enemy.take_damage(proj.damage)
                        if not proj.is_area_effect:
                            proj.kill()
                            break
                            
            # Kill enemies with no health and spawn XP orbs
            for enemy in enemies:
                if enemy.health <= 0:
                    # Spawn XP orb
                    orb = XPOrb(enemy.rect.centerx, enemy.rect.centery)
                    xp_orbs.add(orb)
                    all_sprites.add(orb)
                    # Add to score
                    score += 10
                    # Remove enemy
                    enemy.kill()
                    
            # Player collects XP orbs
            orb_hits = pygame.sprite.spritecollide(player, xp_orbs, True)
            for orb in orb_hits:
                player.gain_xp(1)
                
            # Enemies damage player
            if player.hurt_timer == 0:
                hits = pygame.sprite.spritecollide(player, enemies, False)
                if hits:
                    player.take_damage(10)
                    
            # Check if player is dead
            if player.health <= 0:
                game_over = True
            
        # Draw
        DISPLAYSURF.fill(BLACK)
        
        # Draw background (office tile) - smaller tiles and based on camera
        # Calculate visible area based on camera position
        cam_x, cam_y = camera.camera.topleft
        start_x = max(0, -cam_x // TILE_SIZE)
        start_y = max(0, -cam_y // TILE_SIZE)
        end_x = min(WORLD_WIDTH // TILE_SIZE, (-cam_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        end_y = min(WORLD_HEIGHT // TILE_SIZE, (-cam_y + SCREEN_HEIGHT) // TILE_SIZE + 1)
        
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                # Draw tile with camera offset
                rect = pygame.Rect(
                    x * TILE_SIZE + cam_x,
                    y * TILE_SIZE + cam_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(DISPLAYSURF, (50, 50, 50), rect, 1)
                
        # Draw all sprites with camera applied
        for sprite in all_sprites:
            DISPLAYSURF.blit(sprite.image, camera.apply(sprite))
            
        # Draw speech bubbles for enemies
        for enemy in enemies:
            enemy.draw_speech_bubble(DISPLAYSURF, camera)
        
        # Draw UI
        if not game_over:
            # Health bar
            draw_bar(DISPLAYSURF, 10, 10, player.health, player.max_health, 200, 20, RED)
            draw_text(DISPLAYSURF, f"HP: {player.health}/{player.max_health}", 20, 110, 10, WHITE)
            
            # XP bar
            draw_bar(DISPLAYSURF, 10, 40, player.xp, player.xp_to_level, 200, 20, BLUE)
            draw_text(DISPLAYSURF, f"Level {player.level} - XP: {player.xp}/{player.xp_to_level}", 20, 110, 40, WHITE)
            
            # Score
            draw_text(DISPLAYSURF, f"Score: {score}", 24, SCREEN_WIDTH - 100, 10, WHITE)
            
            # Wave number
            draw_text(DISPLAYSURF, f"Wave: {wave_number}", 24, SCREEN_WIDTH - 100, 40, WHITE)
            
            # Ability cooldowns
            draw_ability_cooldowns(DISPLAYSURF, player)
            
            # Hurt effect
            if player.hurt_timer > 0 and player.hurt_timer % 6 < 3:
                hurt_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                hurt_surf.fill((255, 0, 0, 100))
                DISPLAYSURF.blit(hurt_surf, (0, 0))
        else:
            show_game_over(DISPLAYSURF, player.level)
            
        pygame.display.update()
        clock.tick(FPS)
        
# Main loop
def main():
    while True:
        game()  # Start a new game
        
if __name__ == '__main__':
    main()
