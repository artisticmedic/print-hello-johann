
import pygame
import math

class Player:
    def __init__(self, x, y, hero_img):
        self.x = x
        self.y = y
        self.img = hero_img
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

    def move(self, dx, dy, map_width, map_height, tile_size):
        speed_multiplier = 2 if self.abilities["speed_burst"]["active"] else 1
        self.x += dx * self.speed * speed_multiplier
        self.y += dy * self.speed * speed_multiplier
        
        # Keep player within map bounds
        self.x = max(0, min(self.x, map_width * tile_size - self.width))
        self.y = max(0, min(self.y, map_height * tile_size - self.height))
        
        self.rect.x = self.x
        self.rect.y = self.y

    def use_ability(self, ability_name, enemies, projectiles, abilities_module):
        ability = self.abilities[ability_name]
        if ability["cooldown"] <= 0:
            ability["cooldown"] = ability["max_cooldown"]
            
            if ability_name == "lightning":
                projectiles.append(abilities_module.Lightning(self.x + self.width // 2, self.y + self.height // 2))
            
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
                    projectiles.append(abilities_module.MagicMissile(
                        self.x + self.width // 2, 
                        self.y + self.height // 2,
                        closest_enemy  # Pass target enemy for homing
                    ))
            
            elif ability_name == "fire_cone":
                projectiles.append(abilities_module.FireCone(self.x + self.width // 2, self.y + self.height // 2))
            
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
        window.blit(self.img, (self.x - camera_x, self.y - camera_y))
        
        # Draw health bar
        pygame.draw.rect(window, (255, 0, 0), (self.x - camera_x, self.y - camera_y - 10, self.width, 5))
        pygame.draw.rect(window, (0, 255, 0), (self.x - camera_x, self.y - camera_y - 10, self.width * (self.health / self.max_health), 5))

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp = 0
        self.xp_to_level = 10 * self.level
        self.health = self.max_health  # Refill health on level up
