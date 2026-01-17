"""Smoke test - verify the game can be imported and initialized without crashing."""
#AI generated

import unittest
import sys
import os

# Add parent directory to path so we can import game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSmokeTest(unittest.TestCase):
    """Smoke tests to verify basic imports work."""
    
    def test_import_main(self):
        """Test that main module can be imported."""
        try:
            import main
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import main: {e}")
    
    def test_import_settings(self):
        """Test that settings module can be imported."""
        try:
            import settings
            self.assertIsNotNone(settings.settings)
        except Exception as e:
            self.fail(f"Failed to import settings: {e}")
    
    def test_import_engine_modules(self):
        """Test that engine modules can be imported."""
        try:
            from engine import raycaster, assets, audio
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import engine modules: {e}")
    
    def test_import_world_modules(self):
        """Test that world modules can be imported."""
        try:
            from world import player, map, monster, collectible
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import world modules: {e}")
    
    def test_pygame_available(self):
        """Test that pygame is installed and can be imported."""
        try:
            import pygame
            self.assertTrue(True)
        except ImportError:
            self.fail("pygame is not installed")
    
    def test_numpy_available(self):
        """Test that numpy is installed and can be imported."""
        try:
            import numpy
            self.assertTrue(True)
        except ImportError:
            self.fail("numpy is not installed")
    
    def test_numba_available(self):
        """Test that numba is installed and can be imported."""
        try:
            import numba
            self.assertTrue(True)
        except ImportError:
            self.fail("numba is not installed")


if __name__ == "__main__":
    unittest.main()
