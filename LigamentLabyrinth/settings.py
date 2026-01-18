"""Configuration and constants for Ligament Labyrinth raycasting engine."""
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Tuple, Dict

def get_config_path():
    """
    Returns the absolute path to config.json.
    - EXE Mode: Returns path next to LigamentLabyrinth.exe (User Editable)
    - DEV Mode: Returns path next to main.py
    """
    if getattr(sys, 'frozen', False):
        # sys.executable is the full path to the .exe file
        application_path = os.path.dirname(sys.executable)
    else:
        # Standard python script execution
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(application_path, 'config.json')

def load_user_config():
    """Loads external JSON config and returns a dict."""
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                print(f"Loading config from: {path}")
                return json.load(f)
        except Exception as e:
            print(f"Error loading config.json: {e}. Using defaults.")
    else:
        print(f"Config file not found at {path}. Using defaults.")
    return {}

USER_CONFIG = load_user_config()

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
    
    floor_fallback_primary: Tuple[int, int, int] = (80, 80, 80)
    floor_fallback_secondary: Tuple[int, int, int] = (60, 60, 60)
    ceiling_fallback_primary: Tuple[int, int, int] = (40, 40, 60)
    ceiling_fallback_secondary: Tuple[int, int, int] = (30, 30, 50)
    
    minimap_background: Tuple[int, int, int] = (0, 0, 0)
    minimap_wall_default: Tuple[int, int, int] = (100, 100, 100)
    minimap_player: Tuple[int, int, int] = (255, 0, 0)
    minimap_entity: Tuple[int, int, int] = (255, 100, 100)
    
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
    width: int = USER_CONFIG.get('display', {}).get('width', 1280)
    height: int = USER_CONFIG.get('display', {}).get('height', 720)
    fps: int = USER_CONFIG.get('display', {}).get('fps', 144)
    title: str = "Ligament Labyrinth"

@dataclass(frozen=True)
class RenderSettings:
    """Raycasting and rendering configuration."""
    fov: float = USER_CONFIG.get('render', {}).get('fov', 60.0)
    max_depth: float = 100.0
    
    wall_ray_resolution_divisor: int = USER_CONFIG.get('render', {}).get('wall_ray_resolution_divisor', 1)
    floor_ceiling_ray_resolution_divisor: int = USER_CONFIG.get('render', {}).get('floor_ceiling_ray_resolution_divisor', 1)
    wall_height_factor: float = USER_CONFIG.get('render', {}).get('wall_height_factor', 1.0)
    
    sprite_scale: float = 1.0
    glitch_intensity: float = 0.0
    
    glitch_enable_monster_proximity: bool = USER_CONFIG.get('render', {}).get('glitch_enable_monster_proximity', True)
    glitch_monster_start_distance: float = USER_CONFIG.get('render', {}).get('glitch_monster_start_distance', 5.0)
    glitch_monster_max_distance: float = USER_CONFIG.get('render', {}).get('glitch_monster_max_distance', 0.0)
    glitch_monster_max_intensity: float = USER_CONFIG.get('render', {}).get('glitch_monster_max_intensity', 20.0)

@dataclass(frozen=True)
class PlayerSettings:
    """Player movement and physics configuration."""
    move_speed: float = USER_CONFIG.get('player', {}).get('move_speed', 3.0)
    mouse_sensitivity: float = USER_CONFIG.get('player', {}).get('mouse_sensitivity', 0.2)
    sprint_multiplier: float = USER_CONFIG.get('player', {}).get('sprint_multiplier', 1.5)
    
    collision_radius: float = 0.2
    bob_amplitude: float = 5.0
    bob_frequency: float = 1.0
    sprint_bob_multiplier: float = 2.0

@dataclass(frozen=True)
class MonsterSettings:
    """Monster/enemy configuration."""
    move_speed: float = USER_CONFIG.get('monster', {}).get('move_speed', 1.5)
    collision_distance: float = 0.3
    speed_boost_multiplier: float = 3.0

@dataclass(frozen=True)
class CollectibleSettings:
    """Collectible item configuration."""
    count_to_win: int = 4
    collection_distance: float = 0.5
    texture_ids: tuple = (15,)

@dataclass(frozen=True)
class MapSettings:
    """Map and tile configuration."""
    default_map_file: str = "mapData/map.txt"

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
    enabled: bool = USER_CONFIG.get('minimap', {}).get('enabled', True)
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
    
    enable_vignette: bool = USER_CONFIG.get('lighting', {}).get('enable_vignette', True)
    vignette_intensity: float = 1.0
    vignette_radius: float = 0.5

@dataclass(frozen=True)
class AudioSettings:
    """Audio and sound configuration."""
    sounds_directory: str = "sounds"
    music_directory: str = "music"
    
    master_volume: float = USER_CONFIG.get('audio', {}).get('master_volume', 1.0)
    music_volume: float = USER_CONFIG.get('audio', {}).get('music_volume', 1.0)
    sfx_volume: float = USER_CONFIG.get('audio', {}).get('sfx_volume', 0.2)
    
    enable_3d_audio: bool = True
    footstep_interval: float = 0.4
    footstep_sprint_interval: float = 0.25
    monster_sound_min_volume: float = 0.05
    max_audio_distance: float = 5.0
    
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
    
    show_fps: bool = USER_CONFIG.get('display', {}).get('show_fps', True)

# Global settings instance
settings = GameSettings()