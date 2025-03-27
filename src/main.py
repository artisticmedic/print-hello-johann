import pygame
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Johann's Office Survival")

# Game constants
TILE_SIZE = 40
MAP_WIDTH = 20  # in tiles
MAP_HEIGHT = 20  # in tiles
CAMERA_SPEED = 0.1

# Load assets
try:
    hero_img = pygame.image.load("assets/sprites/hero-johann.png").convert_alpha()
    mob_ariel_img = pygame.image.load("assets/sprites/mob-ariel.png").convert_alpha()
    mob_john_img = pygame.image.load("assets/sprites/mob-john.png").convert_alpha()
    mob_kirtik_img = pygame.image.load("assets/sprites/mob-kirtik.png").convert_alpha()
    mob_margaret_img = pygame.image.load("assets/sprites/mob-margaret.png").convert_alpha()
    mob_tim_img = pygame.image.load("assets/sprites/mob-tim.png").convert_alpha()
    lightning_img = pygame.image.load("assets/sprites/lightning-sprite.png").convert_alpha()
    magic_missile_img = pygame.image.load("assets/sprites/magic-missile-sprite.png").convert_alpha()
    fire_cone_img = pygame.image.load("assets/sprites/fire-cone-sprite.png").convert_alpha()
    cake_img = pygame.Surface((20, 20))  # Placeholder for cake sprite
    cake_img.fill((255, 192, 203))  # Pink color for now
except pygame.error:
    print("Warning: Unable to load one or more images. Using placeholder graphics.")
    # Create placeholder graphics
    hero_img = pygame.Surface((32, 32))
    hero_img.fill((0, 0, 255))
    mob_ariel_img = pygame.Surface((32, 32))
    mob_ariel_img.fill((255, 0, 0))
    mob_john_img = pygame.Surface((32, 32))
    mob_john_img.fill((255, 0, 0))
    mob_kirtik_img = pygame.Surface((32, 32))
    mob_kirtik_img.fill((255, 0, 0))
    mob_margaret_img = pygame.Surface((32, 32))
    mob_margaret_img.fill((255, 0, 0))
    mob_tim_img = pygame.Surface((32, 32))
    mob_tim_img.fill((255, 0, 0))
    lightning_img = pygame.Surface((50, 10))
    lightning_img.fill((255, 255, 0))
    magic_missile_img = pygame.Surface((10, 10))
    magic_missile_img.fill((0, 255, 255))
    fire_cone_img = pygame.Surface((50, 50))
    fire_cone_img.fill((255, 165, 0))
    cake_img = pygame.Surface((20, 20))
    cake_img.fill((255, 192, 203))

# Resize character sprites to match tile size
hero_img = pygame.transform.scale(hero_img, (TILE_SIZE, TILE_SIZE))
mob_ariel_img = pygame.transform.scale(mob_ariel_img, (TILE_SIZE, TILE_SIZE))
mob_john_img = pygame.transform.scale(mob_john_img, (TILE_SIZE, TILE_SIZE))
mob_kirtik_img = pygame.transform.scale(mob_kirtik_img, (TILE_SIZE, TILE_SIZE))
mob_margaret_img = pygame.transform.scale(mob_margaret_img, (TILE_SIZE, TILE_SIZE))
mob_tim_img = pygame.transform.scale(mob_tim_img, (TILE_SIZE, TILE_SIZE))

# Resize ability sprites to specified dimensions
# Lightning should be as long as 6 tiles
lightning_img = pygame.transform.scale(lightning_img, (TILE_SIZE, 6 * TILE_SIZE))
# Magic missile should be only one tile large
magic_missile_img = pygame.transform.scale(magic_missile_img, (TILE_SIZE, TILE_SIZE))
# Fire cone should be the width of roughly 5 tiles
fire_cone_img = pygame.transform.scale(fire_cone_img, (5 * TILE_SIZE, 5 * TILE_SIZE))

