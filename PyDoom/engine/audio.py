"""Audio manager for handling sounds, music, and 3D audio effects."""

import os
import math
from typing import Dict, List, Optional, TYPE_CHECKING
import pygame

from settings import settings

if TYPE_CHECKING:
    from world.player import Player
    from world.monster import Monster


class AudioManager:
    """Manages all audio playback including music, sound effects, and 3D audio."""
    
    def __init__(self) -> None:
        """Initialize the audio manager and load sounds."""
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(32)
        
        self.master_volume: float = settings.audio.master_volume
        self.music_volume: float = settings.audio.music_volume
        self.sfx_volume: float = settings.audio.sfx_volume
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.footstep_sounds: list = []
        self.monster_sound: Optional[pygame.mixer.Sound] = None
        
        self.monster_channels: Dict[int, pygame.mixer.Channel] = {}
        
        self._load_sounds()
        self._load_music()
        
        self.footstep_timer: float = 0.0
        self.current_footstep_index: int = 0
        
    def _load_sounds(self) -> None:
        """Load all sound effects from the sounds directory."""
        sounds_dir = settings.audio.sounds_directory
        
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
            print(f"Created sounds directory: {sounds_dir}")
            print("Please add sound files:")
            print(f"  - {sounds_dir}/footstep1.wav (or .ogg)")
            print(f"  - {sounds_dir}/footstep2.wav")
            print(f"  - {sounds_dir}/footstep3.wav")
            print(f"  - {sounds_dir}/monster.wav")
            return
        
        for i in range(1, 10):
            loaded = False
            for ext in ['.wav', '.ogg', '.mp3']:
                footstep_path = os.path.join(sounds_dir, f"footstep{i}{ext}")
                if os.path.exists(footstep_path):
                    try:
                        sound = pygame.mixer.Sound(footstep_path)
                        self.footstep_sounds.append(sound)
                        print(f"Loaded footstep sound: {footstep_path}")
                        loaded = True
                        break
                    except Exception as e:
                        print(f"Failed to load {footstep_path}: {e}")
            if loaded:
                continue
        
        monster_sound_loaded = False
        for ext in ['.wav', '.ogg', '.mp3']:
            monster_path = os.path.join(sounds_dir, f"monster{ext}")
            if os.path.exists(monster_path):
                try:
                    self.monster_sound = pygame.mixer.Sound(monster_path)
                    print(f"Loaded monster sound: {monster_path}")
                    monster_sound_loaded = True
                    break
                except Exception as e:
                    print(f"Failed to load {monster_path}: {e}")
        
        if not monster_sound_loaded:
            for i in range(1, 10):
                monster_path = os.path.join(sounds_dir, f"monster{i}.wav")
                if os.path.exists(monster_path):
                    try:
                        self.monster_sound = pygame.mixer.Sound(monster_path)
                        print(f"Loaded monster sound: {monster_path}")
                        monster_sound_loaded = True
                        break
                    except Exception as e:
                        print(f"Failed to load {monster_path}: {e}")
        
        if not self.footstep_sounds:
            print("Warning: No footstep sounds loaded!")
        if not monster_sound_loaded:
            print("Warning: No monster sound loaded!")
    
    def _load_music(self) -> None:
        """Load background music from the music directory."""
        music_dir = settings.audio.music_directory
        
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            print(f"Created music directory: {music_dir}")
            print(f"Please add music file: {music_dir}/background.ogg (or .mp3)")
            return
        
        music_files = [
            "background.ogg", "background.mp3", "background.wav",
            "music.ogg", "music.mp3", "music.wav"
        ]
        
        for music_file in music_files:
            music_path = os.path.join(music_dir, music_file)
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                    print(f"Loaded background music: {music_path}")
                    return
                except Exception as e:
                    print(f"Failed to load {music_path}: {e}")
        
        print("Warning: No background music loaded!")
    
    def play_music(self, loops: int = -1) -> None:
        """Start playing background music.
        
        Args:
            loops: Number of times to loop (-1 for infinite)
        """
        try:
            pygame.mixer.music.play(loops=loops)
        except Exception as e:
            print(f"Failed to play music: {e}")
    
    def stop_music(self) -> None:
        """Stop background music."""
        pygame.mixer.music.stop()
    
    def pause_music(self) -> None:
        """Pause background music."""
        pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Unpause background music."""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def play_footstep(self, is_sprinting: bool = False) -> None:
        """Play a footstep sound effect.
        
        Args:
            is_sprinting: Whether the player is sprinting
        """
        if not self.footstep_sounds:
            return
        
        sound = self.footstep_sounds[self.current_footstep_index]
        self.current_footstep_index = (self.current_footstep_index + 1) % len(self.footstep_sounds)
        
        volume = self.sfx_volume * self.master_volume
        if is_sprinting:
            volume *= 1.2
        volume = min(1.0, volume)
        
        sound.set_volume(volume)
        sound.play()
    
    def update_footsteps(self, dt: float, is_moving: bool, is_sprinting: bool) -> None:
        """Update footstep sound timing.
        
        Args:
            dt: Delta time in seconds
            is_moving: Whether the player is moving
            is_sprinting: Whether the player is sprinting
        """
        if not is_moving:
            self.footstep_timer = 0.0
            return
        
        self.footstep_timer += dt
        
        interval = settings.audio.footstep_sprint_interval if is_sprinting else settings.audio.footstep_interval
        
        if self.footstep_timer >= interval:
            self.play_footstep(is_sprinting)
            self.footstep_timer = 0.0
    
    def start_monster_sound(self, monster_id: int) -> None:
        """Start playing a continuous looping sound for a monster.
        
        Args:
            monster_id: Unique identifier for the monster
        """
        if self.monster_sound is None:
            return
        
        if monster_id not in self.monster_channels:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(self.monster_sound, loops=-1)
                channel.set_volume(0.0)
                self.monster_channels[monster_id] = channel
    
    def stop_monster_sound(self, monster_id: int) -> None:
        """Stop the continuous sound for a monster.
        
        Args:
            monster_id: Unique identifier for the monster
        """
        if monster_id in self.monster_channels:
            self.monster_channels[monster_id].stop()
            del self.monster_channels[monster_id]
    
    def update_monster_sound(self, monster_id: int, distance: float) -> None:
        """Update the volume of a monster's sound based on distance.
        
        Args:
            monster_id: Unique identifier for the monster
            distance: Distance from player to monster
        """
        if self.monster_sound is None:
            return
        
        if monster_id not in self.monster_channels:
            self.start_monster_sound(monster_id)
        
        channel = self.monster_channels.get(monster_id)
        if channel:
            volume = self._calculate_volume_from_distance(distance)
            channel.set_volume(volume)
    
    def update_all_monster_sounds(self, monsters: List['Monster'], player: 'Player') -> None:
        """Update volumes for all monster sounds based on distance.
        
        Args:
            monsters: List of all monsters in the game
            player: The player object
        """
        active_monster_ids = set()
        
        for monster in monsters:
            monster_id = id(monster)
            active_monster_ids.add(monster_id)
            
            distance = monster.get_distance_to_player(player)
            self.update_monster_sound(monster_id, distance)
        
        monsters_to_remove = set(self.monster_channels.keys()) - active_monster_ids
        for monster_id in monsters_to_remove:
            self.stop_monster_sound(monster_id)
    
    def _calculate_volume_from_distance(self, distance: float) -> float:
        """Calculate volume based on distance using inverse square law.
        
        Args:
            distance: Distance from sound source to player
            
        Returns:
            Volume level (0.0 to 1.0)
        """
        if not settings.audio.enable_3d_audio:
            return self.sfx_volume * self.master_volume
        
        if distance <= 0:
            return self.sfx_volume * self.master_volume
        
        max_distance = settings.audio.max_audio_distance
        
        if distance >= max_distance:
            return 0.0
        
        falloff = 1.0 - (distance / max_distance)
        falloff = falloff ** 2
        
        volume = falloff * self.sfx_volume * self.master_volume
        volume = max(settings.audio.monster_sound_min_volume * self.master_volume, volume)
        
        return min(1.0, volume)
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        for channel in self.monster_channels.values():
            channel.stop()
        self.monster_channels.clear()
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
