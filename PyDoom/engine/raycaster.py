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
    render_walls_numba,
    process_sprites_numba
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
        
        self.floor_scale: int = settings.render.floor_ceiling_ray_resolution_divisor
        self.floor_width: int = screen_width // self.floor_scale
        self.floor_height: int = screen_height // self.floor_scale
        
    def render_floor_ceiling_vectorized(
        self, 
        screen: pygame.Surface, 
        player: Player, 
        game_map: Map,
        glitch_intensity: float = 0.0
    ) -> None:
        """Render floor and ceiling using Numba-optimized operations.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map
            glitch_intensity: Dynamic glitch effect intensity
        """
        floor_arrays = self.asset_manager.get_floor_arrays()
        ceiling_arrays = self.asset_manager.get_ceiling_arrays()
        
        buffer_surf = pygame.Surface((self.floor_width, self.floor_height))
        buffer_pixels = pygame.surfarray.pixels3d(buffer_surf)
        
        render_floor_ceiling_numba(
            buffer_pixels,
            floor_arrays,
            ceiling_arrays,
            game_map.floor_grid_array,
            game_map.ceiling_grid_array,
            game_map.width,
            game_map.height,
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
            settings.render.wall_height_factor,
            settings.lighting.enable_inverse_square,
            settings.lighting.light_intensity,
            settings.lighting.ambient_light,
            settings.lighting.enable_vignette,
            settings.lighting.vignette_intensity,
            settings.lighting.vignette_radius,
            glitch_intensity  # Use dynamic glitch intensity
        )
        
        del buffer_pixels
        
        scaled_surf = pygame.transform.scale(
            buffer_surf, 
            (self.screen_width, self.screen_height)
        )
        screen.blit(scaled_surf, (0, 0))
                  
    def render_3d_view_numba(self, screen: pygame.Surface, player: Player, game_map: Map, glitch_intensity: float = 0.0) -> None:
        """Render the complete 3D view using Numba optimization for walls.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map
            glitch_intensity: Dynamic glitch effect intensity
        """
        self.render_floor_ceiling_vectorized(screen, player, game_map, glitch_intensity)
        
        screen_pixels = pygame.surfarray.pixels3d(screen)
        
        texture_arrays = self.asset_manager.get_wall_texture_arrays()
        texture_map = self.asset_manager.get_texture_map()
        
        depth_buffer = render_walls_numba(
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
            settings.render.wall_height_factor,
            settings.lighting.enable_inverse_square,
            settings.lighting.light_intensity,
            settings.lighting.ambient_light,
            settings.lighting.enable_vignette,
            settings.lighting.vignette_intensity,
            settings.lighting.vignette_radius,
            glitch_intensity  # Use dynamic glitch intensity
        )
        
        del screen_pixels
        
        self.render_sprites(screen, player, game_map, depth_buffer)
    
    def render_sprites(self, screen: pygame.Surface, player: Player, game_map: Map, depth_buffer: np.ndarray) -> None:
        """Render all sprites (monsters) in the scene using Numba optimization with depth buffer occlusion for collectibles.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map containing sprite data
            depth_buffer: Array of wall distances for occlusion testing
        """
        if game_map.sprite_data.shape[0] == 0:
            return
        
        processed_sprites = process_sprites_numba(
            game_map.sprite_data,
            player.x,
            player.y,
            player.rotation,
            self.fov,
            self.screen_width,
            self.screen_height,
            self.max_depth,
            settings.render.wall_height_factor,
            player.bob_offset_y,
            settings.lighting.enable_inverse_square,
            settings.lighting.light_intensity,
            settings.lighting.ambient_light,
            depth_buffer,
            settings.collectible.texture_ids
        )
        
        for i in range(processed_sprites.shape[0]):
            screen_x = int(processed_sprites[i, 0])
            sprite_height = int(processed_sprites[i, 1])
            sprite_width = int(processed_sprites[i, 2])
            distance = processed_sprites[i, 3]
            texture_id = int(processed_sprites[i, 4])
            light_factor = processed_sprites[i, 5]
            
            draw_start_y = int((self.screen_height - sprite_height) / 2 + player.bob_offset_y)
            draw_start_x = int(screen_x - sprite_width / 2)
            
            sprite_texture = self.asset_manager.get_sprite_texture(texture_id)
            if sprite_texture is None:
                continue
            
            if sprite_width > 0 and sprite_height > 0:
                scaled_sprite = pygame.transform.scale(sprite_texture, (sprite_width, sprite_height))
                
                if light_factor < 1.0:
                    dark_surface = pygame.Surface(scaled_sprite.get_size(), pygame.SRCALPHA)
                    dark_surface.fill((0, 0, 0, int(255 * (1.0 - light_factor))))
                    scaled_sprite.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
                
                screen.blit(scaled_sprite, (draw_start_x, draw_start_y))

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
        
        for i in range(game_map.sprite_data.shape[0]):
            sprite_x_world = game_map.sprite_data[i, 0]
            sprite_y_world = game_map.sprite_data[i, 1]
            monster_x = minimap_x + sprite_x_world * minimap_scale
            monster_y = minimap_y + sprite_y_world * minimap_scale
            pygame.draw.circle(
                screen,
                (255, 100, 100),
                (int(monster_x), int(monster_y)),
                3
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
