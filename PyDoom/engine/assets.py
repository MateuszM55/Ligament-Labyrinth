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
        self.floor_texture: Optional[pygame.Surface] = None
        self.ceiling_texture: Optional[pygame.Surface] = None
        
        self.floor_array: Optional[np.ndarray] = None
        self.ceiling_array: Optional[np.ndarray] = None
        
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
        """Generate a simple checkerboard pattern texture.
        
        Args:
            size: Size of the texture (width and height)
            color1: Primary color
            color2: Secondary color
            
        Returns:
            Surface containing the checkerboard pattern
        """
        surface = pygame.Surface((size, size))
        surface.fill(color1)
        pygame.draw.rect(surface, color2, (0, 0, size // 2, size // 2))
        pygame.draw.rect(surface, color2, (size // 2, size // 2, size // 2, size // 2))
        return surface
    
    def _load_textures_from_directory(self) -> None:
        """Load all textures from the texture directory."""
        texture_dir = settings.assets.texture_directory
        
        if not os.path.exists(texture_dir):
            print(f"Warning: Texture directory '{texture_dir}' not found.")
            return
        
        for filename in os.listdir(texture_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                continue
            
            full_path = os.path.join(texture_dir, filename)
            
            match = re.search(r'(\d+)', filename)
            if match:
                try:
                    tex_id = int(match.group(1))
                    self.textures[tex_id] = pygame.image.load(full_path).convert()
                    print(f"Loaded texture {tex_id} from {filename}")
                except pygame.error as e:
                    print(f"Failed to load texture {filename}: {e}")
            
            if "floor" in filename.lower() and self.floor_texture is None:
                try:
                    self.floor_texture = pygame.image.load(full_path).convert()
                    print(f"Loaded floor texture from {filename}")
                except pygame.error as e:
                    print(f"Failed to load floor texture {filename}: {e}")
            
            if "ceiling" in filename.lower() and self.ceiling_texture is None:
                try:
                    self.ceiling_texture = pygame.image.load(full_path).convert()
                    print(f"Loaded ceiling texture from {filename}")
                except pygame.error as e:
                    print(f"Failed to load ceiling texture {filename}: {e}")
    
    def _generate_fallback_textures(self) -> None:
        """Generate fallback textures for any missing wall textures."""
        texture_size = settings.assets.texture_size
        default_colors = settings.assets.default_texture_colors
        
        for tex_id in range(1, 4):
            if tex_id not in self.textures:
                colors = default_colors.get(
                    tex_id,
                    ((150, 150, 150), (100, 100, 100))
                )
                self.textures[tex_id] = self._generate_checkerboard_texture(
                    texture_size,
                    colors[0],
                    colors[1]
                )
                print(f"Generated fallback texture for ID {tex_id}")
    
    def _generate_fallback_floor_ceiling(self) -> None:
        """Generate fallback floor and ceiling textures if not loaded."""
        texture_size = settings.assets.texture_size
        
        if self.floor_texture is None:
            self.floor_texture = self._generate_checkerboard_texture(
                texture_size,
                settings.colors.floor_primary,
                settings.colors.floor_secondary
            )
            print("Generated fallback floor texture")
        
        if self.ceiling_texture is None:
            self.ceiling_texture = self._generate_checkerboard_texture(
                texture_size,
                settings.colors.ceiling_primary,
                settings.colors.ceiling_secondary
            )
            print("Generated fallback ceiling texture")
    
    def _load_all_textures(self) -> None:
        """Load all textures from files and generate fallbacks."""
        self._load_textures_from_directory()
        self._generate_fallback_textures()
        self._generate_fallback_floor_ceiling()
        
        if 1 in self.textures:
            self.tex_width = self.textures[1].get_width()
            self.tex_height = self.textures[1].get_height()
    
    def _convert_textures_to_arrays(self) -> None:
        """Convert floor and ceiling textures to NumPy arrays for fast access."""
        if self.floor_texture is not None:
            self.floor_array = pygame.surfarray.array3d(self.floor_texture)
        
        if self.ceiling_texture is not None:
            self.ceiling_array = pygame.surfarray.array3d(self.ceiling_texture)
        
        self._prepare_wall_texture_arrays()
    
    def get_wall_texture(self, texture_id: int) -> pygame.Surface:
        """Get a wall texture by ID, falling back to texture 1 if not found.
        
        Args:
            texture_id: The texture ID to retrieve
            
        Returns:
            The requested texture surface, or texture 1 as fallback
        """
        return self.textures.get(texture_id, self.textures.get(1))
    
    def get_floor_texture(self) -> pygame.Surface:
        """Get the floor texture surface.
        
        Returns:
            The floor texture surface
        """
        return self.floor_texture
    
    def get_ceiling_texture(self) -> pygame.Surface:
        """Get the ceiling texture surface.
        
        Returns:
            The ceiling texture surface
        """
        return self.ceiling_texture
    
    def get_floor_array(self) -> np.ndarray:
        """Get the floor texture as a NumPy array for fast pixel access.
        
        Returns:
            NumPy array of the floor texture
        """
        return self.floor_array
    
    def get_ceiling_array(self) -> np.ndarray:
        """Get the ceiling texture as a NumPy array for fast pixel access.
        
        Returns:
            NumPy array of the ceiling texture
        """
        return self.ceiling_array
    
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
            texture_array = pygame.surfarray.array3d(texture)
            self.wall_texture_arrays[tex_id] = texture_array
            self.texture_map[tex_id] = tex_id
    
    def get_wall_texture_arrays(self) -> np.ndarray:
        """Get all wall textures as a single NumPy array.
        
        Returns:
            NumPy array of shape (num_textures, tex_width, tex_height, 3)
        """
        return self.wall_texture_arrays
    
    def get_texture_map(self) -> np.ndarray:
        """Get texture mapping array.
        
        Returns:
            NumPy array mapping tile values to texture indices
        """
        return self.texture_map
