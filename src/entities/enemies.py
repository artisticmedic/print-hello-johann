
import pygame
import math
import random

class Enemy:
    def __init__(self, x, y, type_id, enemy_img, messages):
        self.x = x
        self.y = y
        self.type_id = type_id
        self.img = enemy_img
        self.speed = 2
        self.health = 30
        self.cooldown = 0
        self.message = random.choice(messages)
        self.message_timer = random.randint(100, 200)  # Random timer for speech bubble
        self.show_message = False
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
        pygame.draw.rect(window, (255, 0, 0), (self.x - camera_x, self.y - camera_y - 10, self.width, 5))
        pygame.draw.rect(window, (0, 255, 0), (self.x - camera_x, self.y - camera_y - 10, self.width * (self.health / 30), 5))
        
        # Draw speech bubble with message
        if self.show_message:
            font = pygame.font.SysFont(None, 16)
            text = font.render(self.message, True, (0, 0, 0))
            
            # Speech bubble background
            bubble_width = text.get_width() + 10
            bubble_height = text.get_height() + 10
            bubble_x = self.x - camera_x - bubble_width // 2 + self.width // 2
            bubble_y = self.y - camera_y - 30
            
            pygame.draw.rect(window, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height))
            pygame.draw.rect(window, (0, 0, 0), (bubble_x, bubble_y, bubble_width, bubble_height), 1)
            
            # Triangle pointer
            pygame.draw.polygon(window, (255, 255, 255), [
                (self.x - camera_x + self.width // 2, self.y - camera_y - 5),
                (self.x - camera_x + self.width // 2 - 5, bubble_y + bubble_height),
                (self.x - camera_x + self.width // 2 + 5, bubble_y + bubble_height)
            ])
            
            # Text
            window.blit(text, (bubble_x + 5, bubble_y + 5))

# Common interruption messages
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

def spawn_enemy(player, map_width, map_height, tile_size, enemy_images):
    # Choose random position outside of screen but within map
    side = random.randint(0, 3)
    if side == 0:  # Top
        x = random.randint(0, map_width * tile_size)
        y = 0
    elif side == 1:  # Right
        x = map_width * tile_size
        y = random.randint(0, map_height * tile_size)
    elif side == 2:  # Bottom
        x = random.randint(0, map_width * tile_size)
        y = map_height * tile_size
    else:  # Left
        x = 0
        y = random.randint(0, map_height * tile_size)
        
    enemy_type = random.randint(0, len(enemy_images) - 1)
    return Enemy(x, y, enemy_type, enemy_images[enemy_type], INTERRUPTION_MESSAGES)
