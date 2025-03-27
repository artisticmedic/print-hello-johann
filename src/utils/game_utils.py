
import pygame
import random

# Helper functions for the game

def create_cake_sprite():
    """Create a birthday cake sprite for XP collection"""
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

def create_office_tiles(map_width, map_height, tile_size):
    """Create a grid of office tiles"""
    office_tiles = []
    for y in range(map_height):
        for x in range(map_width):
            # Create floor tiles (placeholder, could be replaced with actual sprites)
            tile_type = random.randint(0, 2)  # 0: Empty, 1: Desk, 2: Chair
            if tile_type > 0:
                office_tiles.append((x * tile_size, y * tile_size, tile_type))
    return office_tiles

def draw_office_tiles(window, office_tiles, camera_x, camera_y, width, height, tile_size):
    """Draw office environment tiles"""
    for tile_x, tile_y, tile_type in office_tiles:
        if (tile_x + tile_size > camera_x and 
            tile_x < camera_x + width and 
            tile_y + tile_size > camera_y and 
            tile_y < camera_y + height):
            
            if tile_type == 1:  # Desk
                pygame.draw.rect(window, (139, 69, 19), (tile_x - camera_x, tile_y - camera_y, tile_size, tile_size))
            elif tile_type == 2:  # Chair
                pygame.draw.rect(window, (70, 70, 70), (tile_x - camera_x, tile_y - camera_y, tile_size, tile_size))

def draw_grid(window, camera_x, camera_y, width, height, map_width, map_height, tile_size):
    """Draw grid lines for the office floor"""
    for x in range(0, map_width * tile_size, tile_size):
        pygame.draw.line(window, (220, 220, 220), (x - camera_x, 0), (x - camera_x, height))
    for y in range(0, map_height * tile_size, tile_size):
        pygame.draw.line(window, (220, 220, 220), (0, y - camera_y), (width, y - camera_y))

def draw_ui(window, player):
    """Draw game UI elements"""
    # - Health bar
    pygame.draw.rect(window, (255, 0, 0), (10, 10, 200, 20))
    pygame.draw.rect(window, (0, 255, 0), (10, 10, 200 * (player.health / player.max_health), 20))
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"Health: {player.health}/{player.max_health}", True, (255, 255, 255))
    window.blit(text, (20, 12))
    
    # - XP bar
    pygame.draw.rect(window, (100, 100, 100), (10, 40, 200, 20))
    pygame.draw.rect(window, (0, 0, 255), (10, 40, 200 * (player.xp / player.xp_to_level), 20))
    text = font.render(f"Level: {player.level} - XP: {player.xp}/{player.xp_to_level}", True, (255, 255, 255))
    window.blit(text, (20, 42))
    
    # - Ability cooldowns
    cooldown_y = 70
    for i, (ability_name, ability) in enumerate(player.abilities.items()):
        pygame.draw.rect(window, (50, 50, 50), (10, cooldown_y + i * 30, 200, 20))
        
        # Calculate cooldown percentage
        if ability_name == "speed_burst" and ability["active"]:
            # Show duration for active speed burst
            cooldown_percent = ability["duration"] / ability["max_duration"]
            color = (255, 255, 0)
        else:
            # Show cooldown for other abilities
            cooldown_percent = 1 - (ability["cooldown"] / ability["max_cooldown"])
            color = (0, 200, 200)
            
        pygame.draw.rect(window, color, (10, cooldown_y + i * 30, 200 * cooldown_percent, 20))
        
        # Ability text
        ability_text = ability_name.replace("_", " ").title()
        if ability_name == "speed_burst" and ability["active"]:
            ability_text += f" ({ability['duration']})"
        text = font.render(ability_text, True, (255, 255, 255))
        window.blit(text, (20, cooldown_y + i * 30 + 2))
        
        # Ability key
        key_map = {"lightning": "J", "magic_missile": "K", "fire_cone": "L", "speed_burst": "I"}
        key_text = font.render(key_map[ability_name], True, (255, 255, 255))
        window.blit(key_text, (180, cooldown_y + i * 30 + 2))

def draw_game_over(window, width, height):
    """Draw game over screen"""
    window.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 48)
    text = font.render("Happiest of birthdays, Johann!", True, (255, 255, 255))
    window.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 50))
    
    font = pygame.font.SysFont(None, 36)
    text = font.render("Better luck next time!", True, (255, 255, 255))
    window.blit(text, (width // 2 - text.get_width() // 2, height // 2))
    
    font = pygame.font.SysFont(None, 24)
    text = font.render("Press R to restart", True, (255, 255, 255))
    window.blit(text, (width // 2 - text.get_width() // 2, height // 2 + 50))
