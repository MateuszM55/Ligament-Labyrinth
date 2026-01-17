"""Configuration and constants for Ligament Labyrinth raycasting engine."""
from dataclasses import dataclass, field
from typing import Tuple, Dict

@dataclass(frozen=True)
class ColorPalette:
    """Color constants used throughout the game."""
    black: Tuple[int, int, int] = (0, 0, 0)
    white: Tuple[int, int, int] = (255, 255, 255)
    red: Tuple[int, int, int] = (255, 0, 0)
    green: Tuple[int, int, int] = (0, 255, 0)
    blue: Tuple[int, int, int] = (0, 0, 255)
    
    wall_gray: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((150, 150, 150), (100, 100, 100))
    wall_red:  Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((150, 100, 100), (100, 50, 50))
    wall_green: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((100, 150, 100), (50, 100, 50))
    
    floor_primary: Tuple[int, int, int] = (80, 80, 80)
    floor_secondary: Tuple[int, int, int] = (60, 60, 60)
    ceiling_primary: Tuple[int, int, int] = (40, 40, 60)
    ceiling_secondary: Tuple[int, int, int] = (30, 30, 50)
    
    minimap_background: Tuple[int, int, int] = (0, 0, 0)
    minimap_wall_default: Tuple[int, int, int] = (100, 100, 100)
    minimap_player: Tuple[int, int, int] = (255, 0, 0)
    minimap_entity: Tuple[int, int, int] = (255, 100, 100)
    # Mapping of tile id -> minimap color. Use get(tile, minimap_wall_default) when rendering.
    minimap_wall_colors: Dict[int, Tuple[int, int, int]] = field(default_factory=lambda: {
        1: (100, 100, 100),
        2: (100, 50, 50),
        3: (50, 100, 50),
        4: (50, 0, 50),
        5: (122, 0, 5),
    })

palette = ColorPalette()


@dataclass(frozen=True)
class DisplaySettings:
    """Display and screen configuration."""
    width: int = 1280
    height: int = 720
    fps: int = 144
    title: str = "Ligament Labyrinth"


@dataclass(frozen=True)
class RenderSettings:
    """Raycasting and rendering configuration."""
    fov: float = 60.0
    max_depth: float = 100.0
    wall_ray_resolution_divisor: int = 1
    floor_ceiling_ray_resolution_divisor: int = 1
    wall_height_factor: float = 1.0
    sprite_scale: float = 1.0
    glitch_intensity: float = 0.0
    
    glitch_enable_monster_proximity: bool = True
    glitch_monster_start_distance: float = 5.0
    glitch_monster_max_distance: float = 0.0
    glitch_monster_max_intensity: float = 20.0


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
    speed_boost_multiplier: float = 3.0


@dataclass(frozen=True)
class CollectibleSettings:
    """Collectible item configuration."""
    total_count: int = 3
    collection_distance: float = 0.5
    texture_ids: tuple = (15, 15, 15)


@dataclass(frozen=True)
class MapSettings:
    """Map and tile configuration."""
    default_map_file: str = "map.txt"


@dataclass(frozen=True)
class AssetSettings:
    """Asset loading configuration."""
    texture_directory: str = "textures"
    texture_size: int = 512
    
    default_texture_colors: Dict[int, Tuple] = field(default_factory=lambda: {
        1: palette.wall_gray,
        2: palette.wall_red,
        3: palette.wall_green
    })


@dataclass(frozen=True)
class MinimapSettings:
    """Minimap rendering configuration."""
    enabled: bool = True
    size: int = 150
    margin: int = 10
    player_dot_radius: int = 3
    direction_line_length: int = 10
    direction_line_width: int = 2


@dataclass(frozen=True)
class LightingSettings:
    """Advanced lighting configuration."""
    enable_inverse_square: bool = True
    light_intensity: float = 1.0
    ambient_light: float = 0.03
    enable_vignette: bool = True
    vignette_intensity: float = 1.0
    vignette_radius: float = 0.5


@dataclass(frozen=True)
class AudioSettings:
    """Audio and sound configuration."""
    sounds_directory: str = "sounds"
    music_directory: str = "music"
    master_volume: float = 1.0
    music_volume: float = 1.0
    sfx_volume: float = 0.2
    footstep_interval: float = 0.4
    footstep_sprint_interval: float = 0.25
    monster_sound_min_volume: float = 0.05
    max_audio_distance: float = 5.0
    enable_3d_audio: bool = True
    supported_extensions: tuple = ('.wav', '.ogg', '.mp3')
    mixer_freq: int = 44100
    mixer_size: int = -16
    mixer_channels: int = 2
    mixer_buffer: int = 512
    total_channels: int = 32


@dataclass(frozen=True)
class GameSettings:
    """Master settings container."""
    colors: ColorPalette = palette 
    
    display: DisplaySettings = DisplaySettings()
    render: RenderSettings = RenderSettings()
    player: PlayerSettings = PlayerSettings()
    monster: MonsterSettings = MonsterSettings()
    collectible: CollectibleSettings = CollectibleSettings()
    map: MapSettings = MapSettings()
    assets: AssetSettings = AssetSettings()
    minimap: MinimapSettings = MinimapSettings()
    lighting: LightingSettings = LightingSettings()
    audio: AudioSettings = AudioSettings()
    
    show_fps: bool = True

# Global settings instance
settings = GameSettings()