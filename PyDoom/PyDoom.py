import pygame
import sys
import math
from pygame.locals import *

class Player:
    def __init__(self, x, y, rotation=0.0):
        """Initialize player with position and rotation"""
        self.x = float(x)
        self.y = float(y)
        self.rotation = float(rotation)  # Rotation in degrees
        
        # Movement settings
        self.move_speed = 3.0  # units per second
        self.rotation_speed = 120.0  # degrees per second
        
    def set_position(self, x, y):
        """Set player position"""
        self.x = float(x)
        self.y = float(y)
        
    def set_rotation(self, rotation):
        """Set player rotation"""
        self.rotation = float(rotation)
        
    def move(self, dx, dy):
        """Move player by delta amounts"""
        self.x += float(dx)
        self.y += float(dy)
        
    def rotate(self, degrees):
        """Rotate player by degrees"""
        self.rotation += float(degrees)
        # Keep rotation in 0-360 range
        self.rotation = self.rotation % 360.0
        
    def move_forward(self, dt, game_map):
        """Move player forward in the direction they're facing"""
        rad = math.radians(self.rotation)
        new_x = self.x + math.cos(rad) * self.move_speed * dt
        new_y = self.y + math.sin(rad) * self.move_speed * dt
        if not game_map.is_wall(new_x, new_y):
            self.x = new_x
            self.y = new_y
        
    def move_backward(self, dt, game_map):
        """Move player backward"""
        rad = math.radians(self.rotation)
        new_x = self.x - math.cos(rad) * self.move_speed * dt
        new_y = self.y - math.sin(rad) * self.move_speed * dt
        if not game_map.is_wall(new_x, new_y):
            self.x = new_x
            self.y = new_y
        
    def strafe_left(self, dt, game_map):
        """Strafe left (perpendicular to facing direction)"""
        rad = math.radians(self.rotation - 90)
        new_x = self.x + math.cos(rad) * self.move_speed * dt
        new_y = self.y + math.sin(rad) * self.move_speed * dt
        if not game_map.is_wall(new_x, new_y):
            self.x = new_x
            self.y = new_y
        
    def strafe_right(self, dt, game_map):
        """Strafe right (perpendicular to facing direction)"""
        rad = math.radians(self.rotation + 90)
        new_x = self.x + math.cos(rad) * self.move_speed * dt
        new_y = self.y + math.sin(rad) * self.move_speed * dt
        if not game_map.is_wall(new_x, new_y):
            self.x = new_x
            self.y = new_y
        
    def look_left(self, dt):
        """Rotate player left"""
        self.rotate(-self.rotation_speed * dt)
        
    def look_right(self, dt):
        """Rotate player right"""
        self.rotate(self.rotation_speed * dt)


class Map:
    def __init__(self, grid):
        """Initialize map with a 2D grid where 1 = wall, 0 = empty"""
        self.grid = grid
        self.width = len(grid[0])
        self.height = len(grid)
        self.tile_size = 64
        
    def is_wall(self, x, y):
        """Check if position is a wall"""
        map_x = int(x)
        map_y = int(y)
        
        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return True
            
        return self.grid[map_y][map_x] == 1
        
    def get_tile(self, x, y):
        """Get tile value at position"""
        map_x = int(x)
        map_y = int(y)
        
        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return 1
            
        return self.grid[map_y][map_x]


class Raycaster:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fov = 60  # Field of view in degrees
        self.max_depth = 20.0  # Maximum ray distance
        self.num_rays = screen_width  # One ray per column
        
    def cast_ray(self, player, game_map, angle):
        """Cast a single ray and return distance to wall"""
        rad = math.radians(angle)
        ray_dx = math.cos(rad)
        ray_dy = math.sin(rad)
        
        # Start from player position
        x = player.x
        y = player.y
        
        # Step along ray until we hit a wall
        step = 0.01
        distance = 0.0
        
        while distance < self.max_depth:
            x += ray_dx * step
            y += ray_dy * step
            distance += step
            
            if game_map.is_wall(x, y):
                return distance
                
        return self.max_depth
        
    def render_3d_view(self, screen, player, game_map):
        """Render the 3D view using raycasting"""
        half_fov = self.fov / 2.0
        
        for ray_index in range(self.num_rays):
            # Calculate ray angle
            angle_offset = (ray_index / self.num_rays - 0.5) * self.fov
            ray_angle = player.rotation + angle_offset
            
            # Cast ray
            distance = self.cast_ray(player, game_map, ray_angle)
            
            # Fix fish-eye effect
            distance *= math.cos(math.radians(angle_offset))
            
            # Calculate wall height based on distance
            if distance == 0:
                distance = 0.01
                
            wall_height = (self.screen_height / distance) * 0.5
            
            # Calculate wall top and bottom
            wall_top = (self.screen_height / 2) - (wall_height / 2)
            wall_bottom = (self.screen_height / 2) + (wall_height / 2)
            
            # Calculate shading based on distance
            shade = max(0, min(255, 255 - (distance * 12)))
            color = (shade, shade, shade)
            
            # Draw ceiling
            pygame.draw.line(screen, (50, 50, 50), 
                           (ray_index, 0), 
                           (ray_index, wall_top))
            
            # Draw wall
            pygame.draw.line(screen, color, 
                           (ray_index, wall_top), 
                           (ray_index, wall_bottom))
            
            # Draw floor
            pygame.draw.line(screen, (30, 30, 30), 
                           (ray_index, wall_bottom), 
                           (ray_index, self.screen_height))
    


class Game:
    def __init__(self):
        pygame.init()
        
        # Display settings
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("PyDoom")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.running = True
        self.paused = False
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        
        # Create a simple map (1 = wall, 0 = empty)
        self.game_map = Map([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ])
        
        # Initialize player in an open area
        self.player = Player(2.5, 2.5, 0.0)
        
        # Initialize raycaster
        self.raycaster = Raycaster(self.screen_width, self.screen_height)
        
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                self.handle_keydown(event)
            elif event.type == KEYUP:
                self.handle_keyup(event)
            elif event.type == MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
                
    def handle_keydown(self, event):
        """Handle key press events"""
        if event.key == K_ESCAPE:
            self.running = False
        elif event.key == K_p:
            self.paused = not self.paused
            
    def handle_keyup(self, event):
        """Handle key release events"""
        pass
        
    def handle_mouse_click(self, event):
        """Handle mouse click events"""
        pass
        
    def handle_player_input(self, dt):
        """Handle continuous keyboard input for player movement"""
        keys = pygame.key.get_pressed()
        
        # Movement: WASD
        if keys[K_w]:
            self.player.move_forward(dt, self.game_map)
        if keys[K_s]:
            self.player.move_backward(dt, self.game_map)
        if keys[K_a]:
            self.player.strafe_left(dt, self.game_map)
        if keys[K_d]:
            self.player.strafe_right(dt, self.game_map)
            
        # Rotation: Arrow keys
        if keys[K_LEFT]:
            self.player.look_left(dt)
        if keys[K_RIGHT]:
            self.player.look_right(dt)
        
    def update(self, dt):
        """Update game logic"""
        if not self.paused:
            self.handle_player_input(dt)
            
    def render(self):
        """Render everything to the screen"""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Render 3D view
        self.raycaster.render_3d_view(self.screen, self.player, self.game_map)
        
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        while self.running:
            # Delta time in seconds
            dt = self.clock.tick(self.fps) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
            
        self.quit()
        
    def quit(self):
        """Clean up and quit"""
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
