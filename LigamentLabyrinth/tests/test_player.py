"""Unit tests for Player class."""
#AI generated

import unittest
import math
import sys
import types
from unittest.mock import MagicMock, patch

# --- SETUP MOCKS ---
mock_pg = types.ModuleType("pygame")
mock_pg.locals = types.ModuleType("pygame.locals")
mock_pg.Surface = MagicMock()

# Define small manageable constants for our test
mock_pg.locals.K_w = 100
mock_pg.locals.K_s = 101
mock_pg.locals.K_a = 102
mock_pg.locals.K_d = 103
mock_pg.locals.K_LSHIFT = 200
mock_pg.locals.K_RSHIFT = 201

class MockMap:
    def __init__(self, walls=None):
        self.width = 10
        self.height = 10
        self.walls = walls or set() 
    def is_wall(self, x: float, y: float) -> bool:
        return (int(x), int(y)) in self.walls

class TestPlayer(unittest.TestCase):
    
    def setUp(self):
        # 1. Patch sys.modules safely
        self.module_patcher = patch.dict(sys.modules, {
            "pygame": mock_pg,
            "pygame.locals": mock_pg.locals
        })
        self.module_patcher.start()
        
        from world.player import Player
        self.player = Player(5.0, 5.0, 0.0)

    def tearDown(self):
        self.module_patcher.stop()
    
    def test_movement_no_walls(self):
        empty_map = MockMap()
        initial_x = self.player.x
        
        # FIX: Use a MagicMock instead of a list. 
        # accessing mock_keys[ANYTHING] returns 0 (False) by default.
        mock_keys = MagicMock()
        mock_keys.__getitem__.return_value = 0 
        
        # When we ask for 'W', return 1 (True)
        def key_side_effect(k):
            return 1 if k == mock_pg.locals.K_w else 0
        
        mock_keys.__getitem__.side_effect = key_side_effect
        
        self.player.update(0.1, mock_keys, empty_map)
        self.assertGreater(self.player.x, initial_x)

    def test_movement_collision(self):
        wall_map = MockMap(walls={(6, 5)})
        
        # Mock pressing 'W'
        mock_keys = MagicMock()
        mock_keys.__getitem__.side_effect = lambda k: 1 if k == mock_pg.locals.K_w else 0
        
        # Move in small steps
        for _ in range(10):
            self.player.update(0.1, mock_keys, wall_map)
        
        self.assertLess(self.player.x, 6.0)

    def test_rotation_logic(self):
        self.player.rotation = 0.0
        
        # Simulate mouse movement
        self.player.rotate_from_mouse(100)
        
        # 1. Check that rotation changed
        self.assertNotEqual(self.player.rotation, 0.0)
        
        # 2. Check consistency (Degrees -> Radians -> Cosine)
        # We don't care about the specific sensitivity value, just that the cache matches the angle.
        rads = math.radians(self.player.rotation)
        expected_cos = math.cos(rads)
        
        self.assertAlmostEqual(self.player._cos_cache, expected_cos, places=5)

if __name__ == "__main__":
    unittest.main()