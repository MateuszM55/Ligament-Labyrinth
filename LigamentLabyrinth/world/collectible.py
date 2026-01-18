"""Collectible entity that player can pick up."""
from world.entity import Entity
from typing import TYPE_CHECKING
from settings import settings

if TYPE_CHECKING:
    from world.player import Player

class Collectible(Entity):
    """Represents a collectible item in the game world."""

    def __init__(self, x: float, y: float, texture_id: int = 11) -> None:
        super().__init__(x, y, texture_id)
        self.collected: bool = False

    def update(self, dt: float, player: 'Player') -> None:
        """Check if player is close enough to collect."""
        if not self.collected:
            dist_sq = self.get_distance_squared_to_player(player)
            threshold_sq = settings.collectible.collection_distance ** 2
            
            if dist_sq < threshold_sq:
                self.collected = True
                self.active = False
