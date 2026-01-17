"""Audio manager for handling sounds, music, and 3D audio effects."""
"""AI generted code"""

import os
from typing import Dict, List, Optional, TYPE_CHECKING
import pygame

from settings import settings

if TYPE_CHECKING:
    from world.player import Player
    from world.monster import Monster


class AudioManager:
    """Manages all audio playback including music, sound effects, and 3D audio."""
    
    # Audio constants
    SUPPORTED_EXTENSIONS = ('.wav', '.ogg', '.mp3')
    MIXER_FREQ = 44100
    MIXER_SIZE = -16
    MIXER_CHANNELS = 2
    MIXER_BUFFER = 512
    TOTAL_CHANNELS = 32

    def __init__(self) -> None:
        """Initialize the audio manager and load sounds."""
        self._init_mixer()
        
        # Volume Settings
        self.master_volume: float = settings.audio.master_volume
        self.music_volume: float = settings.audio.music_volume
        self.sfx_volume: float = settings.audio.sfx_volume
        
        # Sound Assets
        self.footstep_sounds: List[pygame.mixer.Sound] = []
        self.monster_sound: Optional[pygame.mixer.Sound] = None
        
        # State
        self.monster_channels: Dict[int, pygame.mixer.Channel] = {}
        self.footstep_timer: float = 0.0
        self.current_footstep_index: int = 0
        
        # Load Assets
        self._load_sounds()
        self._load_music()

    def _init_mixer(self) -> None:
        """Safely initializes the pygame mixer."""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(
                    frequency=self.MIXER_FREQ, 
                    size=self.MIXER_SIZE, 
                    channels=self.MIXER_CHANNELS, 
                    buffer=self.MIXER_BUFFER
                )
                pygame.mixer.set_num_channels(self.TOTAL_CHANNELS)
            except pygame.error as e:
                print(f"Warning: Could not initialize audio mixer. {e}")

    # -------------------------------------------------------------------------
    # Resource Loading Helpers
    # -------------------------------------------------------------------------

    def _find_file_with_ext(self, directory: str, base_name: str) -> Optional[str]:
        """Helper to find a file checking multiple audio extensions."""
        for ext in self.SUPPORTED_EXTENSIONS:
            path = os.path.join(directory, f"{base_name}{ext}")
            if os.path.exists(path):
                return path
        return None

    def _load_sounds(self) -> None:
        """Load all sound effects (footsteps, monster) from the sounds directory."""
        sounds_dir = settings.audio.sounds_directory
        
        if not os.path.exists(sounds_dir):
            self._create_missing_dir(sounds_dir, "sounds")
            return

        # 1. Load Footsteps
        for i in range(1, 10):
            path = self._find_file_with_ext(sounds_dir, f"footstep{i}")
            if path:
                try:
                    self.footstep_sounds.append(pygame.mixer.Sound(path))
                except Exception as e:
                    print(f"Failed to load footstep: {path} ({e})")

        # 2. Load Monster Sound (Try 'monster' first, then 'monster1')
        monster_path = self._find_file_with_ext(sounds_dir, "monster")
        
        # Fallback: try numbered monster sound if generic not found
        if not monster_path:
            for i in range(1, 10):
                path = self._find_file_with_ext(sounds_dir, f"monster{i}")
                if path:
                    monster_path = path
                    break
        
        if monster_path:
            try:
                self.monster_sound = pygame.mixer.Sound(monster_path)
                print(f"Loaded monster sound: {monster_path}")
            except Exception as e:
                print(f"Failed to load monster sound: {monster_path} ({e})")

        # Warnings
        if not self.footstep_sounds:
            print("Warning: No footstep sounds loaded!")
        if not self.monster_sound:
            print("Warning: No monster sound loaded!")

    def _load_music(self) -> None:
        """Load background music."""
        music_dir = settings.audio.music_directory
        
        if not os.path.exists(music_dir):
            self._create_missing_dir(music_dir, "music")
            return

        # prioritized list of filenames to look for
        music_candidates = ["background", "music"]
        
        for name in music_candidates:
            path = self._find_file_with_ext(music_dir, name)
            if path:
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                    print(f"Loaded background music: {path}")
                    return
                except Exception as e:
                    print(f"Failed to load music {path}: {e}")

        print("Warning: No background music loaded!")

    def _create_missing_dir(self, path: str, resource_type: str) -> None:
        """Helper to create directory and print setup instructions."""
        try:
            os.makedirs(path)
            print(f"Created {resource_type} directory: {path}")
            print(f"Please add files (e.g., {path}/footstep1.wav, {path}/background.ogg)")
        except OSError as e:
            print(f"Error creating directory {path}: {e}")

    # -------------------------------------------------------------------------
    # Music Control
    # -------------------------------------------------------------------------

    def play_music(self, loops: int = -1) -> None:
        """Start playing background music."""
        if not pygame.mixer.get_init(): return
        try:
            pygame.mixer.music.play(loops=loops)
        except Exception as e:
            print(f"Failed to play music: {e}")

    def stop_music(self) -> None:
        pygame.mixer.music.stop()

    def pause_music(self) -> None:
        pygame.mixer.music.pause()

    def unpause_music(self) -> None:
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    # -------------------------------------------------------------------------
    # SFX Control
    # -------------------------------------------------------------------------

    def play_footstep(self, is_sprinting: bool = False) -> None:
        """Play the next footstep sound in the cycle."""
        if not self.footstep_sounds or not pygame.mixer.get_init():
            return
        
        sound = self.footstep_sounds[self.current_footstep_index]
        
        # Calculate volume
        base_vol = self.sfx_volume * self.master_volume
        volume = base_vol * 1.2 if is_sprinting else base_vol
        sound.set_volume(min(1.0, volume))
        
        sound.play()
        
        # Cycle index
        self.current_footstep_index = (self.current_footstep_index + 1) % len(self.footstep_sounds)

    def update_footsteps(self, dt: float, is_moving: bool, is_sprinting: bool) -> None:
        """Update footstep timer and play sound if interval reached."""
        if not is_moving:
            self.footstep_timer = 0.0
            return

        self.footstep_timer += dt
        interval = (settings.audio.footstep_sprint_interval 
                   if is_sprinting else settings.audio.footstep_interval)

        if self.footstep_timer >= interval:
            self.play_footstep(is_sprinting)
            self.footstep_timer = 0.0

    # -------------------------------------------------------------------------
    # 3D Audio / Monster Sounds
    # -------------------------------------------------------------------------

    def start_monster_sound(self, monster_id: int) -> None:
        """Start playing a continuous looping sound for a monster."""
        if not self.monster_sound or not pygame.mixer.get_init():
            return

        if monster_id not in self.monster_channels:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(self.monster_sound, loops=-1)
                channel.set_volume(0.0)  # Start silent, updated by distance later
                self.monster_channels[monster_id] = channel

    def stop_monster_sound(self, monster_id: int) -> None:
        """Stop the continuous sound for a monster."""
        channel = self.monster_channels.pop(monster_id, None)
        if channel:
            channel.stop()

    def update_monster_sound(self, monster_id: int, distance: float) -> None:
        """Update the volume of a specific monster based on distance."""
        if not self.monster_sound:
            return

        # Ensure sound is playing
        if monster_id not in self.monster_channels:
            self.start_monster_sound(monster_id)

        channel = self.monster_channels.get(monster_id)
        if channel:
            volume = self._calculate_volume_from_distance(distance)
            channel.set_volume(volume)

    def update_all_monster_sounds(self, monsters: List['Monster'], player: 'Player') -> None:
        """Update volumes for all monster sounds and cleanup inactive ones."""
        active_ids = set()

        for monster in monsters:
            m_id = id(monster)
            active_ids.add(m_id)
            dist = monster.get_distance_to_player(player)
            self.update_monster_sound(m_id, dist)

        # Cleanup sounds for monsters that no longer exist or were removed
        current_ids = set(self.monster_channels.keys())
        for m_id in current_ids - active_ids:
            self.stop_monster_sound(m_id)

    def _calculate_volume_from_distance(self, distance: float) -> float:
        """Calculate volume using inverse square law falloff."""
        if not settings.audio.enable_3d_audio:
            return self.sfx_volume * self.master_volume

        max_dist = settings.audio.max_audio_distance
        
        # Immediate cutoff
        if distance >= max_dist:
            return 0.0
        if distance <= 0:
            return self.sfx_volume * self.master_volume

        # Quadratic falloff
        falloff = (1.0 - (distance / max_dist)) ** 2
        
        volume = falloff * self.sfx_volume * self.master_volume
        
        # Apply minimum audible volume floor if configured
        min_vol = settings.audio.monster_sound_min_volume * self.master_volume
        return max(0.0, min(1.0, max(min_vol, volume)))

    def cleanup(self) -> None:
        """Stop all sounds and quit mixer."""
        if not pygame.mixer.get_init():
            return
            
        for channel in self.monster_channels.values():
            channel.stop()
        self.monster_channels.clear()
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()