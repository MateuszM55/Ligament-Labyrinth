"""Unit tests for AudioManager."""
#AI generated

import unittest
from unittest.mock import MagicMock, patch
import sys
import types

# Create the mocks outside the class
mock_pygame = types.ModuleType("pygame")
mock_pygame.mixer = MagicMock()
mock_pygame.locals = types.ModuleType("pygame.locals")
mock_pygame.Surface = MagicMock()

class TestAudioManager(unittest.TestCase):
    
    def setUp(self):
        # 1. Start the patcher for sys.modules
        # This replaces pygame ONLY while these tests run, and cleans up automatically.
        self.module_patcher = patch.dict(sys.modules, {
            "pygame": mock_pygame,
            "pygame.mixer": mock_pygame.mixer,
            "pygame.locals": mock_pygame.locals
        })
        self.module_patcher.start()
        
        # Now it is safe to import
        from engine.audio import AudioManager
        from settings import settings

        # 2. Bypass Frozen Settings
        object.__setattr__(settings.audio, 'enable_3d_audio', True)
        object.__setattr__(settings.audio, 'max_audio_distance', 10.0)
        object.__setattr__(settings.audio, 'master_volume', 1.0)
        object.__setattr__(settings.audio, 'sfx_volume', 1.0)
        
        self.audio = AudioManager()
        self.mock_sound = MagicMock()
        self.audio.footstep_sounds = [self.mock_sound, self.mock_sound]
        self.audio.monster_sound = self.mock_sound

    def tearDown(self):
        # Stop the patcher to restore the REAL pygame for other tests
        self.module_patcher.stop()

    def test_play_footstep_cycles_index(self):
        self.audio.current_footstep_index = 0
        self.audio.play_footstep()
        self.assertEqual(self.audio.current_footstep_index, 1)
        self.audio.play_footstep()
        self.assertEqual(self.audio.current_footstep_index, 0)

    def test_3d_audio_volume_falloff(self):
        vol_close = self.audio._calculate_volume_from_distance(0.5)
        vol_med = self.audio._calculate_volume_from_distance(5.0)
        vol_far = self.audio._calculate_volume_from_distance(15.0)
        
        self.assertGreater(vol_close, vol_med)
        self.assertGreater(vol_med, vol_far)
        self.assertEqual(vol_far, 0.0)

    def test_3d_audio_disabled(self):
        from settings import settings
        object.__setattr__(settings.audio, 'enable_3d_audio', False)
        
        vol_close = self.audio._calculate_volume_from_distance(1.0)
        vol_far = self.audio._calculate_volume_from_distance(50.0)
        
        self.assertEqual(vol_close, vol_far)

if __name__ == "__main__":
    unittest.main()