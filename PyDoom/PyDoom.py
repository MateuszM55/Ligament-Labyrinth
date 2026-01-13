"""PyDoom - A raycasting game engine inspired by Doom."""

import pygame
import sys
import math
from typing import Tuple, List, Optional
import numpy as np
from pygame.locals import *

from settings import settings
from managers import AssetManager


class Player:
    """Represents the player with position, rotation, and movement capabilities."""
    
    def __init__(self, x: float, y: float, rotation: float = 0.0) -> None:
        """Initialize the player.
        
        Args:
            x: Initial x position
            y: Initial y position
            rotation: Initial rotation in degrees
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.rotation: float = float(rotation)
        
        # View bobbing state
        self.bob_phase: float = 0.0
        self.bob_offset_y: float = 0.0
        self.is_moving: bool = False
        
        # Pre-calculate collision offsets
        radius = settings.player.collision_radius
        self.collision_offsets: List[Tuple[float, float]] = [
            (radius, 0),
            (-radius, 0),
            (0, radius),
            (0, -radius),
            (radius * 0.707, radius * 0.707),
            (-radius * 0.707, radius * 0.707),
            (radius * 0.707, -radius * 0.707),
            (-radius * 0.707, -radius * 0.707)
        ]
        
        # Cache for trigonometric calculations
        self._cos_cache: float = math.cos(math.radians(rotation))
        self._sin_cache: float = math.sin(math.radians(rotation))
    
    def _check_collision(self, x: float, y: float, game_map: 'Map') -> bool:
        """Check if position collides with walls using multiple points.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            game_map: The game map to check against
            
        Returns:
            True if collision detected, False otherwise
        """
        if game_map.is_wall(x, y):
            return True
        
        for offset_x, offset_y in self.collision_offsets:
            if game_map.is_wall(x + offset_x, y + offset_y):
                return True
        
        return False
    
    def _move_with_collision(self, dx: float, dy: float, game_map: 'Map') -> None:
        """Move player with collision detection and wall sliding.
        
        Args:
            dx: Change in x position
            dy: Change in y position
            game_map: The game map to check collisions against
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Try moving in both X and Y
        if not self._check_collision(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y
            return

        # If diagonal movement failed, try sliding along walls
        if not self._check_collision(new_x, self.y, game_map):
            self.x = new_x

        if not self._check_collision(self.x, new_y, game_map):
            self.y = new_y
        
    def set_position(self, x: float, y: float) -> None:
        """Set player position.
        
        Args:
            x: New x position
            y: New y position
        """
        self.x = float(x)
        self.y = float(y)
        
    def set_rotation(self, rotation: float) -> None:
        """Set player rotation.
        
        Args:
            rotation: New rotation in degrees
        """
        self.rotation = float(rotation)
        self._update_trig_cache()
        
    def _update_trig_cache(self) -> None:
        """Cache trigonometric calculations for performance."""
        rad = math.radians(self.rotation)
        self._cos_cache = math.cos(rad)
        self._sin_cache = math.sin(rad)
        
    def move(self, dx: float, dy: float) -> None:
        """Move player by delta amounts.
        
        Args:
            dx: Change in x position
            dy: Change in y position
        """
        self.x += float(dx)
        self.y += float(dy)
        
    def rotate(self, degrees: float) -> None:
        """Rotate player by degrees.
        
        Args:
            degrees: Rotation amount in degrees
        """
        self.rotation = (self.rotation + float(degrees)) % 360.0
        self._update_trig_cache()
        
    def rotate_from_mouse(self, dx: float) -> None:
        """Rotate player based on mouse movement.
        
        Args:
            dx: Mouse movement delta
        """
        self.rotate(dx * settings.player.mouse_sensitivity)
        
    def move_forward(self, dt: float, game_map: 'Map') -> None:
        """Move player forward in the direction they're facing.
        
        Args:
            dt: Delta time in seconds
            game_map: The game map to check collisions against
        """
        dx = self._cos_cache * settings.player.move_speed * dt
        dy = self._sin_cache * settings.player.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
    def move_backward(self, dt: float, game_map: 'Map') -> None:
        """Move player backward.
        
        Args:
            dt: Delta time in seconds
            game_map: The game map to check collisions against
        """
        dx = -self._cos_cache * settings.player.move_speed * dt
        dy = -self._sin_cache * settings.player.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
    def strafe_left(self, dt: float, game_map: 'Map') -> None:
        """Strafe left perpendicular to facing direction.
        
        Args:
            dt: Delta time in seconds
            game_map: The game map to check collisions against
        """
        dx = self._sin_cache * settings.player.move_speed * dt
        dy = -self._cos_cache * settings.player.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
    def strafe_right(self, dt: float, game_map: 'Map') -> None:
        """Strafe right perpendicular to facing direction.
        
        Args:
            dt: Delta time in seconds
            game_map: The game map to check collisions against
        """
        dx = -self._sin_cache * settings.player.move_speed * dt
        dy = self._cos_cache * settings.player.move_speed * dt
        self._move_with_collision(dx, dy, game_map)
        
    def look_left(self, dt: float) -> None:
        """Rotate player left.
        
        Args:
            dt: Delta time in seconds
        """
        self.rotate(-settings.player.rotation_speed * dt)
        
    def look_right(self, dt: float) -> None:
        """Rotate player right.
        
        Args:
            dt: Delta time in seconds
        """
        self.rotate(settings.player.rotation_speed * dt)
    
    def update_bobbing(self, dt: float) -> None:
        """Update view bobbing for walking animation effect.
        
        Args:
            dt: Delta time in seconds
        """
        if self.is_moving:
            self.bob_phase += settings.player.bob_frequency * dt
            if self.bob_phase > 2 * math.pi * 100:
                self.bob_phase = 0
            
            self.bob_offset_y = (
                math.sin(self.bob_phase * 2 * math.pi) * 
                settings.player.bob_amplitude
            )
        else:
            if abs(self.bob_offset_y) > 0.1:
                self.bob_offset_y *= 0.8
            else:
                self.bob_offset_y = 0.0
                self.bob_phase = 0.0


class Map:
    """Tile-based map where each cell can be empty (0) or a wall (1+)."""
    
    def __init__(self, grid: List[List[int]], player_start: Tuple[float, float] = (2.0, 2.0)) -> None:
        """Initialize the map.
        
        Args:
            grid: 2D list representing the map tiles
            player_start: Starting position for the player
        """
        self.grid: List[List[int]] = grid
        self.width: int = len(grid[0])
        self.height: int = len(grid)
        self.tile_size: int = settings.map.tile_size
        self.player_start: Tuple[float, float] = player_start

    @staticmethod
    def load_from_file(filename: str) -> 'Map':
        """Load map from text file.
        
        Args:
            filename: Path to the map file
            
        Returns:
            Loaded Map instance
            
        Raises:
            SystemExit: If map file is not found
        """
        grid: List[List[int]] = []
        player_start: Tuple[float, float] = (2.0, 2.0)
        
        try:
            with open(filename, 'r') as file:
                for y, line in enumerate(file):
                    row: List[int] = []
                    for x, char in enumerate(line.strip()):
                        if char.isdigit():
                            row.append(int(char))
                        elif char.upper() == 'P':
                            player_start = (float(x), float(y))
                            row.append(0)
                    if row:
                        grid.append(row)
            return Map(grid, player_start)
        except FileNotFoundError:
            print(f"Error: map file '{filename}' not found.")
            sys.exit(1)
        
    def is_wall(self, x: float, y: float) -> bool:
        """Check if given world coordinates contain a wall.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position contains a wall, False otherwise
        """
        map_x = int(x)
        map_y = int(y)
        
        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return True
            
        return self.grid[map_y][map_x] > 0
        
    def get_tile(self, x: float, y: float) -> int:
        """Get tile type at given world coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tile type ID
        """
        map_x = int(x)
        map_y = int(y)
        
        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return 1
            
        return self.grid[map_y][map_x]


class Raycaster:
    """Handles 3D rendering using raycasting technique."""
    
    def __init__(self, screen_width: int, screen_height: int, asset_manager: AssetManager) -> None:
        """Initialize the raycaster.
        
        Args:
            screen_width: Width of the screen in pixels
            screen_height: Height of the screen in pixels
            asset_manager: AssetManager instance for texture access
        """
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.asset_manager: AssetManager = asset_manager
        
        self.fov: float = settings.render.fov
        self.max_depth: float = settings.render.max_depth
        
        self.num_rays: int = screen_width // settings.render.ray_resolution_divisor
        self.ray_width: float = self.screen_width / self.num_rays
        
        self.floor_scale: int = settings.render.floor_scale
        self.floor_width: int = screen_width // self.floor_scale
        self.floor_height: int = screen_height // self.floor_scale
        
        self.wall_buffer: List = []
        
    def cast_ray(
        self, 
        player: Player, 
        game_map: Map, 
        angle: float
    ) -> Tuple[float, int, float, float, int]:
        """Cast a single ray using DDA algorithm.
        
        Args:
            player: The player object
            game_map: The game map
            angle: Ray angle in degrees
            
        Returns:
            Tuple of (distance, side, ray_dx, ray_dy, hit_value)
        """
        rad = math.radians(angle)
        ray_dx = math.cos(rad)
        ray_dy = math.sin(rad)
        
        x = player.x
        y = player.y
        
        map_x = int(x)
        map_y = int(y)
        
        try:
            delta_dist_x = abs(1 / ray_dx) if ray_dx != 0 else float('inf')
            delta_dist_y = abs(1 / ray_dy) if ray_dy != 0 else float('inf')
        except ZeroDivisionError:
            delta_dist_x = float('inf')
            delta_dist_y = float('inf')
        
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
        
        hit = False
        hit_val = 0
        side = 0
        max_iterations = 50
        iterations = 0
        
        while not hit and iterations < max_iterations:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            iterations += 1
            
            tile = game_map.get_tile(map_x, map_y)
            if tile > 0:
                hit = True
                hit_val = tile
        
        if side == 0:
            distance = (
                (map_x - x + (1 - step_x) / 2) / ray_dx 
                if ray_dx != 0 else self.max_depth
            )
        else:
            distance = (
                (map_y - y + (1 - step_y) / 2) / ray_dy 
                if ray_dy != 0 else self.max_depth
            )
        
        distance = abs(distance)
        
        if distance > self.max_depth or distance < 0:
            distance = self.max_depth
            
        return distance, side, ray_dx, ray_dy, hit_val
        
    def render_floor_ceiling_vectorized(
        self, 
        screen: pygame.Surface, 
        player: Player, 
        game_map: Map
    ) -> None:
        """Render floor and ceiling using vectorized NumPy operations.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map
        """
        half_fov_rad = math.radians(self.fov / 2)
        tan_half_fov = math.tan(half_fov_rad)
        aspect_ratio = self.screen_width / self.screen_height
        screen_half = self.screen_height / 2 + player.bob_offset_y
        
        floor_texture = self.asset_manager.get_floor_texture()
        ceiling_texture = self.asset_manager.get_ceiling_texture()
        floor_array = self.asset_manager.get_floor_array()
        ceiling_array = self.asset_manager.get_ceiling_array()
        
        floor_tex_width = floor_texture.get_width()
        floor_tex_height = floor_texture.get_height()
        ceiling_tex_width = ceiling_texture.get_width()
        ceiling_tex_height = ceiling_texture.get_height()
        
        player_cos = math.cos(math.radians(player.rotation))
        player_sin = math.sin(math.radians(player.rotation))
        
        plane_x = -player_sin * tan_half_fov * aspect_ratio
        plane_y = player_cos * tan_half_fov * aspect_ratio
        
        buffer_surf = pygame.Surface((self.floor_width, self.floor_height))
        buffer_pixels = pygame.surfarray.pixels3d(buffer_surf)
        
        x_coords, y_coords = np.meshgrid(
            np.arange(self.floor_width, dtype=np.float32),
            np.arange(self.floor_height, dtype=np.float32),
            indexing='xy'
        )
        
        screen_y_coords = y_coords * self.floor_scale
        p = screen_y_coords - screen_half
        
        epsilon = 1.0
        p_safe = np.where(np.abs(p) < epsilon, np.sign(p) * epsilon, p)
        
        pos_z = 0.5 * self.screen_height
        row_distance = pos_z / np.abs(p_safe)
        
        screen_x_norm = (2.0 * x_coords / self.floor_width) - 1.0
        ray_dir_x = player_cos + plane_x * screen_x_norm
        ray_dir_y = player_sin + plane_y * screen_x_norm
        
        world_x = player.x + ray_dir_x * row_distance
        world_y = player.y + ray_dir_y * row_distance
        
        fog_distance = settings.fog.base_fog_distance
        fog_factor = np.clip(row_distance / fog_distance, 0.0, 1.0)
        floor_fog = 1.0 - fog_factor * settings.fog.floor_fog_intensity
        ceiling_fog = 1.0 - fog_factor * settings.fog.ceiling_fog_intensity
        
        floor_mask = p > epsilon
        ceiling_mask = p < -epsilon
        
        if np.any(floor_mask):
            tex_x = (world_x * floor_tex_width).astype(np.int32) % floor_tex_width
            tex_y = (world_y * floor_tex_height).astype(np.int32) % floor_tex_height
            
            colors = floor_array[tex_x[floor_mask], tex_y[floor_mask]]
            fog_values = floor_fog[floor_mask]
            colors_fogged = (colors * fog_values[:, np.newaxis]).astype(np.uint8)
            
            x_indices = x_coords[floor_mask].astype(np.int32)
            y_indices = y_coords[floor_mask].astype(np.int32)
            buffer_pixels[x_indices, y_indices] = colors_fogged

        if np.any(ceiling_mask):
            tex_x = (world_x * ceiling_tex_width).astype(np.int32) % ceiling_tex_width
            tex_y = (world_y * ceiling_tex_height).astype(np.int32) % ceiling_tex_height
            
            colors = ceiling_array[tex_x[ceiling_mask], tex_y[ceiling_mask]]
            fog_values = ceiling_fog[ceiling_mask]
            colors_fogged = (colors * fog_values[:, np.newaxis]).astype(np.uint8)
            
            x_indices = x_coords[ceiling_mask].astype(np.int32)
            y_indices = y_coords[ceiling_mask].astype(np.int32)
            buffer_pixels[x_indices, y_indices] = colors_fogged

        del buffer_pixels
        
        scaled_surf = pygame.transform.scale(
            buffer_surf, 
            (self.screen_width, self.screen_height)
        )
        screen.blit(scaled_surf, (0, 0))
        
    def render_3d_view(self, screen: pygame.Surface, player: Player, game_map: Map) -> None:
        """Render the complete 3D view.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map
        """
        half_fov_rad = math.radians(self.fov / 2)
        tan_half_fov = math.tan(half_fov_rad)
        aspect_ratio = self.screen_width / self.screen_height
        screen_half = self.screen_height / 2 + player.bob_offset_y
        
        self.render_floor_ceiling_vectorized(screen, player, game_map)
        
        for ray_index in range(self.num_rays):
            screen_x = (2 * ray_index) / self.num_rays - 1
            angle_offset_rad = math.atan(screen_x * tan_half_fov * aspect_ratio)
            angle_offset_deg = math.degrees(angle_offset_rad)
            
            ray_angle = player.rotation + angle_offset_deg
            distance, side, ray_dx, ray_dy, hit_val = self.cast_ray(
                player, game_map, ray_angle
            )
                        
            raw_distance = distance 
            distance *= math.cos(angle_offset_rad)
            
            if distance < 0.01:
                distance = 0.01
                
            wall_height = int(self.screen_height / distance)
            wall_top = int(screen_half - (wall_height / 2))
            
            current_texture = self.asset_manager.get_wall_texture(hit_val)
            cur_tex_width = current_texture.get_width()
            cur_tex_height = current_texture.get_height()
            
            if side == 0:
                wall_x = player.y + raw_distance * ray_dy
            else:
                wall_x = player.x + raw_distance * ray_dx
            
            wall_x -= math.floor(wall_x)
            tex_x = int(wall_x * cur_tex_width)
            
            if side == 0 and ray_dx > 0:
                tex_x = cur_tex_width - tex_x - 1
            if side == 1 and ray_dy < 0:
                tex_x = cur_tex_width - tex_x - 1
                
            tex_x = max(0, min(tex_x, cur_tex_width - 1))
            tex_strip = current_texture.subsurface((tex_x, 0, 1, cur_tex_height))
            render_width = int(self.ray_width) + 1 
            
            if wall_height > 0 and wall_height < 8000:
                scaled_strip = pygame.transform.scale(
                    tex_strip, 
                    (render_width, wall_height)
                )
                
                fog_intensity = min(1.0, distance / settings.fog.base_fog_distance)
                base_fog_alpha = int(
                    fog_intensity * settings.fog.base_fog_intensity * 255
                )
                side_alpha = settings.fog.side_darkening_alpha if side == 1 else 0
                total_alpha = min(255, base_fog_alpha + side_alpha)
                
                if total_alpha > 0:
                    fog_surface = pygame.Surface((render_width, wall_height))
                    fog_surface.set_alpha(total_alpha)
                    fog_surface.fill(settings.colors.black)
                    scaled_strip.blit(fog_surface, (0, 0))

                screen.blit(scaled_strip, (ray_index * self.ray_width, wall_top))

    def render_minimap(self, screen: pygame.Surface, player: Player, game_map: Map) -> None:
        """Render 2D minimap overlay.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map
        """
        minimap_size = settings.minimap.size
        minimap_scale = minimap_size / max(game_map.width, game_map.height)
        minimap_x = screen.get_width() - minimap_size - settings.minimap.margin
        minimap_y = settings.minimap.margin
        
        pygame.draw.rect(
            screen, 
            settings.colors.minimap_background,
            (minimap_x, minimap_y, minimap_size, minimap_size)
        )
        
        for y in range(game_map.height):
            for x in range(game_map.width):
                tile = game_map.grid[y][x]
                if tile > 0:
                    tile_x = minimap_x + x * minimap_scale
                    tile_y = minimap_y + y * minimap_scale
                    
                    color = settings.colors.minimap_wall_default
                    if tile == 2:
                        color = settings.colors.minimap_wall_type2
                    if tile == 3:
                        color = settings.colors.minimap_wall_type3
                    
                    pygame.draw.rect(
                        screen, 
                        color,
                        (tile_x, tile_y, minimap_scale, minimap_scale)
                    )
        
        player_x = minimap_x + player.x * minimap_scale
        player_y = minimap_y + player.y * minimap_scale
        pygame.draw.circle(
            screen, 
            settings.colors.minimap_player,
            (int(player_x), int(player_y)), 
            settings.minimap.player_dot_radius
        )
        
        rad = math.radians(player.rotation)
        end_x = player_x + math.cos(rad) * settings.minimap.direction_line_length
        end_y = player_y + math.sin(rad) * settings.minimap.direction_line_length
        pygame.draw.line(
            screen, 
            settings.colors.minimap_player,
            (player_x, player_y), 
            (end_x, end_y), 
            settings.minimap.direction_line_width
        )


class Game:
    """Main game class handling initialization, game loop, and events."""
    
    def __init__(self) -> None:
        """Initialize the game."""
        pygame.init()
        
        self.screen_width: int = settings.display.width
        self.screen_height: int = settings.display.height
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption(settings.display.title)
        
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.fps: int = settings.display.fps
        
        self.running: bool = True
        self.paused: bool = False
        
        self.show_fps: bool = settings.show_fps
        
        self.last_mouse_pos: Optional[Tuple[int, int]] = None
        
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        
        self.game_map: Map = Map.load_from_file(settings.map.default_map_file)
        
        start_x, start_y = self.game_map.player_start
        self.player: Player = Player(start_x, start_y, 0.0)
        
        self.asset_manager: AssetManager = AssetManager()
        self.raycaster: Raycaster = Raycaster(
            self.screen_width, 
            self.screen_height,
            self.asset_manager
        )
        
        self.font: pygame.font.Font = pygame.font.Font(None, 36)
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        pygame.mouse.set_pos(center_x, center_y)
        self.last_mouse_pos = (center_x, center_y)

    def handle_events(self) -> None:
        """Handle all pygame events."""
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
                
    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle key press events.
        
        Args:
            event: The pygame key event
        """
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
                pygame.mouse.get_rel()

    def handle_keyup(self, event: pygame.event.Event) -> None:
        """Handle key release events.
        
        Args:
            event: The pygame key event
        """
        pass
        
    def handle_mouse_click(self, event: pygame.event.Event) -> None:
        """Handle mouse click events.
        
        Args:
            event: The pygame mouse event
        """
        pass
        
    def handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Handle mouse motion events.
        
        Args:
            event: The pygame mouse event
        """
        if not self.paused:
            dx, dy = pygame.mouse.get_rel()
            
            if dx != 0:
                self.player.rotate_from_mouse(dx)

    def handle_player_input(self, dt: float) -> None:
        """Process continuous keyboard input for smooth movement.
        
        Args:
            dt: Delta time in seconds
        """
        keys = pygame.key.get_pressed()
        
        total_dx = 0.0
        total_dy = 0.0
        
        move_speed = settings.player.move_speed * dt
        
        if keys[K_w]:
            total_dx += self.player._cos_cache * move_speed
            total_dy += self.player._sin_cache * move_speed
            
        if keys[K_s]:
            total_dx += -self.player._cos_cache * move_speed
            total_dy += -self.player._sin_cache * move_speed
            
        if keys[K_a]:
            total_dx += self.player._sin_cache * move_speed
            total_dy += -self.player._cos_cache * move_speed
            
        if keys[K_d]:
            total_dx += -self.player._sin_cache * move_speed
            total_dy += self.player._cos_cache * move_speed

        self.player.is_moving = (keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d])

        if self.player.is_moving:
            current_speed = math.sqrt(total_dx**2 + total_dy**2)
            if current_speed > move_speed:
                scale = move_speed / current_speed
                total_dx *= scale
                total_dy *= scale

        if total_dx != 0 or total_dy != 0:
            self.player._move_with_collision(total_dx, total_dy, self.game_map)
            
        if keys[K_LEFT]:
            self.player.look_left(dt)
        if keys[K_RIGHT]:
            self.player.look_right(dt)

    def update(self, dt: float) -> None:
        """Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.paused:
            self.handle_player_input(dt)
            self.player.update_bobbing(dt)
            
    def render(self) -> None:
        """Render everything to the screen."""
        self.screen.fill(settings.colors.black)
        
        self.raycaster.render_3d_view(self.screen, self.player, self.game_map)
        self.raycaster.render_minimap(self.screen, self.player, self.game_map)
        
        if self.show_fps:
            fps_text = self.font.render(
                f"FPS: {int(self.clock.get_fps())}", 
                True, 
                settings.colors.green
            )
            self.screen.blit(fps_text, (10, 10))
        
        pygame.display.flip()
        
    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
            
        self.quit()
        
    def quit(self) -> None:
        """Clean up and quit."""
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
