"""Unit tests for settings module."""
#AI generated

import unittest
from settings import (
    settings,
    DisplaySettings,
    RenderSettings,
    PlayerSettings,
    MonsterSettings
)


class TestSettings(unittest.TestCase):
    """Test settings configuration."""
    
    def test_display_settings_exists(self):
        """Test that display settings are available."""
        self.assertIsNotNone(settings.display)
        self.assertIsInstance(settings.display.width, int)
        self.assertIsInstance(settings.display.height, int)
        self.assertGreater(settings.display.width, 0)
        self.assertGreater(settings.display.height, 0)
    
    def test_render_settings_exists(self):
        """Test that render settings are available."""
        self.assertIsNotNone(settings.render)
        self.assertIsInstance(settings.render.fov, (int, float))
        self.assertGreater(settings.render.fov, 0)
        self.assertLess(settings.render.fov, 180)
    
    def test_player_settings_exists(self):
        """Test that player settings are available."""
        self.assertIsNotNone(settings.player)
        self.assertIsInstance(settings.player.move_speed, (int, float))
        self.assertGreater(settings.player.move_speed, 0)
    
    def test_settings_immutable(self):
        """Test that settings dataclasses are frozen."""
        with self.assertRaises(Exception):
            settings.display.width = 9999


if __name__ == "__main__":
    unittest.main()
