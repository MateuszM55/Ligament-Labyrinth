"""Raycasting rendering engine."""

import math
import pygame
import numpy as np

from settings import settings
from engine.assets import AssetManager
from world.player import Player
from world.map import Map
from engine.numba_kernels import (
    render_floor_ceiling_numba, 
    render_walls_numba
)


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
        
        self.num_rays: int = screen_width // settings.render.wall_ray_resolution_divisor
        self.ray_width: float = self.screen_width / self.num_rays
        
        self.floor_scale: int = settings.render.floor_and_ceiling_scale
        self.floor_width: int = screen_width // self.floor_scale
        self.floor_height: int = screen_height // self.floor_scale
        
    def render_floor_ceiling_vectorized(
        self, 
        screen: pygame.Surface, 
        player: Player, 
        game_map: Map
    ) -> None:
        """Render floor and ceiling using Numba-optimized operations.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map
        """
        floor_array = self.asset_manager.get_floor_array()
        ceiling_array = self.asset_manager.get_ceiling_array()
        
        buffer_surf = pygame.Surface((self.floor_width, self.floor_height))
        buffer_pixels = pygame.surfarray.pixels3d(buffer_surf)
        
        render_floor_ceiling_numba(
            buffer_pixels,
            floor_array,
            ceiling_array,
            self.floor_width,
            self.floor_height,
            self.floor_scale,
            self.screen_width,
            self.screen_height,
            player.x,
            player.y,
            math.radians(player.rotation),
            math.radians(self.fov),
            player.bob_offset_y,
            settings.lighting.enable_inverse_square,
            settings.lighting.light_intensity,
            settings.lighting.ambient_light,
            settings.lighting.enable_vignette,
            settings.lighting.vignette_intensity,
            settings.lighting.vignette_radius
        )
        
        del buffer_pixels
        
        scaled_surf = pygame.transform.scale(
            buffer_surf, 
            (self.screen_width, self.screen_height)
        )
        screen.blit(scaled_surf, (0, 0))
                  
    def render_3d_view_numba(self, screen: pygame.Surface, player: Player, game_map: Map) -> None:
        """Render the complete 3D view using Numba optimization for walls.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map
        """
        self.render_floor_ceiling_vectorized(screen, player, game_map)
        
        screen_pixels = pygame.surfarray.pixels3d(screen)
        
        texture_arrays = self.asset_manager.get_wall_texture_arrays()
        texture_map = self.asset_manager.get_texture_map()
        
        render_walls_numba(
            screen_pixels,
            texture_arrays,
            texture_map,
            player.x,
            player.y,
            player.rotation,
            game_map.grid_array,
            game_map.width,
            game_map.height,
            self.screen_width,
            self.screen_height,
            self.fov,
            self.max_depth,
            self.num_rays,
            self.ray_width,
            player.bob_offset_y,
            settings.lighting.enable_flashlight,
            settings.lighting.flashlight_radius,
            settings.lighting.flashlight_intensity,
            settings.lighting.flashlight_sharpness,
            settings.lighting.enable_inverse_square,
            settings.lighting.light_intensity,
            settings.lighting.ambient_light,
            settings.lighting.enable_vignette,
            settings.lighting.vignette_intensity,
            settings.lighting.vignette_radius
        )
        
        del screen_pixels

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
