"""Configuration and constants for PyDoom raycasting engine."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class DisplaySettings:
    """Display and screen configuration."""
    width: int = 1280
    height: int = 720
    fps: int = 144
    title: str = "PyDoom"


@dataclass(frozen=True)
class RenderSettings:
    """Raycasting and rendering configuration."""
    fov: float = 60.0
    max_depth: float = 100.0
    wall_ray_resolution_divisor: int = 1
    floor_ceiling_ray_resolution_divisor: int = 1
    wall_height_factor: float = 1.0
    sprite_scale: float = 1.0
    glitch_intensity: float = 0.0  # LSD Glitch effect intensity (0=off, higher values=more intense color banding)
    
    # Monster proximity glitch effect settings
    glitch_enable_monster_proximity: bool = True  # Enable dynamic glitch based on monster distance
    glitch_monster_start_distance: float = 5.0  # Distance where glitch starts to appear
    glitch_monster_max_distance: float = 0.0  # Distance where glitch is at maximum intensity
    glitch_monster_max_intensity: float = 20.0  # Maximum glitch intensity when monster is very close (2.0+ for dramatic effect)


@dataclass(frozen=True)
class PlayerSettings:
    """Player movement and physics configuration."""
    move_speed: float = 3.0
    mouse_sensitivity: float = 0.2
    collision_radius: float = 0.2
    
    bob_amplitude: float = 5.0
    bob_frequency: float = 1.0
    
    sprint_multiplier: float = 1.5
    sprint_bob_multiplier: float = 2.0


@dataclass(frozen=True)
class MonsterSettings:
    """Monster/enemy configuration."""
    move_speed: float = 1.5
    collision_distance: float = 0.3
    speed_boost_multiplier: float = 3.0  # Speed multiplier when all collectibles are obtained


@dataclass(frozen=True)
class CollectibleSettings:
    """Collectible item configuration."""
    total_count: int = 3
    collection_distance: float = 0.5
    texture_ids: tuple = (1,2,3)  # Texture IDs for each collectible (use different sprites)


@dataclass(frozen=True)
class MapSettings:
    """Map and tile configuration."""
    default_map_file: str = "map.txt"


@dataclass(frozen=True)
class AssetSettings:
    """Asset loading configuration."""
    texture_directory: str = "textures"
    texture_size: int = 128
    
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
    # Inverse square law (distance falloff)
    enable_inverse_square: bool = True
    light_intensity: float = 1  # Base light power that emits from the player
    ambient_light: float = 0.03  # Minimum light level everywhere (0-1)
    
    # Vignette effect (darkens screen edges for tunnel vision/horror effect)
    enable_vignette: bool = True
    vignette_intensity: float = 1  # 0-1, multiplier for edge darkening (0=no effect, 1=maximum darkness at edges)
    vignette_radius: float = 0.5  # Size of the clear center 'circle' (0 = whole screen is dark, 1 = effect only visible at edges)


@dataclass(frozen=True)
class AudioSettings:
    """Audio and sound configuration."""
    sounds_directory: str = "sounds"
    music_directory: str = "music"
    
    # Volume levels (0.0 to 1.0)
    master_volume: float = 1.0
    music_volume: float = 1
    sfx_volume: float = 0.2
    
    # Footstep settings
    footstep_interval: float = 0.4  # Time between footstep sounds in seconds (walking)
    footstep_sprint_interval: float = 0.25  # Time between footstep sounds when sprinting
    
    # Monster sound settings
    monster_sound_min_volume: float = 0.05  # Minimum volume for monster sounds
    
    # 3D Audio settings
    max_audio_distance: float = 5.0  # Maximum distance for sound 
    enable_3d_audio: bool = True  # Enable distance-based volume scaling


@dataclass(frozen=True)
class GameSettings:
    """Master settings container."""
    display: DisplaySettings = DisplaySettings()
    render: RenderSettings = RenderSettings()
    player: PlayerSettings = PlayerSettings()
    monster: MonsterSettings = MonsterSettings()
    collectible: CollectibleSettings = CollectibleSettings()
    map: MapSettings = MapSettings()
    assets: AssetSettings = AssetSettings()
    colors: ColorPalette = ColorPalette()
    minimap: MinimapSettings = MinimapSettings()
    lighting: LightingSettings = LightingSettings()
    audio: AudioSettings = AudioSettings()
    
    show_fps: bool = True


# Global settings instance
settings = GameSettings()
