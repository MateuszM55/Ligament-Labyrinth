"""Unit tests for AudioManager."""

import unittest
from unittest.mock import MagicMock
import sys
import types

# --- 1. ROBUST MOCKING SETUP ---
# We must mock pygame AND pygame.locals so imports in other files don't crash.
mock_pygame = types.ModuleType("pygame")
mock_pygame.mixer = MagicMock()
mock_pygame.locals = types.ModuleType("pygame.locals") 

# Inject these fakes into Python's system modules
sys.modules["pygame"] = mock_pygame
sys.modules["pygame.mixer"] = mock_pygame.mixer
sys.modules["pygame.locals"] = mock_pygame.locals

# Now we can safely import game modules
from engine.audio import AudioManager
from settings import settings

class TestAudioManager(unittest.TestCase):
    
    def setUp(self):
        # --- 2. BYPASS FROZEN DATACLASS ---
        # We use object.__setattr__ to modify the frozen settings specifically for testing.
        object.__setattr__(settings.audio, 'enable_3d_audio', True)
        object.__setattr__(settings.audio, 'max_audio_distance', 10.0)
        object.__setattr__(settings.audio, 'master_volume', 1.0)
        object.__setattr__(settings.audio, 'sfx_volume', 1.0)
        
        self.audio = AudioManager()
        
        # Mock sound objects so we don't need real .wav files
        self.mock_sound = MagicMock()
        self.audio.footstep_sounds = [self.mock_sound, self.mock_sound]
        self.audio.monster_sound = self.mock_sound

    def test_play_footstep_cycles_index(self):
        self.audio.current_footstep_index = 0
        self.audio.play_footstep()
        self.assertEqual(self.audio.current_footstep_index, 1)
        self.audio.play_footstep()
        self.assertEqual(self.audio.current_footstep_index, 0)

    def test_3d_audio_volume_falloff(self):
        """Test that volume gets quieter as distance increases."""
        # Close (0.5m)
        vol_close = self.audio._calculate_volume_from_distance(0.5)
        # Medium (5.0m)
        vol_med = self.audio._calculate_volume_from_distance(5.0)
        # Far (15.0m) - beyond max distance of 10.0
        vol_far = self.audio._calculate_volume_from_distance(15.0)
        
        self.assertGreater(vol_close, vol_med)
        self.assertGreater(vol_med, vol_far)
        self.assertEqual(vol_far, 0.0)

    def test_3d_audio_disabled(self):
        """Test volume is constant if 3D audio is off."""
        # Disable 3D audio
        object.__setattr__(settings.audio, 'enable_3d_audio', False)
        
        vol_close = self.audio._calculate_volume_from_distance(1.0)
        vol_far = self.audio._calculate_volume_from_distance(50.0)
        
        self.assertEqual(vol_close, vol_far)

if __name__ == "__main__":
    unittest.main()