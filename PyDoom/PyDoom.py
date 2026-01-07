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
        
        # Cache for trigonometric calculations
        self._cos_cache = math.cos(math.radians(rotation))
        self._sin_cache = math.sin(math.radians(rotation))
    
    def _check_collision(self, x, y, game_map):
        """Check if position collides with walls using collision radius"""
        # Check the center point
        if game_map.is_wall(x, y):
            return True
        
        # Check points around the player's collision circle
        # Check 4 cardinal directions at the collision radius
        offsets = [
            (self.collision_radius, 0),
            (-self.collision_radius, 0),
            (0, self.collision_radius),
            (0, -self.collision_radius),
            # Also check diagonal corners for better collision
            (self.collision_radius * 0.707, self.collision_radius * 0.707),
            (-self.collision_radius * 0.707, self.collision_radius * 0.707),
            (self.collision_radius * 0.707, -self.collision_radius * 0.707),
            (-self.collision_radius * 0.707, -self.collision_radius * 0.707)
        ]
        
        for offset_x, offset_y in offsets:
            if game_map.is_wall(x + offset_x, y + offset_y):
                return True
        
        return False
        
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
        """Move player forward in the direction they're facing"""
        new_x = self.x + self._cos_cache * self.move_speed * dt
        new_y = self.y + self._sin_cache * self.move_speed * dt
        if not self._check_collision(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y
        
    def move_backward(self, dt, game_map):
        """Move player backward"""
        new_x = self.x - self._cos_cache * self.move_speed * dt
        new_y = self.y - self._sin_cache * self.move_speed * dt
        if not self._check_collision(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y
        
    def strafe_left(self, dt, game_map):
        """Strafe left (perpendicular to facing direction)"""
        # Left is 90 degrees counter-clockwise: (cos, sin) -> (sin, -cos)
        new_x = self.x + self._sin_cache * self.move_speed * dt
        new_y = self.y - self._cos_cache * self.move_speed * dt
        if not self._check_collision(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y
        
    def strafe_right(self, dt, game_map):
        """Strafe right (perpendicular to facing direction)"""
        # Right is 90 degrees clockwise: (cos, sin) -> (-sin, cos)
        new_x = self.x - self._sin_cache * self.move_speed * dt
        new_y = self.y + self._cos_cache * self.move_speed * dt
        if not self._check_collision(new_x, new_y, game_map):
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
        self.wall_buffer = []  # Cache for wall rendering
        
        # Load or create textures
        self.textures = {}
        self._init_textures()
        
        # Create a surface for faster blitting
        self.wall_surface = pygame.Surface((1, screen_height))
        
    def _init_textures(self):
        """Initialize wall textures"""
        # Create a simple brick texture (64x64)
        texture_size = 64
        brick_texture = pygame.Surface((texture_size, texture_size))
        
        # Draw brick pattern
        brick_color = (120, 60, 40)
        mortar_color = (80, 80, 80)
        brick_texture.fill(brick_color)
        
        # Draw horizontal mortar lines
        for y in range(0, texture_size, 16):
            pygame.draw.line(brick_texture, mortar_color, (0, y), (texture_size, y), 2)
        
        # Draw vertical mortar lines (offset every other row)
        for y in range(0, texture_size // 16):
            offset = 8 if y % 2 == 0 else 0
            for x in range(offset, texture_size, 32):
                pygame.draw.line(brick_texture, mortar_color, (x, y * 16), (x, (y + 1) * 16), 2)
        
        self.textures['wall'] = brick_texture
        self.texture_width = texture_size
        self.texture_height = texture_size
        
        # Pre-create shaded versions of textures for performance
        self._create_shaded_textures()
        
    def _create_shaded_textures(self):
        """Create pre-shaded versions of textures"""
        wall_texture = self.textures['wall']
        
        # No shading - all textures at full brightness
        self.shaded_textures = {}
        self.shaded_textures_y = {}
        
        # Create single brightness level for both X and Y sides
        for i in range(6):
            self.shaded_textures[i] = wall_texture.copy()
            self.shaded_textures_y[i] = wall_texture.copy()

    def cast_ray(self, player, game_map, angle):
        """Cast a single ray using DDA algorithm for better performance"""
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
        max_iterations = 50  # Prevent infinite loops
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
        
        # Calculate wall_x: exact position where ray hit the wall
        # This is the fractional part of the wall coordinate
        if side == 0:
            # X-side hit: use Y coordinate
            wall_x = y + distance * ray_dy
        else:
            # Y-side hit: use X coordinate
            wall_x = x + distance * ray_dx
        
        # Get fractional part (0.0 to 1.0)
        wall_x = wall_x - math.floor(wall_x)
            
        return distance, side, wall_x
        
    def render_3d_view(self, screen, player, game_map):
        """Render the 3D view using raycasting with optimized texture mapping"""
        half_fov = self.fov / 2.0
        
        # Pre-calculate constants
        screen_half = self.screen_height / 2
        
        # Clear wall buffer
        self.wall_buffer.clear()
        
        for ray_index in range(self.num_rays):
            # Calculate ray angle
            angle_offset = (ray_index / self.num_rays - 0.5) * self.fov
            ray_angle = player.rotation + angle_offset
            
            # Cast ray
            distance, side, wall_x = self.cast_ray(player, game_map, ray_angle)
            
            # Fix fish-eye effect
            distance *= math.cos(math.radians(angle_offset))
            
            # Calculate wall height based on distance
            if distance < 0.01:
                distance = 0.01
                
            wall_height = (self.screen_height / distance) * 0.5
            
            # Calculate wall top and bottom
            wall_top = screen_half - (wall_height / 2)
            wall_bottom = screen_half + (wall_height / 2)
            
            # Calculate texture X coordinate
            tex_x = int(wall_x * self.texture_width)
            if tex_x < 0:
                tex_x = 0
            if tex_x >= self.texture_width:
                tex_x = self.texture_width - 1
            
            # No shading - use level 0 (full brightness) for everything
            shade_level = 0
            
            self.wall_buffer.append((ray_index, wall_top, wall_bottom, tex_x, shade_level, side))
        
        # Batch render ceiling and floor
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, self.screen_width, screen_half))
        pygame.draw.rect(screen, (30, 30, 30), (0, screen_half, self.screen_width, screen_half))
        
        # Draw textured walls using optimized column slicing
        for ray_index, wall_top, wall_bottom, tex_x, shade_level, side in self.wall_buffer:
            
            # 1. Calculate the actual pixel range to draw on screen
            draw_start = max(0, int(wall_top))
            draw_end = min(self.screen_height, int(wall_bottom))
            
            # 2. Calculate height of the drawn segment
            draw_height = draw_end - draw_start
            
            if draw_height <= 0:
                continue

            # 3. Calculate the "True" height of the wall (even the parts off-screen)
            full_wall_height = wall_bottom - wall_top
            
            # Prevent division by zero
            if full_wall_height <= 0:
                continue
                
            # 4. Get the texture (assuming you want the unshaded one for now)
            texture = self.shaded_textures[0]
            
            # 5. Math Magic: Calculate texture coordinates
            # ratio: How many texture pixels match 1 screen pixel?
            ratio = self.texture_height / full_wall_height
            
            # src_y: Where in the texture do we start? 
            # If wall_top is negative (off-screen), this skips the top part of the texture
            src_y = (draw_start - wall_top) * ratio
            
            # src_h: How much of the texture height do we need?
            src_h = draw_height * ratio
            
            # 6. Safety Clamping
            # Floating point errors can make src_y slightly negative or too large
            if src_y < 0: src_y = 0
            if src_h <= 0: src_h = 1 # minimal height
            if src_y + src_h > self.texture_height:
                src_h = self.texture_height - src_y

            try:
                # 7. Extract only the needed part of the texture
                # subsurface((x, y, width, height))
                texture_chunk = texture.subsurface((tex_x, int(src_y), 1, int(src_h)))
                
                # 8. Scale ONLY that chunk to fit the screen gap
                scaled_chunk = pygame.transform.scale(texture_chunk, (1, draw_height))
                
                # 9. Blit
                screen.blit(scaled_chunk, (ray_index, draw_start))
                
            except (ValueError, pygame.error):
                # Fallback if math goes weird (e.g., extremely close walls)
                pass
    
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
