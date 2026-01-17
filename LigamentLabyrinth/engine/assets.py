"""Asset management for textures and resources."""

import os
import re
from typing import Dict, Optional, Tuple
import pygame
import numpy as np

from settings import settings


class AssetManager:
    """Manages loading and caching of game textures and assets."""
    
    def __init__(self) -> None:
        """Initialize the asset manager and load all textures."""
        self.textures: Dict[int, pygame.Surface] = {}
        self.sprite_textures: Dict[int, pygame.Surface] = {}
        
        self.floor_textures: Dict[int, np.ndarray] = {}
        self.ceiling_textures: Dict[int, np.ndarray] = {}
        
        self.tex_width: int = settings.assets.texture_size
        self.tex_height: int = settings.assets.texture_size
        
        self._load_all_textures()
        self._convert_textures_to_arrays()
    
    def _generate_checkerboard_texture(
        self,
        size: int,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int]
    ) -> pygame.Surface:
        """Generate a simple checkerboard pattern texture."""
        surface = pygame.Surface((size, size))
        surface.fill(color1)
        pygame.draw.rect(surface, color2, (0, 0, size // 2, size // 2))
        pygame.draw.rect(surface, color2, (size // 2, size // 2, size // 2, size // 2))
        return surface
    
    def _ensure_power_of_two_size(self, surface: pygame.Surface, target_size: int) -> pygame.Surface:
        """Ensure texture is power-of-2 size for optimal Numba performance."""
        width, height = surface.get_size()
        if width != target_size or height != target_size:
            return pygame.transform.scale(surface, (target_size, target_size))
        return surface
    
    def _load_textures_from_directory(self) -> None:
        """Load all textures from the texture directory."""
        texture_dir = settings.assets.texture_directory
        texture_size = settings.assets.texture_size
        
        if not os.path.exists(texture_dir):
            print(f"Warning: Texture directory '{texture_dir}' not found.")
            return
        
        # Regex to find the ID specifically at the end of the filename (e.g., "wall_1.png")
        # This prevents matching "512" in "wall_512x512_1.png"
        id_pattern = re.compile(r'(\d+)\.[a-zA-Z0-9]+$')

        for filename in os.listdir(texture_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                continue
            
            full_path = os.path.join(texture_dir, filename)
            match = id_pattern.search(filename)
            
            if not match:
                continue

            try:
                tex_id = int(match.group(1))
                img = pygame.image.load(full_path)
                
                # Normalize texture immediately
                if "sprite" in filename.lower():
                    surface = self._ensure_power_of_two_size(img.convert_alpha(), texture_size)
                    self.sprite_textures[tex_id] = surface
                
                elif "floor" in filename.lower():
                    surface = self._ensure_power_of_two_size(img.convert(), texture_size)
                    self.floor_textures[tex_id] = pygame.surfarray.array3d(surface)
                    
                elif "ceiling" in filename.lower():
                    surface = self._ensure_power_of_two_size(img.convert(), texture_size)
                    self.ceiling_textures[tex_id] = pygame.surfarray.array3d(surface)
                    
                else:
                    # Wall texture
                    surface = self._ensure_power_of_two_size(img.convert(), texture_size)
                    self.textures[tex_id] = surface
                    
                print(f"Loaded {filename} as ID {tex_id}")

            except (pygame.error, ValueError) as e:
                print(f"Failed to load {filename}: {e}")

    def _generate_fallback_textures(self) -> None:
        """Generate fallback textures for any missing wall textures based on Settings."""
        texture_size = settings.assets.texture_size
        
        # Pulls directly from the dataclass default_factory we fixed in settings.py
        for tex_id, colors in settings.assets.default_texture_colors.items():
            if tex_id not in self.textures:
                self.textures[tex_id] = self._generate_checkerboard_texture(
                    texture_size, colors[0], colors[1]
                )
                print(f"Generated fallback texture for ID {tex_id}")
    
    def _generate_fallback_floor_ceiling(self) -> None:
        """Generate fallback floor and ceiling textures using the ColorPalette."""
        texture_size = settings.assets.texture_size
        colors = settings.colors

        # ID 0 uses the primary palette defined in settings
        if 0 not in self.floor_textures:
            surf = self._generate_checkerboard_texture(
                texture_size, colors.floor_primary, colors.floor_secondary
            )
            self.floor_textures[0] = pygame.surfarray.array3d(surf)
            print("Generated fallback floor (ID 0)")
        
        if 0 not in self.ceiling_textures:
            surf = self._generate_checkerboard_texture(
                texture_size, colors.ceiling_primary, colors.ceiling_secondary
            )
            self.ceiling_textures[0] = pygame.surfarray.array3d(surf)
            print("Generated fallback ceiling (ID 0)")

    def _generate_fallback_sprites(self) -> None:
        """Generate fallback sprite textures using the ColorPalette."""
        texture_size = settings.assets.texture_size
        
        if 0 not in self.sprite_textures:
            sprite_surface = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
            sprite_surface.fill((0, 0, 0, 0))
            
            # Use palette colors for the fallback sprite
            pygame.draw.circle(
                sprite_surface,
                settings.colors.red,
                (texture_size // 2, texture_size // 2 - texture_size // 8),
                texture_size // 8
            )
            
            pygame.draw.circle(
                sprite_surface,
                settings.colors.red,
                (texture_size // 2, texture_size // 2 + texture_size // 8),
                texture_size // 4
            )
            
            pygame.draw.circle(
                sprite_surface,
                settings.colors.black,
                (texture_size // 2 - texture_size // 8, texture_size // 2 - texture_size // 8),
                texture_size // 16
            )
            
            pygame.draw.circle(
                sprite_surface,
                settings.colors.black,
                (texture_size // 2 + texture_size // 8, texture_size // 2 - texture_size // 8),
                texture_size // 16
            )
            
            self.sprite_textures[0] = sprite_surface
            print("Generated fallback sprite texture")
    
    def _load_all_textures(self) -> None:
        """Load all textures from files and generate fallbacks."""
        self._load_textures_from_directory()
        self._generate_fallback_textures()
        self._generate_fallback_floor_ceiling()
        self._generate_fallback_sprites()
        
        # Ensure we have dimensions set even if only fallbacks exist
        if self.textures:
            first_tex = next(iter(self.textures.values()))
            self.tex_width = first_tex.get_width()
            self.tex_height = first_tex.get_height()
    
    def _convert_textures_to_arrays(self) -> None:
        """Convert wall textures to NumPy arrays for fast access."""
        self._prepare_wall_texture_arrays()
        self._prepare_floor_ceiling_arrays()
    
    def get_floor_arrays(self) -> np.ndarray:
        return self.floor_texture_arrays
    
    def get_ceiling_arrays(self) -> np.ndarray:
        return self.ceiling_texture_arrays
    
    def get_sprite_texture(self, sprite_id: int) -> Optional[pygame.Surface]:
        return self.sprite_textures.get(sprite_id, self.sprite_textures.get(0))
    
    def _prepare_wall_texture_arrays(self) -> None:
        """Prepare wall textures as a single NumPy array for numba optimization."""
        if not self.textures:
            self.wall_texture_arrays = np.zeros((1, self.tex_width, self.tex_height, 3), dtype=np.uint8)
            self.texture_map = np.zeros(1, dtype=np.int32)
            return
        
        max_tex_id = max(self.textures.keys())
        num_textures = max_tex_id + 1
        
        self.wall_texture_arrays = np.zeros(
            (num_textures, self.tex_width, self.tex_height, 3),
            dtype=np.uint8
        )
        
        self.texture_map = np.zeros(num_textures, dtype=np.int32)
        
        for tex_id, texture in self.textures.items():
            self.wall_texture_arrays[tex_id] = pygame.surfarray.array3d(texture)
            self.texture_map[tex_id] = tex_id
    
    def _prepare_floor_ceiling_arrays(self) -> None:
        """Prepare floor and ceiling textures as NumPy arrays for numba optimization."""
        # Helper to pack a dictionary of surfaces/arrays into a single 4D array
        def pack_textures(texture_dict: Dict[int, np.ndarray]) -> np.ndarray:
            if not texture_dict:
                return np.zeros((1, self.tex_width, self.tex_height, 3), dtype=np.uint8)
            
            max_id = max(texture_dict.keys())
            # Use first texture to determine dimensions
            first = next(iter(texture_dict.values()))
            w, h = first.shape[:2]
            
            arr = np.zeros((max_id + 1, w, h, 3), dtype=np.uint8)
            for tid, tdata in texture_dict.items():
                arr[tid] = tdata
            return arr

        self.floor_texture_arrays = pack_textures(self.floor_textures)
        self.ceiling_texture_arrays = pack_textures(self.ceiling_textures)

    def get_wall_texture_arrays(self) -> np.ndarray:
        return self.wall_texture_arrays
    
    def get_texture_map(self) -> np.ndarray:
        return self.texture_map