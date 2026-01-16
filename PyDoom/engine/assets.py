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
    
    def _ensure_power_of_two_size(self, surface: pygame.Surface, target_size: int) -> pygame.Surface:
        """Ensure texture is power-of-2 size for optimal Numba performance.
        
        Args:
            surface: Original surface
            target_size: Target power-of-2 size (e.g., 64, 128, 256)
            
        Returns:
            Resized surface if needed, otherwise original surface
        """
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
        
        for filename in os.listdir(texture_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                continue
            
            full_path = os.path.join(texture_dir, filename)
            
            if "sprite" in filename.lower():
                match = re.search(r'(\d+)', filename)
                if match:
                    try:
                        sprite_id = int(match.group(1))
                        # Immediate format conversion for faster NumPy conversion later
                        sprite_surface = pygame.image.load(full_path).convert_alpha()
                        sprite_surface = self._ensure_power_of_two_size(sprite_surface, texture_size)
                        self.sprite_textures[sprite_id] = sprite_surface
                        print(f"Loaded sprite texture {sprite_id} from {filename}")
                    except pygame.error as e:
                        print(f"Failed to load sprite texture {filename}: {e}")
            elif "floor" in filename.lower():
                match = re.search(r'(\d+)', filename)
                if match:
                    try:
                        floor_id = int(match.group(1))
                        # Immediate format conversion for faster NumPy conversion
                        floor_surface = pygame.image.load(full_path).convert()
                        floor_surface = self._ensure_power_of_two_size(floor_surface, texture_size)
                        self.floor_textures[floor_id] = pygame.surfarray.array3d(floor_surface)
                        print(f"Loaded floor texture {floor_id} from {filename}")
                    except pygame.error as e:
                        print(f"Failed to load floor texture {filename}: {e}")
            elif "ceiling" in filename.lower():
                match = re.search(r'(\d+)', filename)
                if match:
                    try:
                        ceiling_id = int(match.group(1))
                        # Immediate format conversion for faster NumPy conversion
                        ceiling_surface = pygame.image.load(full_path).convert()
                        ceiling_surface = self._ensure_power_of_two_size(ceiling_surface, texture_size)
                        self.ceiling_textures[ceiling_id] = pygame.surfarray.array3d(ceiling_surface)
                        print(f"Loaded ceiling texture {ceiling_id} from {filename}")
                    except pygame.error as e:
                        print(f"Failed to load ceiling texture {filename}: {e}")
            else:
                match = re.search(r'(\d+)', filename)
                if match:
                    try:
                        tex_id = int(match.group(1))
                        # Immediate format conversion for faster NumPy conversion
                        wall_surface = pygame.image.load(full_path).convert()
                        wall_surface = self._ensure_power_of_two_size(wall_surface, texture_size)
                        self.textures[tex_id] = wall_surface
                        print(f"Loaded texture {tex_id} from {filename}")
                    except pygame.error as e:
                        print(f"Failed to load texture {filename}: {e}")
    
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
        
        if 0 not in self.floor_textures:
            floor_surface = self._generate_checkerboard_texture(
                texture_size,
                settings.colors.floor_primary,
                settings.colors.floor_secondary
            )
            self.floor_textures[0] = pygame.surfarray.array3d(floor_surface)
            print("Generated fallback floor texture (ID 0)")
        
        if 0 not in self.ceiling_textures:
            ceiling_surface = self._generate_checkerboard_texture(
                texture_size,
                settings.colors.ceiling_primary,
                settings.colors.ceiling_secondary
            )
            self.ceiling_textures[0] = pygame.surfarray.array3d(ceiling_surface)
            print("Generated fallback ceiling texture (ID 0)")
        
        # Generate additional fallback textures for different IDs
        floor_colors = [
            ((80, 80, 80), (60, 60, 60)),    # ID 0 (default gray)
            ((100, 70, 50), (80, 50, 30)),   # ID 1 (brown/wood)
            ((60, 80, 60), (40, 60, 40)),    # ID 2 (green/grass)
            ((70, 70, 90), (50, 50, 70)),    # ID 3 (blue/stone)
            ((90, 70, 60), (70, 50, 40)),    # ID 4 (red/brick)
            ((110, 90, 70), (90, 70, 50))    # ID 5 (tan/sand)
        ]
        
        ceiling_colors = [
            ((40, 40, 60), (30, 30, 50)),    # ID 0 (default dark blue)
            ((60, 50, 40), (40, 30, 20)),    # ID 1 (brown/wood)
            ((50, 70, 50), (30, 50, 30)),    # ID 2 (green)
            ((80, 80, 100), (60, 60, 80)),   # ID 3 (light stone)
            ((80, 60, 50), (60, 40, 30)),    # ID 4 (red/brick)
            ((100, 90, 80), (80, 70, 60))    # ID 5 (tan/sand)
        ]
        
        for i in range(1, 6):
            if i not in self.floor_textures:
                floor_surface = self._generate_checkerboard_texture(
                    texture_size,
                    floor_colors[i][0],
                    floor_colors[i][1]
                )
                self.floor_textures[i] = pygame.surfarray.array3d(floor_surface)
                print(f"Generated fallback floor texture (ID {i})")
            
            if i not in self.ceiling_textures:
                ceiling_surface = self._generate_checkerboard_texture(
                    texture_size,
                    ceiling_colors[i][0],
                    ceiling_colors[i][1]
                )
                self.ceiling_textures[i] = pygame.surfarray.array3d(ceiling_surface)
                print(f"Generated fallback ceiling texture (ID {i})")
    
    def _load_all_textures(self) -> None:
        """Load all textures from files and generate fallbacks."""
        self._load_textures_from_directory()
        self._generate_fallback_textures()
        self._generate_fallback_floor_ceiling()
        self._generate_fallback_sprites()
        
        if 1 in self.textures:
            self.tex_width = self.textures[1].get_width()
            self.tex_height = self.textures[1].get_height()
    
    def _generate_fallback_sprites(self) -> None:
        """Generate fallback sprite textures if not loaded."""
        """AI generated code"""
        texture_size = settings.assets.texture_size
        
        if 0 not in self.sprite_textures:
            sprite_surface = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
            sprite_surface.fill((0, 0, 0, 0))
            
            pygame.draw.circle(
                sprite_surface,
                (255, 50, 50),
                (texture_size // 2, texture_size // 2 - texture_size // 8),
                texture_size // 8
            )
            
            pygame.draw.circle(
                sprite_surface,
                (255, 50, 50),
                (texture_size // 2, texture_size // 2 + texture_size // 8),
                texture_size // 4
            )
            
            pygame.draw.circle(
                sprite_surface,
                (0, 0, 0),
                (texture_size // 2 - texture_size // 8, texture_size // 2 - texture_size // 8),
                texture_size // 16
            )
            
            pygame.draw.circle(
                sprite_surface,
                (0, 0, 0),
                (texture_size // 2 + texture_size // 8, texture_size // 2 - texture_size // 8),
                texture_size // 16
            )
            
            self.sprite_textures[0] = sprite_surface
            print("Generated fallback sprite texture")
            self.tex_width = self.textures[1].get_width()
            self.tex_height = self.textures[1].get_height()
    
    def _convert_textures_to_arrays(self) -> None:
        """Convert wall textures to NumPy arrays for fast access."""
        self._prepare_wall_texture_arrays()
        self._prepare_floor_ceiling_arrays()
    
    def get_floor_arrays(self) -> np.ndarray:
        """Get all floor textures as a NumPy array.
        
        Returns:
            NumPy array of shape (num_textures, tex_width, tex_height, 3)
        """
        return self.floor_texture_arrays
    
    def get_ceiling_arrays(self) -> np.ndarray:
        """Get all ceiling textures as a NumPy array.
        
        Returns:
            NumPy array of shape (num_textures, tex_width, tex_height, 3)
        """
        return self.ceiling_texture_arrays
    
    def get_sprite_texture(self, sprite_id: int) -> Optional[pygame.Surface]:
        """Get a sprite texture by ID.
        
        Args:
            sprite_id: The sprite texture ID
            
        Returns:
            Sprite surface or None if not found
        """
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
            texture_array = pygame.surfarray.array3d(texture)
            self.wall_texture_arrays[tex_id] = texture_array
            self.texture_map[tex_id] = tex_id
    
    def _prepare_floor_ceiling_arrays(self) -> None:
        """Prepare floor and ceiling textures as NumPy arrays for numba optimization."""
        if not self.floor_textures:
            self.floor_texture_arrays = np.zeros((1, self.tex_width, self.tex_height, 3), dtype=np.uint8)
        else:
            max_floor_id = max(self.floor_textures.keys())
            num_floor_textures = max_floor_id + 1
            
            # Get the actual size of the first floor texture
            first_texture = next(iter(self.floor_textures.values()))
            floor_tex_width = first_texture.shape[0]
            floor_tex_height = first_texture.shape[1]
            
            self.floor_texture_arrays = np.zeros(
                (num_floor_textures, floor_tex_width, floor_tex_height, 3),
                dtype=np.uint8
            )
            
            for tex_id, texture_array in self.floor_textures.items():
                self.floor_texture_arrays[tex_id] = texture_array
        
        if not self.ceiling_textures:
            self.ceiling_texture_arrays = np.zeros((1, self.tex_width, self.tex_height, 3), dtype=np.uint8)
        else:
            max_ceiling_id = max(self.ceiling_textures.keys())
            num_ceiling_textures = max_ceiling_id + 1
            
            # Get the actual size of the first ceiling texture
            first_texture = next(iter(self.ceiling_textures.values()))
            ceiling_tex_width = first_texture.shape[0]
            ceiling_tex_height = first_texture.shape[1]
            
            self.ceiling_texture_arrays = np.zeros(
                (num_ceiling_textures, ceiling_tex_width, ceiling_tex_height, 3),
                dtype=np.uint8
            )
            
            for tex_id, texture_array in self.ceiling_textures.items():
                self.ceiling_texture_arrays[tex_id] = texture_array
    
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
