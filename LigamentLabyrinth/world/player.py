"""Player entity with movement, collision, and view bobbing."""

import math
from typing import TYPE_CHECKING

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
        self.is_sprinting: bool = False
        
        radius = settings.player.collision_radius
        self.collision_offsets: list[tuple[float, float]] = [
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
            bob_freq = settings.player.bob_frequency
            if self.is_sprinting:
                bob_freq *= settings.player.sprint_bob_multiplier
            
            self.bob_phase += bob_freq * dt
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
    
    def update(self, dt: float, keys_pressed, game_map: 'Map') -> None:
        """Update player state based on input.
        
        Args:
            dt: Delta time in seconds
            keys_pressed: Dictionary/sequence of pressed keys from pygame
            game_map: The game map for collision detection
        """
        total_dx = 0.0
        total_dy = 0.0
        
        from pygame.locals import K_LSHIFT, K_RSHIFT, K_w, K_s, K_a, K_d
        
        is_sprinting = keys_pressed[K_LSHIFT] or keys_pressed[K_RSHIFT]
        self.is_sprinting = is_sprinting
        
        move_speed = settings.player.move_speed * dt
        if is_sprinting:
            move_speed *= settings.player.sprint_multiplier
        
        if keys_pressed[K_w]:
            total_dx += self._cos_cache * move_speed
            total_dy += self._sin_cache * move_speed
            
        if keys_pressed[K_s]:
            total_dx += -self._cos_cache * move_speed
            total_dy += -self._sin_cache * move_speed
            
        if keys_pressed[K_a]:
            total_dx += self._sin_cache * move_speed
            total_dy += -self._cos_cache * move_speed
            
        if keys_pressed[K_d]:
            total_dx += -self._sin_cache * move_speed
            total_dy += self._cos_cache * move_speed

        self.is_moving = (keys_pressed[K_w] or keys_pressed[K_s] or keys_pressed[K_a] or keys_pressed[K_d])

        if self.is_moving:
            current_speed = math.sqrt(total_dx**2 + total_dy**2)
            if current_speed > move_speed:
                scale = move_speed / current_speed
                total_dx *= scale
                total_dy *= scale

        if total_dx != 0 or total_dy != 0:
            self._move_with_collision(total_dx, total_dy, game_map)
        
        self.update_bobbing(dt)
