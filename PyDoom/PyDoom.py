import pygame
import sys
import math
from pygame.locals import *

class Player:
    def __init__(self, x, y, rotation=0.0):
        """Initialize player with position and rotation"""
        self.x = float(x)
        self.y = float(y)
        self.rotation = float(rotation)  # Rotation in degrees (yaw)
        
        # Movement settings
        self.move_speed = 3.0  # units per second
        self.rotation_speed = 120.0  # degrees per second
        self.mouse_sensitivity = 0.2  # Mouse sensitivity multiplier
        
        # Collision settings
        self.collision_radius = 0.1  # Radius for collision detection
        self.anticipation_frames = 2  # Number of frames to look ahead
        
        # Pre-calculate collision offsets
        self.collision_offsets = [
            (self.collision_radius, 0),
            (-self.collision_radius, 0),
            (0, self.collision_radius),
            (0, -self.collision_radius),
            (self.collision_radius * 0.707, self.collision_radius * 0.707),
            (-self.collision_radius * 0.707, self.collision_radius * 0.707),
            (self.collision_radius * 0.707, -self.collision_radius * 0.707),
            (-self.collision_radius * 0.707, -self.collision_radius * 0.707)
        ]
        
        # Cache for trigonometric calculations
        self._cos_cache = math.cos(math.radians(rotation))
        self._sin_cache = math.sin(math.radians(rotation))
    
    def _check_collision(self, x, y, game_map):
        """Check if position collides with walls using collision radius"""
        # Check the center point
        if game_map.is_wall(x, y):
            return True
        
        # Use the pre-calculated list
        for offset_x, offset_y in self.collision_offsets:
            if game_map.is_wall(x + offset_x, y + offset_y):
                return True
        
        return False
    
    def _move_with_collision(self, dx, dy, game_map):
        """Move with anticipation and wall sliding"""
        # Calculate anticipated position (look ahead)
        anticipated_x = self.x + dx * self.anticipation_frames
        anticipated_y = self.y + dy * self.anticipation_frames
    
        # Check if final position will collide
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Try moving in both X and Y
        if not self._check_collision(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y
            return

        # If diagonal movement failed, try sliding along walls
        # Try X movement only
        if not self._check_collision(new_x, self.y, game_map):
            self.x = new_x

        # Try Y movement only
        if not self._check_collision(self.x, new_y, game_map):
            self.y = new_y
        
    def set_position(self, x, y):
        """Set player position"""
        self.x = float(x)
        self.y = float(y)
        
    def set_rotation(self, rotation):
        """Set player rotation"""
        self.rotation = float(rotation)
        self._update_trig_cache()
        
    def _update_trig_cache(self):
        """Update cached trigonometric values"""
        rad = math.radians(self.rotation)
        self._cos_cache = math.cos(rad)
        self._sin_cache = math.sin(rad)
        
    def move(self, dx, dy):
        """Move player by delta amounts"""
        self.x += float(dx)
        self.y += float(dy)
        
    def rotate(self, degrees):
        """Rotate player by degrees"""
        self.rotation += float(degrees)
        # Keep rotation in 0-360 range
        self.rotation = self.rotation % 360.0
        self._update_trig_cache()
        
    def rotate_from_mouse(self, dx):
        """Rotate player based on mouse movement"""
        self.rotate(dx * self.mouse_sensitivity)
        
    def move_forward(self, dt, game_map):
        """Move player forward in the direction they're facing with anticipation"""
        dx = self._cos_cache * self.move_speed * dt
        dy = self._sin_cache * self.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
    def move_backward(self, dt, game_map):
        """Move player backward with anticipation"""
        dx = -self._cos_cache * self.move_speed * dt
        dy = -self._sin_cache * self.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
    def strafe_left(self, dt, game_map):
        """Strafe left (perpendicular to facing direction) with anticipation"""
        # Left is 90 degrees counter-clockwise: (cos, sin) -> (sin, -cos)
        dx = self._sin_cache * self.move_speed * dt
        dy = -self._cos_cache * self.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
    def strafe_right(self, dt, game_map):
        """Strafe right (perpendicular to facing direction) with anticipation"""
        # Right is 90 degrees clockwise: (cos, sin) -> (-sin, cos)
        dx = -self._sin_cache * self.move_speed * dt
        dy = self._cos_cache * self.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
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


def generate_texture(size=64, color1=(150, 150, 150), color2=(100, 100, 100)):
    """Generates a simple checkerboard texture surface"""
    surface = pygame.Surface((size, size))
    surface.fill(color1)
    # Draw a checker pattern
    pygame.draw.rect(surface, color2, (0, 0, size//2, size//2))
    pygame.draw.rect(surface, color2, (size//2, size//2, size//2, size//2))
    return surface

class Raycaster:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fov = 60  # Field of view in degrees
        self.max_depth = 20.0  # Maximum ray distance
        
        # PERFORMANCE SETTING:
        # Texture mapping in Python is slow. We reduce resolution to keep FPS high.
        # // 2 means half resolution (e.g., 800 rays for 1600px screen).
        self.num_rays = screen_width // 2
        self.ray_width = self.screen_width / self.num_rays
        
        self.wall_buffer = []  # Cache for wall rendering
        
        # Initialize Texture
        # In the future, use: self.wall_texture = pygame.image.load("wall.png").convert()
        self.wall_texture = generate_texture(64, (120, 120, 120), (80, 80, 80))
        self.tex_width = self.wall_texture.get_width()
        self.tex_height = self.wall_texture.get_height()
        
    def cast_ray(self, player, game_map, angle):
        """Cast a single ray using DDA algorithm"""
        rad = math.radians(angle)
        ray_dx = math.cos(rad)
        ray_dy = math.sin(rad)
        
        # Player position
        x = player.x
        y = player.y
        
        # Map position
        map_x = int(x)
        map_y = int(y)
        
        # Length of ray from one x or y-side to next x or y-side
        try:
            delta_dist_x = abs(1 / ray_dx) if ray_dx != 0 else float('inf')
            delta_dist_y = abs(1 / ray_dy) if ray_dy != 0 else float('inf')
        except ZeroDivisionError:
            delta_dist_x = float('inf')
            delta_dist_y = float('inf')
        
        # Calculate step and initial side_dist
        if ray_dx < 0:
            step_x = -1
            side_dist_x = (x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - x) * delta_dist_x
            
        if ray_dy < 0:
            step_y = -1
            side_dist_y = (y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - y) * delta_dist_y
        
        # Perform DDA
        hit = False
        side = 0  # 0 for x-side, 1 for y-side
        max_iterations = 50
        iterations = 0
        
        while not hit and iterations < max_iterations:
            # Jump to next map square in x or y direction
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            iterations += 1
            
            # Check if ray has hit a wall
            if game_map.get_tile(map_x, map_y) == 1:
                hit = True
        
        # Calculate distance
        if side == 0:
            distance = (map_x - x + (1 - step_x) / 2) / ray_dx if ray_dx != 0 else self.max_depth
        else:
            distance = (map_y - y + (1 - step_y) / 2) / ray_dy if ray_dy != 0 else self.max_depth
        
        distance = abs(distance)
        
        if distance > self.max_depth or distance < 0:
            distance = self.max_depth
            
        return distance, side, ray_dx, ray_dy
        
    def render_3d_view(self, screen, player, game_map):
        """Render the 3D view using raycasting with textures"""
        
        aspect_ratio = self.screen_width / self.screen_height

        # Pre-calculate geometry
        half_fov_rad = math.radians(self.fov / 2)
        tan_half_fov = math.tan(half_fov_rad)
        screen_half = self.screen_height / 2
        
        # Batch render ceiling and floor
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, self.screen_width, screen_half))
        pygame.draw.rect(screen, (30, 30, 30), (0, screen_half, self.screen_width, screen_half))
        
        for ray_index in range(self.num_rays):
            # Calculate Screen Coordinate
            screen_x = (2 * ray_index) / self.num_rays - 1
            
            angle_offset_rad = math.atan(screen_x * tan_half_fov * aspect_ratio)
            angle_offset_deg = math.degrees(angle_offset_rad)
            
            # Apply to player rotation
            ray_angle = player.rotation + angle_offset_deg
            
            # Cast ray - getting distance AND vectors
            distance, side, ray_dx, ray_dy = self.cast_ray(player, game_map, ray_angle)
            
            # Fix fish-eye effect
            distance *= math.cos(angle_offset_rad)
            
            if distance < 0.01:
                distance = 0.01
                
            # Calculate wall height
            wall_height = int(self.screen_height / distance)
            wall_top = int(screen_half - (wall_height / 2))
            
            # --- TEXTURE CALCULATION ---
            
            # 1. Calculate exactly where the wall was hit
            if side == 0:
                wall_x = player.y + distance * ray_dy
            else:
                wall_x = player.x + distance * ray_dx
            
            wall_x -= math.floor(wall_x)
            
            # 2. X coordinate on the texture
            tex_x = int(wall_x * self.tex_width)
            
            # 3. Prevent texture mirroring
            if side == 0 and ray_dx > 0:
                tex_x = self.tex_width - tex_x - 1
            if side == 1 and ray_dy < 0:
                tex_x = self.tex_width - tex_x - 1
                
            # 4. Create the vertical strip
            # We use a subsurface: (x, y, width, height)
            tex_strip = self.wall_texture.subsurface((tex_x, 0, 1, self.tex_height))
            
            # 5. Scale it to the height of the wall on screen
            # We add 1 to width to prevent gap artifacts
            render_width = int(self.ray_width) + 1 
            
            # Optimization: Don't draw if invisible or crazy huge
            if wall_height > 0 and wall_height < 8000:
                scaled_strip = pygame.transform.scale(tex_strip, (render_width, wall_height))
                
                # 6. Darken the Y-sides for simple lighting effect
                if side == 1:
                    darken_surf = pygame.Surface((render_width, wall_height))
                    darken_surf.set_alpha(80) # 0-255 transparency
                    darken_surf.fill((0,0,0))
                    scaled_strip.blit(darken_surf, (0,0))

                screen.blit(scaled_strip, (ray_index * self.ray_width, wall_top))

    def render_minimap(self, screen, player, game_map):
        """Render a 2D minimap in the corner"""
        minimap_size = 150
        minimap_scale = minimap_size / max(game_map.width, game_map.height)
        minimap_x = screen.get_width() - minimap_size - 10
        minimap_y = 10
        
        # Draw minimap background
        pygame.draw.rect(screen, (0, 0, 0), 
                        (minimap_x, minimap_y, minimap_size, minimap_size))
        
        # Draw map tiles
        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.grid[y][x] == 1:
                    tile_x = minimap_x + x * minimap_scale
                    tile_y = minimap_y + y * minimap_scale
                    pygame.draw.rect(screen, (100, 100, 100),
                                   (tile_x, tile_y, minimap_scale, minimap_scale))
        
        # Draw player
        player_x = minimap_x + player.x * minimap_scale
        player_y = minimap_y + player.y * minimap_scale
        pygame.draw.circle(screen, (255, 0, 0), (int(player_x), int(player_y)), 3)
        
        # Draw player direction
        rad = math.radians(player.rotation)
        end_x = player_x + math.cos(rad) * 10
        end_y = player_y + math.sin(rad) * 10
        pygame.draw.line(screen, (255, 0, 0), 
                        (player_x, player_y), 
                        (end_x, end_y), 2)


class Game:
    def __init__(self):
        pygame.init()
        
        # Display settings
        self.screen_width = 1600
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("PyDoom")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.running = True
        self.paused = False
        
        # Performance settings
        self.show_fps = True
        
        # Mouse control settings
        self.last_mouse_pos = None
        
        # Grab mouse input
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        
        # Create a simple map (1 = wall, 0 = empty)
        self.game_map = Map([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
])
        
        # Initialize player in an open area
        self.player = Player(25, 20, 0.0)
        
        # Initialize raycaster
        self.raycaster = Raycaster(self.screen_width, self.screen_height)
        
        # Font for FPS display
        self.font = pygame.font.Font(None, 36)
        
        # Center mouse
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        pygame.mouse.set_pos(center_x, center_y)
        self.last_mouse_pos = (center_x, center_y)

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
            elif event.type == MOUSEMOTION:
                self.handle_mouse_motion(event)
                
    def handle_keydown(self, event):
        """Handle key press events"""
        if event.key == K_ESCAPE:
            self.running = False
        elif event.key == K_p:
            self.paused = not self.paused
            if self.paused:
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
            else:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                pygame.mouse.get_rel()  # Clear relative motion

    def handle_keyup(self, event):
        """Handle key release events"""
        pass
        
    def handle_mouse_click(self, event):
        """Handle mouse click events"""
        pass
        
    def handle_mouse_motion(self, event):
        """Handle mouse motion events"""
        if not self.paused:
            # Get mouse movement using relative motion
            dx, dy = pygame.mouse.get_rel()
            
            # Apply mouse movement to player rotation (horizontal only)
            if dx != 0:
                self.player.rotate_from_mouse(dx)


    def handle_player_input(self, dt):
        """Handle continuous keyboard input for player movement"""
        keys = pygame.key.get_pressed()
        
        # Initialize total movement vector
        total_dx = 0.0
        total_dy = 0.0
        
        move_speed = self.player.move_speed * dt
        
        # 1. Accumulate movement vectors based on keys
        # Forward (W)
        if keys[K_w]:
            total_dx += self.player._cos_cache * move_speed
            total_dy += self.player._sin_cache * move_speed
            
        # Backward (S)
        if keys[K_s]:
            total_dx += -self.player._cos_cache * move_speed
            total_dy += -self.player._sin_cache * move_speed
            
        # Strafe Left (A)
        if keys[K_a]:
            total_dx += self.player._sin_cache * move_speed
            total_dy += -self.player._cos_cache * move_speed
            
        # Strafe Right (D)
        if keys[K_d]:
            total_dx += -self.player._sin_cache * move_speed
            total_dy += self.player._cos_cache * move_speed

        # 2. Normalize vector 
        # Without this, moving diagonally (W+D) makes you move ~1.4x faster
        if keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d]:
            # If we are moving diagonally (non-zero in both axes relative to player), 
            # the magnitude will be greater than move_speed
            current_speed = math.sqrt(total_dx**2 + total_dy**2)
            if current_speed > move_speed:
                scale = move_speed / current_speed
                total_dx *= scale
                total_dy *= scale

        # 3. Apply ONE physics update with the combined vector
        if total_dx != 0 or total_dy != 0:
            self.player._move_with_collision(total_dx, total_dy, self.game_map)
            
        # Rotation: Arrow keys (This is fine to keep separate as it doesn't affect X/Y collision)
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
        
        # Render minimap
        self.raycaster.render_minimap(self.screen, self.player, self.game_map)
        
        # Display FPS
        if self.show_fps:
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, self.GREEN)
            self.screen.blit(fps_text, (10, 10))
        
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
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
