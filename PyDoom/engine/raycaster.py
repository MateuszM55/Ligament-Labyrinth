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
        
        self.floor_scale: int = settings.render.floor_ceiling_ray_resolution_divisor
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
            settings.render.wall_height_factor,
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
            settings.render.wall_height_factor,
            settings.lighting.enable_inverse_square,
            settings.lighting.light_intensity,
            settings.lighting.ambient_light,
            settings.lighting.enable_vignette,
            settings.lighting.vignette_intensity,
            settings.lighting.vignette_radius
        )
        
        del screen_pixels
        
        self.render_sprites(screen, player, game_map)
    
    def render_sprites(self, screen: pygame.Surface, player: Player, game_map: Map) -> None:
        """Render all sprites (monsters) in the scene.
        
        Args:
            screen: Pygame surface to render to
            player: The player object
            game_map: The game map containing monsters
        """
        if not game_map.monsters:
            return
        
        sprite_data = []
        for monster in game_map.monsters:
            distance = monster.get_distance_to_player(player)
            
            if distance < 0.1 or distance > self.max_depth:
                continue
            
            sprite_data.append((distance, monster))
        
        sprite_data.sort(key=lambda x: x[0], reverse=True)
        
        player_rad = math.radians(player.rotation)
        player_cos = math.cos(player_rad)
        player_sin = math.sin(player_rad)
        
        half_fov = math.radians(self.fov / 2.0)
        tan_half_fov = math.tan(half_fov)
        aspect_ratio = self.screen_width / self.screen_height
        
        for distance, monster in sprite_data:
            dx = monster.x - player.x
            dy = monster.y - player.y
            
            sprite_y = dx * player_cos + dy * player_sin
            sprite_x = dy * player_cos - dx * player_sin
            
            if sprite_y <= 0.1:
                continue
            
            projection_plane_x = (sprite_x / sprite_y) / (tan_half_fov * aspect_ratio)
            screen_x = int((self.screen_width / 2.0) * (1.0 + projection_plane_x))
            
            sprite_height = int(self.screen_height / sprite_y * settings.render.wall_height_factor)
            sprite_width = sprite_height
            
            draw_start_y = int((self.screen_height - sprite_height) / 2 + player.bob_offset_y)
            draw_start_x = int(screen_x - sprite_width / 2)
            
            sprite_texture = self.asset_manager.get_sprite_texture(monster.texture_id)
            if sprite_texture is None:
                continue
            
            if sprite_width > 0 and sprite_height > 0:
                scaled_sprite = pygame.transform.scale(sprite_texture, (sprite_width, sprite_height))
                
                light_factor = 1.0
                if settings.lighting.enable_inverse_square:
                    light_factor = min(1.0, settings.lighting.light_intensity / (distance * distance + 0.1))
                    light_factor = max(settings.lighting.ambient_light, light_factor)
                
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
        
        for monster in game_map.monsters:
            monster_x = minimap_x + monster.x * minimap_scale
            monster_y = minimap_y + monster.y * minimap_scale
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
