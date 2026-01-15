"""Player entity with movement, collision, and view bobbing."""

import math
from typing import List, Tuple, TYPE_CHECKING

from settings import settings

if TYPE_CHECKING:
    from world.map import Map


class Player:
    """Represents the player with position, rotation, and movement capabilities."""
    
    def __init__(self, x: float, y: float, rotation: float = 0.0) -> None:
        """Initialize the player.
        
        Args:
            x: Initial x position
            y: Initial y position
            rotation: Initial rotation in degrees
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.rotation: float = float(rotation)
        
        self.bob_phase: float = 0.0
        self.bob_offset_y: float = 0.0
        self.is_moving: bool = False
        
        radius = settings.player.collision_radius
        self.collision_offsets: List[Tuple[float, float]] = [
            (radius, 0),
            (-radius, 0),
            (0, radius),
            (0, -radius),
            (radius * 0.707, radius * 0.707),
            (-radius * 0.707, radius * 0.707),
            (radius * 0.707, -radius * 0.707),
            (-radius * 0.707, -radius * 0.707)
        ]
        
        self._cos_cache: float = math.cos(math.radians(rotation))
        self._sin_cache: float = math.sin(math.radians(rotation))
    
    def _check_collision(self, x: float, y: float, game_map: 'Map') -> bool:
        """Check if position collides with walls using multiple points.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            game_map: The game map to check against
            
        Returns:
            True if collision detected, False otherwise
        """
        if game_map.is_wall(x, y):
            return True
        
        for offset_x, offset_y in self.collision_offsets:
            if game_map.is_wall(x + offset_x, y + offset_y):
                return True
        
        return False
    
    def _move_with_collision(self, dx: float, dy: float, game_map: 'Map') -> None:
        """Move player with collision detection and wall sliding.
        
        Args:
            dx: Change in x position
            dy: Change in y position
            game_map: The game map to check collisions against
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        if not self._check_collision(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y
            return

        if not self._check_collision(new_x, self.y, game_map):
            self.x = new_x

        if not self._check_collision(self.x, new_y, game_map):
            self.y = new_y
        
    def set_position(self, x: float, y: float) -> None:
        """Set player position.
        
        Args:
            x: New x position
            y: New y position
        """
        self.x = float(x)
        self.y = float(y)
        
    def set_rotation(self, rotation: float) -> None:
        """Set player rotation.
        
        Args:
            rotation: New rotation in degrees
        """
        self.rotation = float(rotation)
        self._update_trig_cache()
        
    def _update_trig_cache(self) -> None:
        """Cache trigonometric calculations for performance."""
        rad = math.radians(self.rotation)
        self._cos_cache = math.cos(rad)
        self._sin_cache = math.sin(rad)
        
    def rotate(self, degrees: float) -> None:
        """Rotate player by degrees.
        
        Args:
            degrees: Rotation amount in degrees
        """
        self.rotation = (self.rotation + float(degrees)) % 360.0
        self._update_trig_cache()
        
    def rotate_from_mouse(self, dx: float) -> None:
        """Rotate player based on mouse movement.
        
        Args:
            dx: Mouse movement delta
        """
        self.rotate(dx * settings.player.mouse_sensitivity)
            
    def update_bobbing(self, dt: float) -> None:
        """Update view bobbing for walking animation effect.
        
        Args:
            dt: Delta time in seconds
        """
        if self.is_moving:
            self.bob_phase += settings.player.bob_frequency * dt
            if self.bob_phase > 2 * math.pi * 100:
                self.bob_phase = 0
            
            self.bob_offset_y = (
                math.sin(self.bob_phase * 2 * math.pi) * 
                settings.player.bob_amplitude
            )
        else:
            if abs(self.bob_offset_y) > 0.1:
                self.bob_offset_y *= 0.8
            else:
                self.bob_offset_y = 0.0
                self.bob_phase = 0.0
