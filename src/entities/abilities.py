
import pygame
import math

class Lightning:
    def __init__(self, x, y, lightning_img=None):
        self.x = x
        self.y = y
        self.img = lightning_img
        if lightning_img:
            self.width = lightning_img.get_width()
            self.height = lightning_img.get_height()
        else:
            self.width = 50
            self.height = 10
            # Create placeholder image if none provided
            self.img = pygame.Surface((self.width, self.height))
            self.img.fill((255, 255, 0))  # Yellow color
        self.lifetime = 10
        self.damage = 20
        self.rect = pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

    def update(self):
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, window, camera_x, camera_y):
        window.blit(self.img, (self.x - self.width // 2 - camera_x, self.y - camera_y))

class MagicMissile:
    def __init__(self, x, y, target, missile_img=None):
        self.x = x
        self.y = y
        self.target = target  # Target enemy for homing
        self.speed = 6
        self.img = missile_img
        if missile_img:
            self.width = missile_img.get_width()
            self.height = missile_img.get_height()
        else:
            self.width = 10
            self.height = 10
            # Create placeholder image if none provided
            self.img = pygame.Surface((self.width, self.height))
            self.img.fill((0, 255, 255))  # Cyan color
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
        window.blit(self.img, (self.x - self.width // 2 - camera_x, self.y - self.height // 2 - camera_y))

class FireCone:
    def __init__(self, x, y, cone_img=None):
        self.x = x
        self.y = y
        self.img = cone_img
        if cone_img:
            self.width = cone_img.get_width()
            self.height = cone_img.get_height()
        else:
            self.width = 50
            self.height = 50
            # Create placeholder image if none provided
            self.img = pygame.Surface((self.width, self.height))
            self.img.fill((255, 165, 0))  # Orange color
        self.lifetime = 15
        self.damage = 10
        self.rect = pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

    def update(self):
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self, window, camera_x, camera_y):
        window.blit(self.img, (self.x - self.width // 2 - camera_x, self.y - camera_y))

class Cake:  # Birthday cake collectible (XP)
    def __init__(self, x, y, cake_img=None):
        self.x = x
        self.y = y
        self.img = cake_img
        if cake_img:
            self.width = cake_img.get_width()
            self.height = cake_img.get_height()
        else:
            self.width = 20
            self.height = 20
            # Create placeholder cake if no image provided
            self.img = self.create_cake_sprite()
        self.value = 1
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.pulse = 0
        self.growing = True

    def create_cake_sprite(self):
        cake = pygame.Surface((20, 20), pygame.SRCALPHA)
        # Base of cake (brown)
        pygame.draw.rect(cake, (139, 69, 19), (2, 10, 16, 10))
        # Frosting (white)
        pygame.draw.rect(cake, (255, 255, 255), (1, 5, 18, 5))
        # Candle (red)
        pygame.draw.rect(cake, (255, 0, 0), (9, 0, 2, 5))
        # Flame (yellow)
        pygame.draw.circle(cake, (255, 255, 0), (10, 0), 2)
        return cake

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
            self.img, 
            (int(self.width * pulse_scale), int(self.height * pulse_scale))
        )
        window.blit(
            pulsed_img, 
            (
                self.x - camera_x - (pulsed_img.get_width() - self.width) // 2, 
                self.y - camera_y - (pulsed_img.get_height() - self.height) // 2
            )
        )
