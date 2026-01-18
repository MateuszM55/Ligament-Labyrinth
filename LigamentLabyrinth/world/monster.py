"""Monster entity that chases the player."""

import math
from typing import TYPE_CHECKING

from settings import settings
from world.entity import Entity

if TYPE_CHECKING:
    from world.player import Player


class Monster(Entity):
    """Represents a monster/enemy sprite that chases the player."""
    
    def __init__(self, x: float, y: float, texture_id: int = 0) -> None:
        """Initialize the monster.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            texture_id: Texture ID for the sprite
        """
        super().__init__(x, y, texture_id)
        self.speed_multiplier: float = 1.0
        self.triggered_game_over: bool = False
    
    def update(self, dt: float, player: 'Player') -> None:
        """Update monster behavior: move towards player and check collision.
        
        Args:
            dt: Delta time in seconds.
            player: The player instance.
        """
        self.move_towards_player(player, dt)
        
        # Check collision with player
        collision_distance_sq = settings.monster.collision_distance ** 2
        if self.get_distance_squared_to_player(player) < collision_distance_sq:
            self.triggered_game_over = True
    
    def move_towards_player(self, player: 'Player', dt: float) -> None:
        """Move the monster towards the player (ignores walls).
        
        Args:
            player: Player object
            dt: Delta time in seconds
        """
        dx = player.x - self.x
        dy = player.y - self.y
        
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            # Normalize direction and apply speed
            move_speed = settings.monster.move_speed * self.speed_multiplier * dt
            self.x += (dx / distance) * move_speed
            self.y += (dy / distance) * move_speed