# Rotate lightning sprite 90 degrees
lightning_img = pygame.transform.rotate(lightning_img, 90)

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create birthday cake sprite (replacing XP orbs)
def create_cake_sprite():
    cake = pygame.Surface((10, 10), pygame.SRCALPHA)  # Smaller cake sprite
    # Base of cake (brown)
    pygame.draw.rect(cake, (139, 69, 19), (1, 5, 8, 5))
    # Frosting (white)
    pygame.draw.rect(cake, (255, 255, 255), (0, 2, 10, 3))
    # Candle (red)
    pygame.draw.rect(cake, (255, 0, 0), (4, 0, 2, 2))
    # Flame (yellow)
    pygame.draw.circle(cake, (255, 255, 0), (5, 0), 1)
    return cake

# Create birthday cake sprite
cake_img = create_cake_sprite()

# Interruption messages for speech bubbles
INTERRUPTION_MESSAGES = [
    "New high-priority task!",
    "Design has been updated...again",
    "Can we huddle right now?",
    "Urgent email!",
    "Quick question?",
    "Got a minute?",
    "Need your input!",
    "Let's sync up!",
    "Call just ended, need update",
    "Client wants changes"
]

# Classes
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = hero_img.get_width()
        self.height = hero_img.get_height()
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.xp = 0
        self.level = 1
        self.xp_to_level = 10
        self.abilities = {
            "lightning": {"cooldown": 0, "max_cooldown": 30},
            "magic_missile": {"cooldown": 0, "max_cooldown": 15},
            "fire_cone": {"cooldown": 0, "max_cooldown": 45},
            "speed_burst": {"cooldown": 0, "max_cooldown": 60, "active": False, "duration": 0, "max_duration": 30}
        }
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dx, dy):
        speed_multiplier = 2 if self.abilities["speed_burst"]["active"] else 1
        self.x += dx * self.speed * speed_multiplier
        self.y += dy * self.speed * speed_multiplier

        # Keep player within map bounds
        self.x = max(0, min(self.x, MAP_WIDTH * TILE_SIZE - self.width))
        self.y = max(0, min(self.y, MAP_HEIGHT * TILE_SIZE - self.height))

        self.rect.x = self.x
        self.rect.y = self.y

    def use_ability(self, ability_name, enemies, projectiles):
        ability = self.abilities[ability_name]
        if ability["cooldown"] <= 0:
            ability["cooldown"] = ability["max_cooldown"]

            if ability_name == "lightning":
                projectiles.append(Lightning(self.x + self.width // 2, self.y + self.height // 2))

            elif ability_name == "magic_missile":
                # Find closest enemy for homing
                closest_enemy = None
                min_distance = float('inf')

                for enemy in enemies:
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    distance = math.sqrt(dx*dx + dy*dy)

                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy

                if closest_enemy:
                    projectiles.append(MagicMissile(
                        self.x + self.width // 2, 
                        self.y + self.height // 2,
                        closest_enemy  # Pass target enemy for homing
                    ))

            elif ability_name == "fire_cone":
                projectiles.append(FireCone(self.x + self.width // 2, self.y + self.height // 2))

            elif ability_name == "speed_burst":
                ability["active"] = True
                ability["duration"] = ability["max_duration"]

    def update(self):
        # Update ability cooldowns
        for ability in self.abilities.values():
            if ability["cooldown"] > 0:
                ability["cooldown"] -= 1

        # Update speed burst duration
        if self.abilities["speed_burst"]["active"]:
            self.abilities["speed_burst"]["duration"] -= 1
            if self.abilities["speed_burst"]["duration"] <= 0:
                self.abilities["speed_burst"]["active"] = False

    def draw(self, window, camera_x, camera_y):
        window.blit(hero_img, (self.x - camera_x, self.y - camera_y))

        # Draw health bar
        pygame.draw.rect(window, RED, (self.x - camera_x, self.y - camera_y - 10, self.width, 5))
        pygame.draw.rect(window, GREEN, (self.x - camera_x, self.y - camera_y - 10, self.width * (self.health / self.max_health), 5))

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp = 0
        self.xp_to_level = 10 * self.level
        self.health = self.max_health  # Refill health on level up

class Enemy:
    def __init__(self, x, y, type_id):
        self.x = x
        self.y = y
        self.type_id = type_id
        self.speed = 2
        self.health = 30
        self.cooldown = 0
        self.message = random.choice(INTERRUPTION_MESSAGES)
        self.message_timer = random.randint(100, 200)  # Random timer for speech bubble
        self.show_message = False

        # Select sprite based on enemy type
        if type_id == 0:
            self.img = mob_ariel_img
        elif type_id == 1:
            self.img = mob_john_img
        elif type_id == 2:
            self.img = mob_kirtik_img
        elif type_id == 3:
            self.img = mob_margaret_img
        else:
            self.img = mob_tim_img

        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move_towards_player(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist != 0:
            dx = dx / dist
            dy = dy / dist

            self.x += dx * self.speed
            self.y += dy * self.speed

            self.rect.x = self.x
            self.rect.y = self.y

    def update(self, player):
        self.move_towards_player(player)

        # Update message timer
        self.message_timer -= 1
        if self.message_timer <= 0:
            self.show_message = True
            if self.message_timer <= -50:  # Show message for 50 frames
                self.show_message = False
                self.message = random.choice(INTERRUPTION_MESSAGES)
                self.message_timer = random.randint(100, 200)

    def draw(self, window, camera_x, camera_y):
        window.blit(self.img, (self.x - camera_x, self.y - camera_y))

        # Draw health bar
        pygame.draw.rect(window, RED, (self.x - camera_x, self.y - camera_y - 10, self.width, 5))
        pygame.draw.rect(window, GREEN, (self.x - camera_x, self.y - camera_y - 10, self.width * (self.health / 30), 5))

        # Draw speech bubble with message
        if self.show_message:
            font = pygame.font.SysFont(None, 16)
            text = font.render(self.message, True, BLACK)

            # Speech bubble background
            bubble_width = text.get_width() + 10
            bubble_height = text.get_height() + 10
            bubble_x = self.x - camera_x - bubble_width // 2 + self.width // 2
            bubble_y = self.y - camera_y - 30

            pygame.draw.rect(window, WHITE, (bubble_x, bubble_y, bubble_width, bubble_height))
            pygame.draw.rect(window, BLACK, (bubble_x, bubble_y, bubble_width, bubble_height), 1)

            # Triangle pointer
            pygame.draw.polygon(window, WHITE, [
                (self.x - camera_x + self.width // 2, self.y - camera_y - 5),
                (self.x - camera_x + self.width // 2 - 5, bubble_y + bubble_height),
                (self.x - camera_x + self.width // 2 + 5, bubble_y + bubble_height)
            ])

            # Text
            window.blit(text, (bubble_x + 5, bubble_y + 5))

class Lightning:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = lightning_img.get_width()
        self.height = lightning_img.get_height()
        self.lifetime = 10
        self.damage = 20
        self.rect = pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

    def update(self):
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, window, camera_x, camera_y):
        window.blit(lightning_img, (self.x - self.width // 2 - camera_x, self.y - camera_y))

class MagicMissile:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target  # Target enemy for homing
        self.speed = 6
        self.width = magic_missile_img.get_width()
        self.height = magic_missile_img.get_height()
        self.lifetime = 120
        self.damage = 15
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    def update(self):
        # Home in on target
        if self.target and self.target.health > 0:
            dx = self.target.x + self.target.width // 2 - self.x
            dy = self.target.y + self.target.height // 2 - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > 0:
                dx = dx / dist
                dy = dy / dist

                self.x += dx * self.speed
                self.y += dy * self.speed

        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2

        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, window, camera_x, camera_y):
        window.blit(magic_missile_img, (self.x - self.width // 2 - camera_x, self.y - self.height // 2 - camera_y))

class FireCone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = fire_cone_img.get_width()
        self.height = fire_cone_img.get_height()
        self.lifetime = 180  # 3 seconds at 60 FPS
        self.damage = 10
        self.rect = pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

    def update(self):
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, window, camera_x, camera_y):
        window.blit(fire_cone_img, (self.x - self.width // 2 - camera_x, self.y - camera_y))

class Cake:  # Renamed from XPOrb to Cake
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = cake_img.get_width()
        self.height = cake_img.get_height()
        self.value = 1
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.pulse = 0
        self.growing = True

    def update(self):
        # Pulsing effect
        if self.growing:
            self.pulse += 0.05
            if self.pulse >= 1:
                self.growing = False
        else:
            self.pulse -= 0.05
            if self.pulse <= 0:
                self.growing = True

    def draw(self, window, camera_x, camera_y):
        # Apply pulsing effect
        pulse_scale = 1 + 0.2 * self.pulse
        pulsed_img = pygame.transform.scale(
            cake_img, 
            (int(self.width * pulse_scale), int(self.height * pulse_scale))
        )
        window.blit(
            pulsed_img, 
            (
                self.x - camera_x - (pulsed_img.get_width() - self.width) // 2, 
                self.y - camera_y - (pulsed_img.get_height() - self.height) // 2
            )
        )

# Game functions
def spawn_enemy(player):
    # Choose random position outside of screen but within map
    side = random.randint(0, 3)
    if side == 0:  # Top
        x = random.randint(0, MAP_WIDTH * TILE_SIZE)
        y = 0
    elif side == 1:  # Right
        x = MAP_WIDTH * TILE_SIZE
        y = random.randint(0, MAP_HEIGHT * TILE_SIZE)
    elif side == 2:  # Bottom
        x = random.randint(0, MAP_WIDTH * TILE_SIZE)
        y = MAP_HEIGHT * TILE_SIZE
    else:  # Left
        x = 0
        y = random.randint(0, MAP_HEIGHT * TILE_SIZE)

    enemy_type = random.randint(0, 4)
    return Enemy(x, y, enemy_type)

def main():
    # Game setup
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2, HEIGHT // 2)
    enemies = []
    projectiles = []
    cakes = []  # Renamed from xp_orbs to cakes
    spawn_timer = 0
    camera_x, camera_y = 0, 0
    game_over = False
    game_over_start_time = 0

    # Create office tile grid
    office_tiles = []
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            # Create floor tiles (placeholder, could be replaced with actual sprites)
            tile_type = random.randint(0, 2)  # 0: Empty, 1: Desk, 2: Chair
            if tile_type > 0:
                office_tiles.append((x * TILE_SIZE, y * TILE_SIZE, tile_type))

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                # Only handle ability inputs if not game over
                if not game_over:
                    if event.key == K_j:
                        player.use_ability("lightning", enemies, projectiles)
                    elif event.key == K_k:
                        player.use_ability("magic_missile", enemies, projectiles)
                    elif event.key == K_l:
                        player.use_ability("fire_cone", enemies, projectiles)
                    elif event.key == K_i:
                        player.use_ability("speed_burst", enemies, projectiles)
                # Restart on R key if game over
                elif event.key == K_r:
                    main()  # Restart game
                    return

        if game_over:
            # Display game over screen
            window.fill(BLACK)
            
            # Calculate hero position and fade effect
            current_time = pygame.time.get_ticks()
            fall_distance = min(150, current_time - game_over_start_time) / 1.5
            fall_alpha = max(0, 255 - fall_distance)
            
            # Create a fading hero sprite
            falling_hero = hero_img.copy()
            falling_hero.set_alpha(int(fall_alpha))
            
            # Center message
            font = pygame.font.SysFont(None, 48)
            message = "Happiest of birthdays, Johann!"
            message_text = font.render(message, True, WHITE)
            message_y = HEIGHT//2 - 40
            
            # Create skull sprite above the message
            skull_size = 80
            skull = pygame.Surface((skull_size, skull_size), pygame.SRCALPHA)
            
            # Draw skull - white circle for head
            pygame.draw.circle(skull, WHITE, (skull_size//2, skull_size//2), skull_size//2)
            
            # Draw eye sockets - black circles
            eye_radius = skull_size//6
            pygame.draw.circle(skull, BLACK, (skull_size//3, skull_size//3), eye_radius)
            pygame.draw.circle(skull, BLACK, (2*skull_size//3, skull_size//3), eye_radius)
            
            # Draw nose - triangle
            nose_points = [(skull_size//2, skull_size//2), 
                          (skull_size//2 - skull_size//8, 2*skull_size//3),
                          (skull_size//2 + skull_size//8, 2*skull_size//3)]
            pygame.draw.polygon(skull, BLACK, nose_points)
            
            # Draw mouth - curved line
            for i in range(5):
                x_offset = (i - 2) * (skull_size//6)
                y_pos = 3*skull_size//4 + abs(x_offset)//2
                pygame.draw.circle(skull, BLACK, (skull_size//2 + x_offset, y_pos), skull_size//20)
            
            # Display skull above the message
            skull_y = message_y - skull_size - 20
            window.blit(skull, (WIDTH//2 - skull_size//2, skull_y))
            
            # Draw message
            window.blit(message_text, (WIDTH//2 - message_text.get_width()//2, message_y))
            
            # Draw falling hero just below the message
            window.blit(falling_hero, (WIDTH//2 - falling_hero.get_width()//2, message_y + message_text.get_height() + 20 + fall_distance))
            
            # Draw additional text
            font = pygame.font.SysFont(None, 36)
            text = font.render("Better luck next time!", True, WHITE)
            window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 80))
            
            font = pygame.font.SysFont(None, 24)
            text = font.render("Press R to restart", True, WHITE)
            window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 40))
            
            pygame.display.update()
            clock.tick(60)
            continue

        # Movement input
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[K_w]:
            dy = -1
        if keys[K_s]:
            dy = 1
        if keys[K_a]:
            dx = -1
        if keys[K_d]:
            dx = 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071

        player.move(dx, dy)

        # Update camera position to follow player smoothly
        target_camera_x = player.x - WIDTH // 2
        target_camera_y = player.y - HEIGHT // 2

        # Camera bounds
        target_camera_x = max(0, min(target_camera_x, MAP_WIDTH * TILE_SIZE - WIDTH))
        target_camera_y = max(0, min(target_camera_y, MAP_HEIGHT * TILE_SIZE - HEIGHT))

        # Smooth camera movement
        camera_x += (target_camera_x - camera_x) * CAMERA_SPEED
        camera_y += (target_camera_y - camera_y) * CAMERA_SPEED

        # Update game objects
        player.update()

        # Enemy spawning
        spawn_timer -= 1
        if spawn_timer <= 0:
            enemies.append(spawn_enemy(player))
            spawn_timer = 60  # Spawn enemy every 60 frames

        # Update enemies
        for enemy in enemies[:]:
            enemy.update(player)

            # Check collision with player
            if enemy.rect.colliderect(player.rect):
                player.health -= 1

                # Check for game over
                if player.health <= 0:
                    game_over = True
                    game_over_start_time = pygame.time.get_ticks()

        # Update projectiles
        for proj in projectiles[:]:
            if proj.update():
                projectiles.remove(proj)
                continue

            # Check collision with enemies
            for enemy in enemies[:]:
                if proj.rect.colliderect(enemy.rect):
                    enemy.health -= proj.damage

                    # Remove dead enemies and drop cake
                    if enemy.health <= 0:
                        cakes.append(Cake(enemy.x, enemy.y))
                        enemies.remove(enemy)

                    # Remove projectile after hitting an enemy (except for fire cone)
                    if not isinstance(proj, FireCone):
                        if proj in projectiles:
                            projectiles.remove(proj)
                        break

        # Update cakes
        for cake in cakes[:]:
            cake.update()

            # Check collision with player
            if cake.rect.colliderect(player.rect):
                player.gain_xp(cake.value)
                cakes.remove(cake)

        # Drawing
        window.fill((0, 0, 0))  # Black background for terminal theme

        # Draw office tiles (terminal style)
        for tile_x, tile_y, tile_type in office_tiles:
            if (tile_x + TILE_SIZE > camera_x and 
                tile_x < camera_x + WIDTH and 
                tile_y + TILE_SIZE > camera_y and 
                tile_y < camera_y + HEIGHT):

                if tile_type == 1:  # Terminal window
                    pygame.draw.rect(window, (30, 30, 30), (tile_x - camera_x, tile_y - camera_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(window, (0, 100, 0), (tile_x - camera_x, tile_y - camera_y, TILE_SIZE, TILE_SIZE), 1)
                elif tile_type == 2:  # Command prompt
                    pygame.draw.rect(window, (20, 20, 20), (tile_x - camera_x, tile_y - camera_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(window, (0, 150, 0), (tile_x - camera_x, tile_y - camera_y, TILE_SIZE, TILE_SIZE), 1)

                    # Add text cursor effect
                    if random.random() < 0.3:  # Only some tiles get the cursor
                        cursor_x = tile_x - camera_x + random.randint(5, TILE_SIZE - 10)
                        cursor_y = tile_y - camera_y + random.randint(5, TILE_SIZE - 10)
                        pygame.draw.rect(window, (0, 255, 0), (cursor_x, cursor_y, 5, 2))

        # Draw terminal-style grid lines
        for x in range(0, MAP_WIDTH * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(window, (0, 80, 0), (x - camera_x, 0), (x - camera_x, HEIGHT))
        for y in range(0, MAP_HEIGHT * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(window, (0, 80, 0), (0, y - camera_y), (WIDTH, y - camera_y))

        # Add some terminal effects - random dots of green text
        for _ in range(20):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.rect(window, (0, 200, 0), (x, y, 2, 2))

        # Draw cakes
        for cake in cakes:
            cake.draw(window, camera_x, camera_y)

        # Draw projectiles
        for proj in projectiles:
            proj.draw(window, camera_x, camera_y)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(window, camera_x, camera_y)

        # Draw player
        player.draw(window, camera_x, camera_y)

        # Draw UI
        # - Health bar
        pygame.draw.rect(window, RED, (10, 10, 200, 20))
        pygame.draw.rect(window, GREEN, (10, 10, 200 * (player.health / player.max_health), 20))
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
        window.blit(text, (20, 12))

        # - XP bar
        pygame.draw.rect(window, (100, 100, 100), (10, 40, 200, 20))
        pygame.draw.rect(window, BLUE, (10, 40, 200 * (player.xp / player.xp_to_level), 20))
        text = font.render(f"Level: {player.level} - XP: {player.xp}/{player.xp_to_level}", True, WHITE)
        window.blit(text, (20, 42))

        # - Ability cooldowns
        cooldown_y = 70
        for i, (ability_name, ability) in enumerate(player.abilities.items()):
            pygame.draw.rect(window, (50, 50, 50), (10, cooldown_y + i * 30, 200, 20))

            # Calculate cooldown percentage
            if ability_name == "speed_burst" and ability["active"]:
                # Show duration for active speed burst
                cooldown_percent = ability["duration"] / ability["max_duration"]
                color = YELLOW
            else:
                # Show cooldown for other abilities
                cooldown_percent = 1 - (ability["cooldown"] / ability["max_cooldown"])
                color = (0, 200, 200)

            pygame.draw.rect(window, color, (10, cooldown_y + i * 30, 200 * cooldown_percent, 20))

            # Ability text
            ability_text = ability_name.replace("_", " ").title()
            if ability_name == "speed_burst" and ability["active"]:
                ability_text += f" ({ability['duration']})"
            text = font.render(ability_text, True, WHITE)
            window.blit(text, (20, cooldown_y + i * 30 + 2))

            # Ability key
            key_map = {"lightning": "J", "magic_missile": "K", "fire_cone": "L", "speed_burst": "I"}
            key_text = font.render(key_map[ability_name], True, WHITE)
            window.blit(key_text, (180, cooldown_y + i * 30 + 2))

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()