"""Unit tests for the Map class."""
#AI generated

import unittest
import tempfile
import os
from world.map import Map


class TestMap(unittest.TestCase):
    """Test Map loading and functionality."""
    
    def test_map_dimensions(self):
        """Test that loaded map has valid dimensions."""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("111\n")
            f.write("101\n")
            f.write("111\n")
            temp_map = f.name
        
        try:
            game_map, _, _ = Map.load_from_file(temp_map)
            
            self.assertEqual(game_map.width, 3)
            self.assertEqual(game_map.height, 3)
            self.assertIsNotNone(game_map.grid)
        finally:
            os.unlink(temp_map)
    
    def test_map_has_player_start(self):
        """Test that map has player start position."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("111\n")
            f.write("1P1\n")
            f.write("111\n")
            temp_map = f.name
        
        try:
            game_map, _, _ = Map.load_from_file(temp_map)
            
            self.assertIsNotNone(game_map.player_start)
            self.assertIsInstance(game_map.player_start, tuple)
            self.assertEqual(len(game_map.player_start), 2)
        finally:
            os.unlink(temp_map)


if __name__ == "__main__":
    unittest.main()