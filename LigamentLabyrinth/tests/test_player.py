"""Unit tests for Player class."""

import unittest
import math
from world.player import Player
from world.map import Map


class TestPlayer(unittest.TestCase):
    """Test Player functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(5.0, 5.0, 0.0)
    
    def test_player_initialization(self):
        """Test player is initialized correctly."""
        self.assertEqual(self.player.x, 5.0)
        self.assertEqual(self.player.y, 5.0)
        self.assertEqual(self.player.rotation, 0.0)
    
    def test_rotation_caching(self):
        """Test that rotation caching works."""
        initial_cos = self.player._cos_cache
        initial_sin = self.player._sin_cache
        
        self.player.rotation = 90.0
        self.player._update_trig_cache()
        
        self.assertNotEqual(self.player._cos_cache, initial_cos)
        self.assertNotEqual(self.player._sin_cache, initial_sin)
    
    def test_mouse_rotation(self):
        """Test mouse rotation."""
        initial_rotation = self.player.rotation
        self.player.rotate_from_mouse(10)
        self.assertNotEqual(self.player.rotation, initial_rotation)
    
    def test_bobbing_initialization(self):
        """Test bobbing starts at zero."""
        self.assertEqual(self.player.bob_phase, 0.0)
        self.assertEqual(self.player.bob_offset_y, 0.0)


if __name__ == "__main__":
    unittest.main()
