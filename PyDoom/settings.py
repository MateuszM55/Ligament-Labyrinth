"""Configuration and constants for PyDoom raycasting engine."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class DisplaySettings:
    """Display and screen configuration."""
    width: int = 854
    height: int = 480
    fps: int = 144
    title: str = "PyDoom"


@dataclass(frozen=True)
class RenderSettings:
    """Raycasting and rendering configuration."""
    fov: float = 90.0
    max_depth: float = 100.0
    wall_ray_resolution_divisor: int = 1
    floor_and_ceiling_scale: int = 1


@dataclass(frozen=True)
class PlayerSettings:
    """Player movement and physics configuration."""
    move_speed: float = 3.0
    mouse_sensitivity: float = 0.2
    collision_radius: float = 0.2
    
    bob_amplitude: float = 5.0
    bob_frequency: float = 1.0


@dataclass(frozen=True)
class MapSettings:
    """Map and tile configuration."""
    default_map_file: str = "map.txt"


@dataclass(frozen=True)
class AssetSettings:
    """Asset loading configuration."""
    texture_directory: str = "textures"
    texture_size: int = 64
    
    default_texture_colors: dict = None
    
    def __post_init__(self):
        if self.default_texture_colors is None:
            object.__setattr__(self, 'default_texture_colors', {
                1: ((150, 150, 150), (100, 100, 100)),
                2: ((150, 100, 100), (100, 50, 50)),
                3: ((100, 150, 100), (50, 100, 50))
            })


@dataclass(frozen=True)
class ColorPalette:
    """Color constants used throughout the game."""
    black: Tuple[int, int, int] = (0, 0, 0)
    white: Tuple[int, int, int] = (255, 255, 255)
    red: Tuple[int, int, int] = (255, 0, 0)
    green: Tuple[int, int, int] = (0, 255, 0)
    blue: Tuple[int, int, int] = (0, 0, 255)
    
    floor_primary: Tuple[int, int, int] = (80, 80, 80)
    floor_secondary: Tuple[int, int, int] = (60, 60, 60)
    ceiling_primary: Tuple[int, int, int] = (40, 40, 60)
    ceiling_secondary: Tuple[int, int, int] = (30, 30, 50)
    
    minimap_background: Tuple[int, int, int] = (0, 0, 0)
    minimap_wall_default: Tuple[int, int, int] = (100, 100, 100)
    minimap_wall_type2: Tuple[int, int, int] = (100, 50, 50)
    minimap_wall_type3: Tuple[int, int, int] = (50, 100, 50)
    minimap_player: Tuple[int, int, int] = (255, 0, 0)


@dataclass(frozen=True)
class MinimapSettings:
    """Minimap rendering configuration."""
    size: int = 150
    margin: int = 10
    player_dot_radius: int = 3
    direction_line_length: int = 10
    direction_line_width: int = 2


@dataclass(frozen=True)
class LightingSettings:
    """Advanced lighting configuration for horror atmosphere."""
    # Flashlight effect (radial falloff)
    enable_flashlight: bool = True
    flashlight_radius: float = 0.4  # 0.0 = narrow beam, 1.0 = wide beam
    flashlight_intensity: float = 0  # How much darker the edges are (0-1)
    flashlight_sharpness: float = 2.0  # Higher = sharper falloff
    
    # Inverse square law (distance falloff)
    enable_inverse_square: bool = True
    light_intensity: float = 3  # Base light power
    ambient_light: float = 0.03  # Minimum light level (0-1)
    
    # Vignette effect
    enable_vignette: bool = True
    vignette_intensity: float = 1  # 0-1, how dark the edges get
    vignette_radius: float = 0.1  # 0-1, where vignette starts


@dataclass(frozen=True)
class GameSettings:
    """Master settings container."""
    display: DisplaySettings = DisplaySettings()
    render: RenderSettings = RenderSettings()
    player: PlayerSettings = PlayerSettings()
    map: MapSettings = MapSettings()
    assets: AssetSettings = AssetSettings()
    colors: ColorPalette = ColorPalette()
    minimap: MinimapSettings = MinimapSettings()
    lighting: LightingSettings = LightingSettings()
    
    show_fps: bool = True


# Global settings instance
settings = GameSettings()
